#!/usr/bin/env python3
"""SVG render gate hook.

Fires after any file write from the agent. If the written file is an .svg,
the hook:
  1. Parses the XML to verify it is well-formed.
  2. Scans for corrupted byte ranges (control chars 0x00-0x1F except tab /
     newline / carriage return, and Windows-1252 garbage 0x80-0x9F).
  3. Renders a sibling .png via rsvg-convert so the agent can visually
     verify the result.
  4. Writes a JSON report at <svg>.render-report.json.
  5. Returns a compact summary to the agent as additional_context.

The hook is NON-BLOCKING. It never refuses a write. It reports facts and
lets the skill decide whether to advance to the next phase.

For non-SVG files, the hook exits 0 with no output (cheap no-op).

Protocol reference: Cursor hooks exchange JSON over stdin/stdout. See
~/.cursor/skills/build-agent-architecture-svg/references/phased-construction.md
for the report schema and usage.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

REPORT_SUFFIX = ".render-report.json"
PNG_SUFFIX = ".png"

ALLOWED_CONTROL_CODES = {0x09, 0x0A, 0x0D}
MAX_BAD_BYTE_SAMPLES = 20


def _emit(report: dict[str, Any]) -> None:
    """Write Cursor hook response to stdout and exit 0."""
    summary_lines = [
        f"SVG render gate: status={report['status']}",
        f"  svg: {report['svg_path']}",
        f"  png: {report.get('png_path') or '(not rendered)'}",
    ]

    if report["status"] != "OK":
        msgs = report.get("messages") or []
        for m in msgs[:5]:
            summary_lines.append(f"  - {m}")

    context = "\n".join(summary_lines)
    context += (
        "\n  Full report: "
        + report["svg_path"]
        + REPORT_SUFFIX
    )

    response = {"additional_context": context}
    sys.stdout.write(json.dumps(response))
    sys.exit(0)


def _write_report(report_path: Path, report: dict[str, Any]) -> None:
    try:
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    except OSError:
        pass


def _scan_bad_bytes(svg_bytes: bytes) -> list[dict[str, Any]]:
    """Identify content problems that should not appear in a clean SVG.

    Detection proceeds in two stages so we do not flag legitimate UTF-8
    multi-byte characters (which contain continuation bytes in 0x80-0xBF):

    1. Attempt strict UTF-8 decoding. If it fails, report the first byte
       position that breaks decoding — this catches classic Windows-1252
       paste corruption (e.g. a standalone 0x92 right-single-quote).

    2. If UTF-8 is valid, scan code points for XML-forbidden control
       characters (U+0000..U+001F except TAB/LF/CR, and C1 controls
       U+0080..U+009F). These are legal UTF-8 but illegal in XML 1.0 and
       usually indicate garbage text that would render as a replacement
       glyph.
    """
    try:
        decoded = svg_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail_at = exc.start
        byte_val = svg_bytes[fail_at] if fail_at < len(svg_bytes) else 0
        return [{
            "offset": fail_at,
            "byte": f"0x{byte_val:02X}",
            "reason": f"invalid UTF-8 sequence: {exc.reason}",
            "position": "byte",
        }]

    bad: list[dict[str, Any]] = []
    for char_index, ch in enumerate(decoded):
        code = ord(ch)
        if code < 0x20 and code not in ALLOWED_CONTROL_CODES:
            bad.append({
                "offset": char_index,
                "byte": f"U+{code:04X}",
                "reason": "XML-forbidden C0 control character",
                "position": "char",
            })
        elif 0x80 <= code <= 0x9F:
            bad.append({
                "offset": char_index,
                "byte": f"U+{code:04X}",
                "reason": "C1 control character (often Windows-1252 paste corruption)",
                "position": "char",
            })
        if len(bad) >= MAX_BAD_BYTE_SAMPLES:
            break
    return bad


def _extract_viewbox(svg_path: Path) -> dict[str, float] | None:
    try:
        tree = ET.parse(svg_path)
    except ET.ParseError:
        return None
    root = tree.getroot()
    viewbox = root.get("viewBox")
    if not viewbox:
        return None
    parts = viewbox.split()
    if len(parts) != 4:
        return None
    try:
        _, _, w, h = (float(p) for p in parts)
    except ValueError:
        return None
    return {"width": w, "height": h}


def _render_png(svg_path: Path, png_path: Path) -> tuple[bool, str]:
    if shutil.which("rsvg-convert") is None:
        return False, "rsvg-convert not found on PATH"

    try:
        result = subprocess.run(
            ["rsvg-convert", "-o", str(png_path), str(svg_path)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, "rsvg-convert timed out after 10s"
    except OSError as exc:
        return False, f"rsvg-convert invocation failed: {exc}"

    if result.returncode != 0:
        stderr = (result.stderr or "").strip().splitlines()
        tail = stderr[-1] if stderr else f"exit code {result.returncode}"
        return False, f"rsvg-convert failed: {tail}"

    return True, "ok"


def _build_report(svg_path: Path) -> dict[str, Any]:
    report: dict[str, Any] = {
        "status": "OK",
        "svg_path": str(svg_path),
        "png_path": None,
        "xml_ok": False,
        "bad_bytes": [],
        "render_ok": False,
        "viewbox": None,
        "file_size_bytes": None,
        "messages": [],
    }

    try:
        svg_bytes = svg_path.read_bytes()
    except OSError as exc:
        report["status"] = "XML_ERROR"
        report["messages"].append(f"could not read svg file: {exc}")
        return report

    report["file_size_bytes"] = len(svg_bytes)

    bad_bytes = _scan_bad_bytes(svg_bytes)
    if bad_bytes:
        report["status"] = "BAD_BYTES"
        report["bad_bytes"] = bad_bytes
        report["messages"].append(
            f"{len(bad_bytes)} corrupted byte(s) found "
            f"(showing first {MAX_BAD_BYTE_SAMPLES})"
        )
        report["messages"].append(
            "Replace with UTF-8 glyphs such as → — · ✓ ✗ before re-checking XML."
        )
        return report

    try:
        ET.fromstring(svg_bytes)
        report["xml_ok"] = True
    except ET.ParseError as exc:
        report["status"] = "XML_ERROR"
        report["messages"].append(f"XML parse error: {exc}")
        return report

    viewbox = _extract_viewbox(svg_path)
    if viewbox is not None:
        report["viewbox"] = viewbox

    png_path = svg_path.with_suffix(svg_path.suffix + PNG_SUFFIX)
    render_ok, render_msg = _render_png(svg_path, png_path)
    report["render_ok"] = render_ok
    if render_ok:
        report["png_path"] = str(png_path)
    else:
        report["messages"].append(render_msg)
        if report["status"] == "OK":
            report["status"] = "RENDER_FAILED"

    return report


def _read_stdin() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _extract_file_path(event: dict[str, Any]) -> str | None:
    """Cursor afterFileEdit payload varies slightly; probe common fields."""
    for key in ("file_path", "filePath", "path"):
        val = event.get(key)
        if isinstance(val, str) and val:
            return val

    tool_input = event.get("tool_input") or event.get("toolInput") or {}
    if isinstance(tool_input, dict):
        for key in ("file_path", "filePath", "path", "target_file"):
            val = tool_input.get(key)
            if isinstance(val, str) and val:
                return val

    tool_output = event.get("tool_output") or event.get("toolOutput") or {}
    if isinstance(tool_output, dict):
        for key in ("file_path", "filePath", "path"):
            val = tool_output.get(key)
            if isinstance(val, str) and val:
                return val

    return None


def main() -> None:
    event = _read_stdin()
    file_path = _extract_file_path(event)

    if not file_path or not file_path.lower().endswith(".svg"):
        sys.exit(0)

    svg_path = Path(file_path).resolve()
    if not svg_path.exists():
        report = {
            "status": "XML_ERROR",
            "svg_path": str(svg_path),
            "messages": ["file does not exist after write"],
        }
        _write_report(
            Path(str(svg_path) + REPORT_SUFFIX),
            report,
        )
        _emit(report)
        return

    report = _build_report(svg_path)
    _write_report(Path(str(svg_path) + REPORT_SUFFIX), report)
    _emit(report)


if __name__ == "__main__":
    main()

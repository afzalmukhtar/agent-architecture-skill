# svg-render-gate — Cursor hook

Companion hook for the **agent-architecture-skill**. It enforces the
Phase 0 → Phase 4 render gates automatically: every time the agent writes
an `.svg` file, this hook validates it and gives the agent back a concrete
report so the next phase only begins once the current one is clean.

## What it does

On every `afterFileEdit` event with `matcher: Write`:

1. **Ignores non-SVG writes** — non-`.svg` files short-circuit with no output.
2. **UTF-8 decode** — catches Windows-1252 paste corruption (stray `0x92`,
   `0x96`, etc.) at the first broken byte.
3. **XML parse** — uses `xml.etree.ElementTree` to confirm the file is
   well-formed XML.
4. **Control-character scan** — rejects XML-forbidden C0 controls
   (U+0000–U+001F except TAB/LF/CR) and C1 controls (U+0080–U+009F) that
   survive UTF-8 decoding.
5. **PNG render** — shells out to `rsvg-convert` to produce
   `<file>.svg.png` so the agent (and you) can visually verify the result.
6. **JSON report** — writes `<file>.svg.render-report.json` with the full
   outcome (viewBox, file size, error messages, rendered dimensions).
7. **Agent summary** — returns a one-screen summary via Cursor's
   `additional_context` channel so the agent sees the result inline.

The hook is **non-blocking**. It never refuses a write. It reports facts
and lets the skill's Phase 0 → Phase 4 workflow decide whether to advance.

## Report schema

```json
{
  "status": "OK" | "XML_ERROR" | "BAD_BYTES" | "RENDER_FAILED",
  "svg_path": "/abs/path/file.svg",
  "png_path": "/abs/path/file.svg.png",
  "viewbox": "0 0 1440 1760",
  "file_size_bytes": 24817,
  "messages": ["..."]
}
```

| Status | Meaning |
|---|---|
| `OK` | XML parsed, no bad bytes, PNG rendered successfully. |
| `BAD_BYTES` | Invalid UTF-8 sequence or XML-forbidden control char detected. First offender is reported with byte offset. |
| `XML_ERROR` | File is UTF-8 clean but XML is malformed (missing tag close, bad attribute, etc.). |
| `RENDER_FAILED` | XML is valid but `rsvg-convert` errored out (unclosed path, invalid gradient, etc.). |

## Installation

### 1. Install the script into your Cursor hooks directory

```bash
mkdir -p ~/.cursor/hooks/svg-render-gate
cp hooks/svg-render-gate/validate.py ~/.cursor/hooks/svg-render-gate/
chmod +x ~/.cursor/hooks/svg-render-gate/validate.py
```

Or symlink it so repo updates propagate automatically:

```bash
mkdir -p ~/.cursor/hooks
ln -s "$PWD/hooks/svg-render-gate" ~/.cursor/hooks/svg-render-gate
```

### 2. Register the hook in `~/.cursor/hooks.json`

Merge the snippet from [`hooks.json.example`](./hooks.json.example) into
your existing `~/.cursor/hooks.json`. If the file does not exist yet,
copy it verbatim:

```bash
cp hooks/svg-render-gate/hooks.json.example ~/.cursor/hooks.json
```

If you already have other hooks registered, splice this entry into the
`afterFileEdit` array instead of overwriting the file.

### 3. Install `rsvg-convert`

The PNG render step uses `rsvg-convert` (from `librsvg`). Install once:

```bash
# macOS
brew install librsvg

# Debian / Ubuntu
sudo apt install librsvg2-bin

# Fedora
sudo dnf install librsvg2-tools
```

If `rsvg-convert` is absent the hook still runs — it just reports
`RENDER_FAILED` with a clear message. XML validation and byte scanning
always execute.

### 4. Add the sidecar artifacts to `.gitignore`

The hook writes `<file>.svg.png` and `<file>.svg.render-report.json`
beside every SVG it touches. In any project that authors SVGs, add:

```gitignore
# SVG render gate hook artifacts
*.svg.png
*.svg.render-report.json
```

## Verifying the install

```bash
echo '{"file_path":"/tmp/nope.txt"}' | ~/.cursor/hooks/svg-render-gate/validate.py
# → exits 0 silently (non-SVG short-circuit)

cat > /tmp/good.svg <<'EOF'
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect x="10" y="10" width="80" height="80" fill="#333"/>
</svg>
EOF
echo "{\"file_path\":\"/tmp/good.svg\"}" | ~/.cursor/hooks/svg-render-gate/validate.py
# → emits additional_context JSON with status=OK
# → writes /tmp/good.svg.png and /tmp/good.svg.render-report.json
```

## Why this hook exists

The parent skill (`build-agent-architecture-svg`) enforces a **phased**
construction workflow (Plan → Scaffold → Fill → Connect → Polish) with
mandatory render gates between phases. Running the validator by hand after
every edit is easy to skip. This hook makes the render gate automatic,
consistent, and impossible to forget, which is the whole point of using
Cursor hooks for enforcement rather than prose instructions.

See [`../../references/phased-construction.md`](../../references/phased-construction.md)
for how the render gate fits into each phase.

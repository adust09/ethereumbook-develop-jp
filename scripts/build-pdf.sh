#!/usr/bin/env bash
# Build the Japanese translation of Mastering Ethereum (2nd edition) as an A4 PDF.
#
# Usage:
#   ./scripts/build-pdf.sh
#   PDF_OUT=/tmp/book.pdf ./scripts/build-pdf.sh
#
# Requirements:
#   - mdBook 0.4.36 (downloaded automatically if missing)
#   - Chrome or Chromium
#   - Node.js + npm (for puppeteer-core; used only to drive Chrome)
#   - Noto CJK fonts (fonts-noto-cjk on Debian/Ubuntu)
#
# Optional env:
#   CHROME          path to Chrome / Chromium
#   PDF_OUT         output path (default: <repo>/pdf/mastering-ethereum-2nd-ja.pdf)
#   PDF_BUILD_DIR   mdBook output directory (default: <repo>/book)
#   MDBOOK_BIN      path to an existing mdbook binary
#   MDBOOK_VERSION  default: 0.4.36
#   SKIP_MDBOOK     if set to 1, reuse PDF_BUILD_DIR without rebuilding

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MDBOOK_VERSION="${MDBOOK_VERSION:-0.4.36}"
OUT="${PDF_OUT:-$ROOT/pdf/mastering-ethereum-2nd-ja.pdf}"
BUILD_DIR="${PDF_BUILD_DIR:-$ROOT/book}"
CACHE="${XDG_CACHE_HOME:-$HOME/.cache}/ethereumbook-pdf"
CSS_SRC="$ROOT/scripts/print-pdf.css"
PRINT_JS="$ROOT/scripts/print-to-pdf.js"

log() { printf '==> %s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

# --- mdBook -----------------------------------------------------------------

install_mdbook() {
  local dest="$CACHE/mdbook-${MDBOOK_VERSION}"
  if [[ -x "$dest/mdbook" ]]; then
    printf '%s/mdbook' "$dest"
    return 0
  fi

  need_cmd curl
  need_cmd tar
  local arch asset url tmp
  case "$(uname -m)" in
    x86_64)        asset="mdbook-v${MDBOOK_VERSION}-x86_64-unknown-linux-gnu.tar.gz" ;;
    aarch64|arm64) asset="mdbook-v${MDBOOK_VERSION}-aarch64-unknown-linux-gnu.tar.gz" ;;
    *) die "unsupported architecture: $(uname -m)" ;;
  esac
  url="https://github.com/rust-lang/mdBook/releases/download/v${MDBOOK_VERSION}/${asset}"
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN
  log "downloading mdBook v${MDBOOK_VERSION} ($asset)"
  curl -fsSL -o "$tmp/$asset" "$url"
  mkdir -p "$dest"
  tar -xzf "$tmp/$asset" -C "$dest"
  [[ -x "$dest/mdbook" ]] || die "mdbook binary missing after extract"
  printf '%s/mdbook' "$dest"
}

resolve_mdbook() {
  if [[ -n "${MDBOOK_BIN:-}" ]]; then
    [[ -x "$MDBOOK_BIN" ]] || die "MDBOOK_BIN is not executable: $MDBOOK_BIN"
    printf '%s' "$MDBOOK_BIN"
    return 0
  fi
  if command -v mdbook >/dev/null 2>&1; then
    local ver
    ver="$(mdbook --version | awk '{print $2}')"
    if [[ "$ver" == "$MDBOOK_VERSION" ]]; then
      command -v mdbook
      return 0
    fi
    log "found mdbook $ver, but $MDBOOK_VERSION is required; downloading"
  fi
  install_mdbook
}

# --- Chrome / fonts / node --------------------------------------------------

resolve_chrome() {
  if [[ -n "${CHROME:-}" ]]; then
    [[ -x "$CHROME" ]] || die "CHROME is not executable: $CHROME"
    printf '%s' "$CHROME"
    return 0
  fi
  local cand
  for cand in \
      google-chrome-stable \
      google-chrome \
      chromium-browser \
      chromium \
      chrome \
      /usr/bin/google-chrome-stable \
      /usr/bin/google-chrome \
      /usr/bin/chromium-browser \
      /usr/bin/chromium; do
    if command -v "$cand" >/dev/null 2>&1; then
      command -v "$cand"
      return 0
    fi
    if [[ -x "$cand" ]]; then
      printf '%s' "$cand"
      return 0
    fi
  done
  die "Chrome or Chromium not found. Install Google Chrome / Chromium, or set CHROME=."
}

ensure_fonts() {
  if command -v fc-list >/dev/null 2>&1 && fc-list :lang=ja family | grep -qi 'Noto Sans CJK'; then
    return 0
  fi
  if [[ -n "${GITHUB_ACTIONS:-}" ]] && command -v apt-get >/dev/null 2>&1; then
    log "installing fonts-noto-cjk"
    sudo apt-get update -y
    sudo apt-get install -y fonts-noto-cjk
    return 0
  fi
  die "Noto CJK fonts not found. On Debian/Ubuntu: sudo apt-get install fonts-noto-cjk"
}

ensure_puppeteer() {
  need_cmd node
  need_cmd npm
  if [[ -d "$CACHE/npm/node_modules/puppeteer-core" ]]; then
    return 0
  fi
  log "installing puppeteer-core into $CACHE/npm"
  mkdir -p "$CACHE/npm"
  (
    cd "$CACHE/npm"
    if [[ ! -f package.json ]]; then
      npm init -y >/dev/null 2>&1
    fi
    npm install --no-fund --no-audit puppeteer-core
  )
}

# --- HTML prep --------------------------------------------------------------

prepare_print_html() {
  local book_dir="$1"
  local src="$book_dir/print.html"
  local dst="$book_dir/print-pdf.html"
  [[ -f "$src" ]] || die "mdBook print page missing: $src (is output.html.print enabled?)"
  [[ -f "$CSS_SRC" ]] || die "missing $CSS_SRC"
  cp -f "$CSS_SRC" "$book_dir/print-pdf.css"
  python3 - "$src" "$dst" << 'PY'
import sys
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
html = src.read_text(encoding="utf-8")
if "print-pdf.css" not in html:
    html = html.replace("</head>", '<link rel="stylesheet" href="print-pdf.css">\n</head>', 1)
html = html.replace(
    '<html lang="ja" class="light"',
    '<html lang="ja" class="light" data-pdf="1"',
    1,
)
html = html.replace(
    'var default_theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "navy" : "light";',
    'var default_theme = "light";',
)
html = html.replace(
    "html.classList.add(theme);",
    'html.classList.add("light"); theme = "light";',
)
dst.write_text(html, encoding="utf-8")
PY
}

free_port() {
  python3 - << 'PY'
import socket
s = socket.socket()
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()
PY
}

# --- main -------------------------------------------------------------------

need_cmd python3
[[ -f "$ROOT/book.toml" ]] || die "book.toml not found in $ROOT"
[[ -f "$CSS_SRC" ]] || die "missing $CSS_SRC"
[[ -f "$PRINT_JS" ]] || die "missing $PRINT_JS"

MDBOOK="$(resolve_mdbook)"
CHROME_BIN="$(resolve_chrome)"
ensure_fonts
ensure_puppeteer

if [[ "${SKIP_MDBOOK:-0}" != "1" ]]; then
  log "building mdBook with $($MDBOOK --version)"
  (cd "$ROOT" && "$MDBOOK" build -d "$BUILD_DIR")
else
  log "skipping mdBook build; using $BUILD_DIR"
fi

prepare_print_html "$BUILD_DIR"
[[ -f "$BUILD_DIR/print-pdf.html" ]] || die "failed to write print-pdf.html"

mkdir -p "$(dirname "$OUT")"
OUT="$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$OUT")"

PORT="$(free_port)"
log "serving $BUILD_DIR at http://127.0.0.1:${PORT}"
python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$BUILD_DIR" >/dev/null 2>&1 &
SERVER_PID=$!
cleanup() { kill "$SERVER_PID" >/dev/null 2>&1 || true; }
trap cleanup EXIT

# wait until the print page is reachable
for _ in $(seq 1 50); do
  if curl -fsS "http://127.0.0.1:${PORT}/print-pdf.html" >/dev/null 2>&1; then
    break
  fi
  sleep 0.1
done
curl -fsS "http://127.0.0.1:${PORT}/print-pdf.html" >/dev/null \
  || die "local HTTP server did not become ready"

log "rendering PDF with $CHROME_BIN"
NODE_PATH="$CACHE/npm/node_modules" \
  PDF_URL="http://127.0.0.1:${PORT}/print-pdf.html" \
  PDF_OUT="$OUT" \
  CHROME="$CHROME_BIN" \
  node "$PRINT_JS"

[[ -s "$OUT" ]] || die "PDF was not created: $OUT"
log "done: $OUT ($(python3 -c 'import os,sys; n=os.path.getsize(sys.argv[1]); print(f"{n/1024/1024:.1f} MiB")' "$OUT"))"

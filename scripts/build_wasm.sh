#!/usr/bin/env bash
# AMDE Interactive Demos: WASM Build Pipeline (PRD-29 / MIN-90)
# Zero-server reproducible build script.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CRATE_DIR="${ROOT_DIR}/crate"
PKG_DIR="${ROOT_DIR}/demo/pkg"

echo "=== [1/4] Checking Rust & WASM Target ==="
export PATH="$HOME/.cargo/bin:$PATH"
if ! command -v cargo >/dev/null 2>&1; then
    echo "ERROR: cargo not found in PATH or ~/.cargo/bin"
    exit 1
fi

echo "Rustc: $(rustc --version)"
echo "Cargo: $(cargo --version)"

echo "=== [2/4] Building WASM binary (release) ==="
cd "${CRATE_DIR}"
cargo build --target wasm32-unknown-unknown --release

WASM_SRC="${CRATE_DIR}/target/wasm32-unknown-unknown/release/amde_demo_wasm.wasm"
if [ ! -f "${WASM_SRC}" ]; then
    echo "ERROR: Target WASM not found at ${WASM_SRC}"
    exit 1
fi

WASM_SIZE=$(wc -c < "${WASM_SRC}" | tr -d ' ')
echo "Compiled WASM: ${WASM_SRC} (${WASM_SIZE} bytes)"

echo "=== [3/4] Copying to Demo Package ==="
mkdir -p "${PKG_DIR}"
cp -f "${WASM_SRC}" "${PKG_DIR}/amde_demo_wasm.wasm"

echo "=== [4/4] Generating Zero-Server Base64 JS Loader ==="
python3 "${SCRIPT_DIR}/generate_loader.py"

echo "=== WASM Pipeline Build Complete! ==="

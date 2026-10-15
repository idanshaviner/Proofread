#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Keep caches writable in restricted cloud workspaces without changing HOME.
cache_root="$PWD/.build/caches"
export CLANG_MODULE_CACHE_PATH="$cache_root/clang"
export SWIFTPM_MODULECACHE_OVERRIDE="$cache_root/modules"
exec "${SWIFT_BIN:-swift}" test \
  --cache-path "$cache_root/swiftpm" \
  --config-path "$cache_root/config" \
  --security-path "$cache_root/security" \
  -j 4 "$@"

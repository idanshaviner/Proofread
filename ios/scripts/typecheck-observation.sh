#!/usr/bin/env bash
# Compile the real Observation macro path without linking Apple's UI or Linux
# Observation runtime. This is a compiler regression check, not an iOS build.
set -euo pipefail
cd "$(dirname "$0")/.."
swift_driver="$(command -v "${SWIFT_BIN:-swift}")"
swift_compiler="${SWIFTC_BIN:-$(dirname "$swift_driver")/swiftc}"
module_cache="$PWD/.build/caches/observation"
mkdir -p "$module_cache"
"$swift_compiler" -typecheck -D PROOFREAD_OBSERVATION_TYPECHECK \
  -module-cache-path "$module_cache" \
  Proofread/Models/ComposerModel.swift Proofread/Models/ResponseModels.swift \
  Proofread/Services/ReplyClient.swift
printf '%s\n' 'Observation compiler regression check passed (not an iOS build).'

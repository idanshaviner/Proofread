#!/usr/bin/env bash
# Unsigned simulator build plus shared tests; no deployment or paid inference.
set -euo pipefail
if [[ "$(uname -s)" != Darwin ]]; then
  echo "Native validation requires macOS with Xcode; no build was run." >&2
  exit 1
fi
for tool in xcodebuild xcrun xcodegen swift; do
  if ! command -v "$tool" >/dev/null; then
    echo "Missing prerequisite: $tool. See ios/README.md." >&2
    exit 1
  fi
done
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir/.."
xcodebuild -version
xcrun --sdk iphonesimulator --show-sdk-version
xcodegen generate
xcodebuild -project Proofread.xcodeproj -scheme Proofread \
  -configuration Debug -sdk iphonesimulator \
  -destination 'generic/platform=iOS Simulator' \
  -derivedDataPath .build/xcode CODE_SIGNING_ALLOWED=NO build
bash scripts/test-networking.sh
printf '%s\n' 'Unsigned simulator build and shared tests passed.' \
  'Interactive simulator generate/rewrite/copy acceptance remains a separate check.'

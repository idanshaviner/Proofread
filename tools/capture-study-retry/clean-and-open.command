#!/bin/bash
# Local Mac helper: preserve signing/source, archive generated builds, compile.
set -euo pipefail
helper_dir="$(cd "$(dirname "$0")" && pwd)"
project_root="${1:-$HOME/Documents/Proofread-Capture-Study}"
if [[ "$(uname -s)" != Darwin ]]; then
  echo 'Run this helper on the Mac with Xcode.' >&2
  exit 1
fi
study_dir="$project_root/ios/CaptureStudy"
xcode_project="$study_dir/ProofreadCaptureStudy.xcodeproj"
controller="$project_root/ios/Proofread/Views/ScreenCaptureStudyController.swift"
if [[ ! -f "$controller" || ! -d "$xcode_project" || -L "$controller" ]]; then
  echo 'Expected existing capture-study source and Xcode project were not found. Nothing changed.' >&2
  exit 1
fi
current_hash="$(shasum -a 256 "$controller" | awk '{print $1}')"
case "$current_hash" in
  b09ea54dce626914ab4796b89c6786dc068d6a3f89a44bac1af8f3493901d4c9|0414e1816e205e6d18cffdd8ce4a00226d579abb18440cd88d20cc907c3cdffb) ;;
  *) echo 'Source has unexpected edits. Nothing changed; keep it and report this message.' >&2; exit 1 ;;
esac
# Bundles include the source; repository use reads the authoritative source file.
supplied_source="$helper_dir/ScreenCaptureStudyController.swift"
if [[ ! -f "$supplied_source" ]]; then
  supplied_source="$helper_dir/../../ios/Proofread/Views/ScreenCaptureStudyController.swift"
fi
# All helpers/provided sources must be present before moving generated output.
if [[ ! -f "$supplied_source" ]]; then
  echo 'Extract the complete helper ZIP first. Nothing changed.' >&2
  exit 1
fi
supplied_hash="$(shasum -a 256 "$supplied_source" | awk '{print $1}')"
if [[ "$supplied_hash" != 0414e1816e205e6d18cffdd8ce4a00226d579abb18440cd88d20cc907c3cdffb ]]; then
  echo 'Supplied source does not match this helper. Nothing changed.' >&2
  exit 1
fi
for generated in "$project_root/ios/.build" "$study_dir/.build" "$study_dir/build"; do
  if [[ -L "$generated" ]]; then
    echo 'A generated directory is a symbolic link; nothing changed.' >&2
    exit 1
  fi
done
backup_dir="$(mktemp -d "$project_root/.capture-retry-backup.XXXXXX")"
cp -p "$controller" "$backup_dir/ScreenCaptureStudyController.swift"
cp "$supplied_source" "$controller"
index=0
for generated in "$project_root/ios/.build" "$study_dir/.build" "$study_dir/build"; do
  index=$((index + 1))
  if [[ -e "$generated" ]]; then mv "$generated" "$backup_dir/generated-$index"; fi
done
printf 'Source/build backup: %s\n' "$backup_dir"
# No xcodegen: retain the user's project, bundle ID and Personal Team settings.
xcodebuild -project "$xcode_project" -scheme ProofreadCaptureStudy \
  -configuration Debug -sdk iphoneos -destination 'generic/platform=iOS' \
  -derivedDataPath "$study_dir/.build/clean-retry" CODE_SIGNING_ALLOWED=NO \
  clean build 2>&1 | tee "$backup_dir/build.log"
open "$xcode_project"
printf '%s\n' 'Compile check passed. In Xcode select your iPhone and press Command-R to install/run with your saved signing settings.'

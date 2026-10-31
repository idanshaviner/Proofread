#!/usr/bin/env bash
# Read-only SDK inspection. No recording, entitlements, builds or private data.
set -euo pipefail
if [[ "$(uname -s)" != Darwin ]]; then
  echo 'Run this read-only inspection on the Mac with Xcode installed.' >&2
  exit 1
fi
xcodebuild -version
capture_sdk="$(xcrun --sdk iphoneos --show-sdk-path)"
xcrun --sdk iphoneos --show-sdk-version
for header in \
  ReplayKit.framework/Headers/RPBroadcastSampleHandler.h \
  ReplayKit.framework/Headers/RPSystemBroadcastPickerView.h \
  ScreenCaptureKit.framework/Headers/SCContentSharingPicker.h \
  ScreenCaptureKit.framework/Headers/SCStream.h; do
  capture_header="$capture_sdk/System/Library/Frameworks/$header"
  printf '\n%s\n' "$header"
  if [[ -f "$capture_header" ]]; then
    # Read only availability and relevant API declarations, never user files.
    grep -nE 'API_AVAILABLE|API_UNAVAILABLE|API_DEPRECATED|NS_SWIFT_UNAVAILABLE|@interface|@protocol|presentPicker|present|processSampleBuffer|startCapture|stopCapture' "$capture_header" || true
  else
    echo 'Not present in this SDK.'
  fi
done
printf '\n%s\n' 'SDK inspection only. Device behavior and App Review acceptance remain untested.'

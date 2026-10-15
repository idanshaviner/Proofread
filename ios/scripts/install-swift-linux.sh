#!/usr/bin/env bash
set -euo pipefail

# Pinned official toolchain, tested on this Debian 13 x86_64 cloud machine.
# This installs no services and never writes to the user's home directory.
. /etc/os-release
if [[ "$ID" != debian || ! "$VERSION_ID" =~ ^(12|13)$ || "$(uname -m)" != x86_64 ]]; then
  echo "This helper supports Debian 12/13 x86_64 only. Install Swift from swift.org for other platforms." >&2
  exit 1
fi
for required_command in curl gpg tar sha256sum; do
  command -v "$required_command" >/dev/null
done

toolchain_parent="${PROOFREAD_SWIFT_TOOLCHAIN_ROOT:-/workspace/toolchains}"
download_cache="${PROOFREAD_SWIFT_DOWNLOAD_CACHE:-/workspace/.cache/proofread-swift-toolchain}"
release="swift-6.1.3-RELEASE-debian12"
toolchain="$toolchain_parent/$release"
archive="$download_cache/proofread-swift.tar.gz"
signature="$download_cache/proofread-swift.tar.gz.sig"
keys="$download_cache/proofread-swift-keys.asc"
release_url="https://download.swift.org/swift-6.1.3-release/debian12/swift-6.1.3-RELEASE/$release.tar.gz"
expected_fingerprint="52BB7E3DE28A71BE22EC05FFEF80A866B47A981F"
mkdir -p "$download_cache" "$toolchain_parent"

download() {
  local url="$1" destination="$2"
  if [[ ! -f "$destination" ]]; then
    curl --fail --location --max-time 600 "$url" --output "$destination.part"
    mv "$destination.part" "$destination"
  fi
}
download "$release_url" "$archive"
download "$release_url.sig" "$signature"
# The Swift project's own website repository also publishes its official keys.
download "https://raw.githubusercontent.com/swiftlang/swift-org-website/main/keys/all-keys.asc" "$keys"

verification_dir="$(mktemp -d)"
trap 'rm -rf "$verification_dir"' EXIT
chmod 700 "$verification_dir"
gpg --homedir "$verification_dir" --batch --import "$keys" >&2
gpg --homedir "$verification_dir" --batch --status-fd 1 --verify "$signature" "$archive" > "$verification_dir/status"
awk -v expected="$expected_fingerprint" '
  $1 == "[GNUPG:]" && $2 == "VALIDSIG" && $3 == expected { valid = 1 }
  END { exit !valid }
' "$verification_dir/status"

archive_digest="$(sha256sum "$archive" | cut -d ' ' -f 1)"
marker="$toolchain/.proofread-verified-archive"
if [[ ! -f "$marker" || "$(cat "$marker")" != "$archive_digest" || ! -x "$toolchain/usr/bin/swift" ]]; then
  tar -xzf "$archive" -C "$toolchain_parent"
  printf '%s\n' "$archive_digest" > "$marker"
fi
"$toolchain/usr/bin/swift" --version
printf 'Swift executable: %s/usr/bin/swift\n' "$toolchain"

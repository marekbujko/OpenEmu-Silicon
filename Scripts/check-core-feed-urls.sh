#!/usr/bin/env bash
# check-core-feed-urls.sh — Guardrail against regressing the core update channel.
#
# Fails if any tracked Info.plist still references the dormant upstream
# OpenEmu-Update appcast host, and fails if a core's SUFeedURL points at an
# Appcasts/<name>.xml file that doesn't exist in the working tree.
#
# Wired into Scripts/verify.sh as a precondition for --core runs. Cheap to run
# everywhere else too.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

fail=0

PLISTS=$(git ls-files '*.plist' | grep -v -E '(^|/)archived/')

# 1. No upstream URLs anywhere in tracked plists.
upstream_hits=$(echo "$PLISTS" \
  | xargs grep -l -E 'OpenEmu-Update|raw\.github\.com/OpenEmu|appcast\.openemu\.org' 2>/dev/null \
  || true)

if [ -n "$upstream_hits" ]; then
  echo "ERROR: upstream OpenEmu-Update/openemu.org SUFeedURL still present in:" >&2
  echo "$upstream_hits" >&2
  echo "Replace with https://raw.githubusercontent.com/nickybmon/OpenEmu-Silicon/main/Appcasts/<core>.xml" >&2
  fail=1
fi

# 2. Every nickybmon SUFeedURL must resolve to an Appcasts/<name>.xml in the tree.
missing=()
while IFS= read -r hit; do
  [ -z "$hit" ] && continue
  plist="${hit%%:*}"
  appcast_name=$(echo "$hit" | sed -E 's#.*/Appcasts/([^"<]+)\.xml.*#\1#')
  if [ ! -f "Appcasts/${appcast_name}.xml" ]; then
    missing+=("$plist → Appcasts/${appcast_name}.xml")
  fi
done < <(echo "$PLISTS" \
  | xargs grep -H -E 'raw\.githubusercontent\.com/nickybmon/OpenEmu-Silicon/main/Appcasts/' 2>/dev/null \
  || true)

if [ ${#missing[@]} -gt 0 ]; then
  echo "ERROR: SUFeedURL points at appcast files that don't exist in the tree:" >&2
  for m in "${missing[@]}"; do
    echo "  $m" >&2
  done
  fail=1
fi

if [ $fail -ne 0 ]; then
  exit 1
fi

echo "OK: no upstream OpenEmu-Update references; all core SUFeedURLs resolve."

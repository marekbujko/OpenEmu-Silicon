#!/usr/bin/env python3
# update_core_appcast.py — Prepend a new release entry to a per-core appcast
#
# Usage:
#   python3 Scripts/update_core_appcast.py <appcast.xml> <core_name> <version> \
#       <download_url> <length> [--sign-zip <path/to/core.zip>]
#
# Arguments:
#   appcast.xml    Path to the core's appcast file (e.g. Appcasts/flycast.xml)
#   core_name      Display name of the core (e.g. Flycast)
#   version        Version string — also used as sparkle:version (e.g. 2.5)
#   download_url   Full URL to the .oecoreplugin.zip on GitHub Releases
#   length         Byte size of the zip file (overridden when --sign-zip parses one)
#
# Options:
#   --sign-zip <path>   Run Sparkle's sign_update against the local zip and embed
#                       sparkle:edSignature on the new <enclosure>. The host app's
#                       Sparkle keypair (already in keychain for the host appcast)
#                       is reused — no new keypair is generated.
#   --sign-update <bin> Path to sign_update. Defaults to release.sh's lookup
#                       (DerivedData → repo SPM cache).

import argparse
import os
import re
import subprocess
import sys


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def find_sign_update():
    derived = os.path.expanduser('~/Library/Developer/Xcode/DerivedData')
    candidates = []
    for root in (derived, REPO_ROOT):
        if not os.path.isdir(root):
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            if 'old_dsa_scripts' in dirpath:
                continue
            if 'sign_update' in filenames and dirpath.endswith('Sparkle/bin'):
                candidates.append(os.path.join(dirpath, 'sign_update'))
    return candidates[0] if candidates else None


def sign_zip(sign_update_bin, zip_path):
    if not sign_update_bin:
        sign_update_bin = find_sign_update()
    if not sign_update_bin or not os.path.isfile(sign_update_bin):
        print(
            'ERROR: sign_update not found. Build the project in Xcode first to '
            'resolve the Sparkle SPM package, or pass --sign-update <path>.',
            file=sys.stderr,
        )
        sys.exit(1)

    out = subprocess.run(
        [sign_update_bin, zip_path], capture_output=True, text=True, check=False
    )
    combined = (out.stdout or '') + (out.stderr or '')
    if out.returncode != 0:
        print(f'ERROR: sign_update failed:\n{combined}', file=sys.stderr)
        sys.exit(1)

    sig_match = re.search(r'sparkle:edSignature="([^"]+)"', combined)
    len_match = re.search(r'length="([0-9]+)"', combined)
    if not sig_match or not len_match:
        print(
            f'ERROR: could not parse sign_update output:\n{combined}',
            file=sys.stderr,
        )
        sys.exit(1)
    return sig_match.group(1), len_match.group(1)


def main():
    parser = argparse.ArgumentParser(
        description='Prepend a new release entry to a per-core Sparkle appcast.'
    )
    parser.add_argument('appcast_path')
    parser.add_argument('core_name')
    parser.add_argument('version')
    parser.add_argument('download_url')
    parser.add_argument('length')
    parser.add_argument('--sign-zip', default=None,
                        help='Local zip to sign with Sparkle EdDSA.')
    parser.add_argument('--sign-update', default=None,
                        help='Path to sign_update binary.')
    args = parser.parse_args()

    ed_sig = None
    length = args.length
    if args.sign_zip:
        ed_sig, length = sign_zip(args.sign_update, args.sign_zip)

    sig_attr = f'\n        sparkle:edSignature="{ed_sig}"' if ed_sig else ''
    new_item = f"""    <item>
      <title>{args.core_name} {args.version}</title>
      <sparkle:minimumSystemVersion>11.0</sparkle:minimumSystemVersion>
      <enclosure
        url="{args.download_url}"
        sparkle:version="{args.version}"
        sparkle:shortVersionString="{args.version}"
        length="{length}"{sig_attr}
        type="application/octet-stream" />
    </item>"""

    with open(args.appcast_path, 'r') as f:
        content = f.read()

    insert_after = re.search(r'(<title>[^<]*</title>\s*)', content)
    if not insert_after:
        print(f'ERROR: could not find insertion point in {args.appcast_path}',
              file=sys.stderr)
        sys.exit(1)

    pos = insert_after.end()
    content = content[:pos] + new_item + '\n' + content[pos:]

    with open(args.appcast_path, 'w') as f:
        f.write(content)

    suffix = ' (signed)' if ed_sig else ''
    print(f'Prepended {args.core_name} {args.version} entry to '
          f'{args.appcast_path}{suffix}')


if __name__ == '__main__':
    main()

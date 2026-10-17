#!/usr/bin/env python3
"""Add locally obtained Bosch SDKs to libraries already installed by Arduino IDE."""
import argparse
from pathlib import Path
import subprocess
import sys

from install_bsec import install


def find_library(collection, name, version):
    matches = []
    for props in collection.glob('*/library.properties'):
        metadata = dict(line.split('=', 1) for line in props.read_text().splitlines()
                        if '=' in line and not line.startswith('#'))
        if metadata.get('name') == name:
            if metadata.get('version') != version:
                raise SystemExit(f'{name}: expected tested version {version}, found {metadata.get("version")} in {props.parent}')
            matches.append(props.parent)
    if len(matches) != 1:
        raise SystemExit(f'Expected exactly one {name} {version} under {collection}; found {len(matches)}. '
                         'Install it in Library Manager and remove duplicate copies first.')
    return matches[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--libraries-dir', type=Path, required=True, help='Sketchbook libraries folder, from Arduino IDE Preferences')
    parser.add_argument('--bsec-zip', type=Path, required=True, help='Bosch BSEC 3.3.0.1 SDK ZIP')
    parser.add_argument('--bmv-zip', type=Path, required=True, help='Bosch BMV080 SDK 11.2.0 ZIP')
    args = parser.parse_args()
    # Folder names vary between IDE installations. Read Arduino metadata instead.
    find_library(args.libraries_dir, 'BME690-Arduino-lib-unofficial', '0.0.1')
    bsec = find_library(args.libraries_dir, 'Bsec3-ArduinoLibrary-Unofficial', '0.0.1')
    bmv = find_library(args.libraries_dir, '7Semi BMV080', '1.0.0')
    find_library(args.libraries_dir, 'ArduinoJson', '7.0.4')
    for archive in (args.bsec_zip, args.bmv_zip):
        if not archive.is_file():
            raise SystemExit(f'Missing SDK ZIP: {archive}')
    install(args.bsec_zip, bsec)
    subprocess.run([sys.executable, str(Path(__file__).with_name('install_bmv080.py')),
                    str(args.bmv_zip.resolve()), '--library-dir', str(bmv.resolve())], check=True)
    print('Arduino libraries ready for Polverine ESP32-S3. Restart Arduino IDE before Verify.')


if __name__ == '__main__':
    main()

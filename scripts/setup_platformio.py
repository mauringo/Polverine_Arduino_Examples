#!/usr/bin/env python3
"""Download published Arduino dependencies, then install your local Bosch SDKs."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bsec-zip', type=Path, required=True)
    parser.add_argument('--bmv-zip', type=Path, help='Required except when preparing only polverine-bsec3')
    parser.add_argument('-e', '--environment', action='append',
                        choices=['polverine-full', 'polverine-bsec3', 'polverine-debug'],
                        help='Repeat for multiple environments (default: polverine-full)')
    args = parser.parse_args()
    environments = args.environment or ['polverine-full']
    if any(env != 'polverine-bsec3' for env in environments) and not args.bmv_zip:
        parser.error('--bmv-zip is required for full/debug builds')
    for archive in filter(None, (args.bsec_zip, args.bmv_zip)):
        if not archive.is_file():
            raise SystemExit(f'Missing SDK ZIP: {archive}')
    # VS Code's PlatformIO installation may not expose pio on the shell PATH.
    pio = shutil.which('pio') or str(Path.home() / '.platformio/penv/bin/pio')
    if not Path(pio).is_file():
        raise SystemExit('PlatformIO CLI not found. Install PlatformIO IDE or add pio to PATH.')
    subprocess.run([pio, 'pkg', 'install', *[arg for env in environments for arg in ('-e', env)]], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / 'scripts/install_bsec.py'), str(args.bsec_zip.resolve())], check=True)
    if args.bmv_zip:
        subprocess.run([sys.executable, str(ROOT / 'scripts/install_bmv080.py'), str(args.bmv_zip.resolve())], check=True)
    print('PlatformIO ready. Build with: pio run -e ' + environments[0])


if __name__ == '__main__':
    main()

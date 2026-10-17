#!/usr/bin/env python3
"""Install your Bosch SDK into downloaded PlatformIO packages or a chosen library."""
import argparse
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
NAME = 'Bsec3-ArduinoLibrary-Unofficial'


def install(archive, library, mcu='esp32s3'):
    installer = library / 'scripts/install_bsec.py'
    if not installer.is_file():
        raise SystemExit(f'No BSEC3 installer in {library}. Install the Arduino library first.')
    subprocess.run([sys.executable, str(installer), str(archive.resolve()), '--mcu', mcu], check=True)
    print(f'BSEC3 SDK ready: {library}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--library-dir', type=Path, help='Exact installed library folder (Arduino IDE or development clone)')
    parser.add_argument('--mcu', choices=['esp32', 'esp32s2', 'esp32s3', 'esp32c3'], default='esp32s3')
    args = parser.parse_args()
    if args.library_dir:
        libraries = [args.library_dir]
    else:
        libraries = [p.parent for p in (ROOT / '.pio/libdeps').glob('*/*/library.properties')
                     if f'name={NAME}' in p.read_text().splitlines()]
        if not libraries:
            raise SystemExit('No downloaded BSEC3 package. Run "pio pkg install" first, or use --library-dir PATH.')
    for library in libraries:
        install(args.archive, library, args.mcu)


if __name__ == '__main__':
    main()

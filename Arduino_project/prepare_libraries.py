#!/usr/bin/env python3
"""Assemble local Arduino libraries including locally installed Bosch SDK files."""
from pathlib import Path
import shutil

sketch = Path(__file__).resolve().parent
root = sketch.parent
output = sketch / 'libraries'
required = [root / 'lib/BSEC3_unofficial/src/esp32s3/libalgobsec.a',
            root / 'lib/BSEC3_unofficial/src/config/bme690',
            *[root / 'private/bmv080' / n for n in
              ('bmv080.h', 'bmv080_defs.h', 'lib_bmv080.a', 'lib_postProcessor.a')]]
for source in required:
    if not source.exists():
        raise SystemExit(f'Missing {source}. Run both SDK installers first; see README.md.')
for name in ('BME690_unofficial', 'BSEC3_unofficial', '7Semi_BMV080'):
    dest = output / name
    if dest.exists():
        raise SystemExit(f'{dest} already exists. Move/remove that generated folder before regenerating.')
output.mkdir(exist_ok=True)
for name in ('BME690_unofficial', 'BSEC3_unofficial', '7Semi_BMV080'):
    shutil.copytree(root / 'lib' / name, output / name,
                    ignore=shutil.ignore_patterns('.git', '*.a', '*.zip', '.pio', '__pycache__'))
# Arduino mixed-source libraries select ESP32-S3 archives under src/esp32s3.
bsec = output / 'BSEC3_unofficial'
(bsec / 'src/esp32s3').mkdir(parents=True, exist_ok=True)
shutil.copy2(required[0], bsec / 'src/esp32s3/libalgobsec.a')
bmv = output / '7Semi_BMV080'
(bmv / 'src/esp32s3').mkdir(parents=True, exist_ok=True)
for name in ('bmv080.h', 'bmv080_defs.h'):
    shutil.copy2(root / 'private/bmv080' / name, bmv / 'src' / name)
for name in ('lib_bmv080.a', 'lib_postProcessor.a'):
    shutil.copy2(root / 'private/bmv080' / name, bmv / 'src/esp32s3' / name)
print(f'Prepared {output}\nCopy these three folders into your Arduino sketchbook libraries folder.\nThey contain local Bosch SDK files: do not commit or redistribute them.')

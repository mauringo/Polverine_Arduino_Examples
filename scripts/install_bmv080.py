#!/usr/bin/env python3
"""Install BMV080 ESP32-S3 SDK files locally; never committed."""
import argparse
from pathlib import Path
from zipfile import ZipFile
root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('archive', type=Path)
a = p.parse_args()
dest = root / 'private/bmv080'
with ZipFile(a.archive) as z:
    members = {name: 'api/inc/' + name for name in ['bmv080.h', 'bmv080_defs.h']}
    members.update({name: 'api/lib/xtensa_esp32s3/xtensa_esp32s3_elf_gcc/release/' + name
                    for name in ['lib_bmv080.a', 'lib_postProcessor.a']})
    content = {name: z.read(member) for name, member in members.items()}
    dest.mkdir(parents=True, exist_ok=True)
    for name, data in content.items(): (dest / name).write_bytes(data)
print(f'Installed SDK files to ignored directory {dest}')

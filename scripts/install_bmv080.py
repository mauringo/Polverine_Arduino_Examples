#!/usr/bin/env python3
"""Install BMV080 ESP32-S3 SDK files locally; never committed."""
import argparse
from pathlib import Path
from zipfile import ZipFile
root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('archive', type=Path)
p.add_argument('--library-dir', type=Path, help='Also install into this Arduino Library Manager library folder')
a = p.parse_args()
if a.library_dir:
    props = a.library_dir / 'library.properties'
    if not props.is_file() or 'name=7Semi BMV080' not in props.read_text().splitlines():
        raise SystemExit('The --library-dir folder must contain the installed 7Semi BMV080 library.')
dest = root / 'private/bmv080'
with ZipFile(a.archive) as z:
    members = {name: 'api/inc/' + name for name in ['bmv080.h', 'bmv080_defs.h']}
    members.update({name: 'api/lib/xtensa_esp32s3/xtensa_esp32s3_elf_gcc/release/' + name
                    for name in ['lib_bmv080.a', 'lib_postProcessor.a']})
    content = {name: z.read(member) for name, member in members.items()}
    for name, data in content.items():
        if name.endswith('.a') and not data.startswith(b'!<arch>\n'):
            raise SystemExit(f'Invalid static archive: {name}')
    dest.mkdir(parents=True, exist_ok=True)
    for name, data in content.items():
        (dest / name).write_bytes(data)
    if a.library_dir:
        for name, data in content.items():
            target = a.library_dir / 'src' / ('esp32s3' if name.endswith('.a') else '') / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        print(f'BMV080 SDK ready: {a.library_dir}')
print(f'Installed SDK files to ignored directory {dest}')

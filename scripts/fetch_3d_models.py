#!/usr/bin/env python3
"""Sparse-clone BlackIoT's Polverine board CAD and extract its STEP model locally."""
import argparse
from pathlib import Path
import subprocess
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://github.com/BlackIoT/Polverine.git'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, default=ROOT / 'hardware/Polverine')
    args = parser.parse_args()
    dest = args.destination.resolve()
    if dest.exists():
        raise SystemExit(f'{dest} already exists. Choose a new --destination; existing CAD work is never overwritten.')
    # --no-checkout avoids downloading all the working-tree blobs first.
    subprocess.run(['git', 'clone', '--depth', '1', '--filter=blob:none', '--no-checkout', URL, str(dest)], check=True)
    git = ['git', '-C', str(dest)]
    subprocess.run([*git, 'sparse-checkout', 'set', '--no-cone',
                    '/DOCS/README.md', '/DOCS/Polverine3D.zip', '/LICENSE'], check=True)
    subprocess.run([*git, 'checkout'], check=True)
    model = dest / 'DOCS/Polverine.stp'
    with ZipFile(dest / 'DOCS/Polverine3D.zip') as archive:
        # Extract only the expected file, never arbitrary archive paths.
        model.write_bytes(archive.read('Polverine.stp'))
    revision = subprocess.check_output([*git, 'rev-parse', 'HEAD'], text=True).strip()
    (dest / 'SOURCE.txt').write_text(f'Source: {URL}\nCommit: {revision}\n'
                                     'Polverine board STEP model extracted from DOCS/Polverine3D.zip.\n'
                                     'Retain upstream notices and review LICENSE before reuse.\n')
    print(f'Board CAD ready: {model}\nUpstream commit: {revision}\n'
          'This STEP board model is a CAD reference; printable covers are linked in docs/3D_MODELS.md.')


if __name__ == '__main__':
    main()

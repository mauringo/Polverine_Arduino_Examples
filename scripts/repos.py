#!/usr/bin/env python3
"""Manage the project and the two independently publishable library repositories."""
import argparse
import json
from pathlib import Path
import subprocess
import re

ROOT = Path(__file__).resolve().parents[1]
REPOS = {'example': ROOT, 'bme690': ROOT / 'lib/BME690-Arduino-lib-unofficial', 'bsec3': ROOT / 'lib/Bsec3-ArduinoLibrary-Unofficial'}
BLOCKED = {'.zip', '.a', '.lib', '.bin', '.elf', '.o', '.so', '.dll', '.dylib'}

def git(repo, *args, capture=False):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True) if capture else subprocess.check_call(['git', '-C', str(repo), *args])

def audit(repo, history=False):
    files = git(repo, 'ls-files', '-z', capture=True).split('\0')
    has_head = subprocess.run(["git", "-C", str(repo), "rev-parse", "--verify", "HEAD"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    if history and has_head:
        # Check every object reachable from the branch being pushed, including old commits.
        files += [line.partition(' ')[2] for line in git(repo, 'rev-list', '--objects', 'HEAD', capture=True).splitlines()]
    bad = [f for f in files if f and Path(f).suffix.lower() in BLOCKED]
    if repo == ROOT:
        bad += [f for f in files if f.startswith(('lib/', 'Arduino_project/libraries/', 'hardware/Polverine/'))]
    if bad:
        raise SystemExit('Refusing operation: prohibited files in index/history:\n' + '\n'.join(sorted(set(bad))))

def metadata(repo):
    props = dict(line.split('=', 1) for line in (repo / 'library.properties').read_text().splitlines()
                 if '=' in line and not line.startswith('#'))
    version = props.get('version', '')
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise SystemExit('Set a three-part Arduino library version before releasing')
    manifest = json.loads((repo / 'library.json').read_text())
    if manifest.get('version') != version or manifest.get('name') != props.get('name'):
        raise SystemExit('library.json and library.properties names/versions must agree')
    return version

def record_published(repo):
    path = ROOT / 'libraries.json'
    dependencies = json.loads(path.read_text())
    dependencies[repo.name]['revision'] = git(repo, 'rev-parse', 'HEAD', capture=True).strip()
    path.write_text(json.dumps(dependencies, indent=2) + '\n')
    print('Updated libraries.json to the published commit. Publish the main project when ready.')

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('action', choices=['bootstrap', 'status', 'diff', 'commit', 'push', 'audit', 'release'])
p.add_argument('target', nargs='?', choices=[*REPOS, 'all'], default='all')
p.add_argument('-m', '--message')
a = p.parse_args()
if a.action == 'bootstrap':
    for name, spec in json.loads((ROOT / 'libraries.json').read_text()).items():
        dest = ROOT / 'lib' / name
        if not dest.exists():
            subprocess.check_call(['git', 'clone', spec['url'], str(dest)])
            git(dest, 'checkout', '-B', 'main', spec['revision'])
    raise SystemExit(0)
if a.action in ('commit', 'push', 'release') and a.target == 'all':
    p.error('Choose example, bme690, or bsec3 explicitly for commit/push')
for name in (REPOS if a.target == 'all' else [a.target]):
    repo = REPOS[name]
    print(f'\n{name}: {repo}', flush=True)
    if a.action == 'status': git(repo, 'status', '--short', '--branch')
    elif a.action == 'diff': git(repo, 'diff', 'HEAD')
    elif a.action == 'commit':
        if not a.message: p.error('commit requires -m MESSAGE')
        git(repo, 'add', '--all')
        audit(repo)
        pending = subprocess.run(['git', '-C', str(repo), 'diff', '--cached', '--quiet'])
        if pending.returncode == 0:
            print('No staged source changes to commit.')
        elif pending.returncode == 1:
            git(repo, 'commit', '-m', a.message)
        else:
            raise SystemExit('Could not inspect staged changes; commit aborted')
    elif a.action == 'push':
        audit(repo, history=True)
        # Push only the current branch; never tags or every local branch.
        branch = git(repo, 'symbolic-ref', '--short', 'HEAD', capture=True).strip()
        git(repo, 'push', 'origin', f'HEAD:refs/heads/{branch}')
        if name != 'example': record_published(repo)
    elif a.action == 'release':
        if name == 'example': p.error('Arduino releases apply to bme690 or bsec3')
        audit(repo, history=True)
        if git(repo, 'status', '--porcelain', capture=True).strip():
            raise SystemExit('Commit library source changes before creating a release')
        tag = 'v' + metadata(repo)
        head = git(repo, 'rev-parse', 'HEAD', capture=True).strip()
        existing = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--verify', tag + '^{}'],
                                  capture_output=True, text=True)
        if existing.returncode == 0:
            if existing.stdout.strip() != head:
                raise SystemExit(f'{tag} already identifies another commit; bump the library version')
        else:
            git(repo, 'tag', '-a', tag, '-m', f'{repo.name} {tag}')
        git(repo, 'push', 'origin', 'refs/tags/' + tag)
        print(f'Published Arduino release {tag}. The registry will index eligible tags for this registered library.')
    elif a.action == 'audit': audit(repo, history=True)

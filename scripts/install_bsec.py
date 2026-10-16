#!/usr/bin/env python3
"""Delegate SDK installation to the BSEC3 library's installer."""
from pathlib import Path
import subprocess
import sys
root = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(root / 'lib/BSEC3_unofficial/scripts/install_bsec.py'), *sys.argv[1:]], check=True)

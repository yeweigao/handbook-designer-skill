#!/usr/bin/env python3
"""Refresh checked-in specimen previews from a verified PDF build (no extra packages)."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / 'dev/samples/native/folio-system'

def main():
    if len(sys.argv) != 2 or not re.fullmatch(r'[a-f0-9]{12}', sys.argv[1]):
        raise SystemExit('Usage: python3 dev/folio-css/update-preview.py BUILD_ID')
    build = sys.argv[1]
    subprocess.run(['node', str(ROOT / 'hb/core/cli.mjs'), 'verify', str(PROJECT)], check=True)
    gate = json.loads((PROJECT / '.qa' / build / 'gate.json').read_text())
    pdf = PROJECT / gate['languages']['zh-CN']['pdf']
    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == gate['languages']['zh-CN']['pdf_sha256']
    # The preview references the project's frozen resources, never repo-wide mutable CSS.
    snapshot = (PROJECT / '.build' / build / 'zh-CN/snapshot.html').read_text()
    snapshot = re.sub(r'<base\b[^>]*>', '', snapshot)
    snapshot = snapshot.replace('<head>', '<head><!-- Generated view only; edit book.html and book.css. -->', 1)
    # Zoom only the screen presentation; printed geometry is the runtime's own CSS.
    screen = '''<style>@media screen{body{background:#e9e9e5}.page{box-shadow:0 1px 12px #18223818}}@media screen and (max-width:850px){body{align-items:flex-start}.page{zoom:calc((100vw - 16px) / (216mm));margin-left:8px}}</style>'''
    snapshot = snapshot.replace('</head>', screen + '</head>')
    (PROJECT / 'preview.html').write_text(snapshot)
    raster = PROJECT / '.qa' / build / 'zh-CN/raster'
    shutil.copyfile(raster / 'sheet.png', ROOT / 'dev/folio-css/specimen.png')
    (ROOT / 'dev/folio-css/specimen.json').write_text(json.dumps({
        'build_id': build,
        'pdf_sha256': gate['languages']['zh-CN']['pdf_sha256'],
        'page_count': gate['languages']['zh-CN']['pages'],
        'family_css_sha256': hashlib.sha256((PROJECT / 'design.css').read_bytes()).hexdigest(),
        'preview': '../samples/native/folio-system/preview.html',
        'source': '../samples/native/folio-system/book.html',
    }, indent=2) + '\n')
    print(f'Updated Folio showcase specimen from {build}')

if __name__ == '__main__':
    main()

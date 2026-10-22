#!/usr/bin/env python3
"""Refresh checked-in specimen previews from a verified PDF build (no extra packages)."""
import hashlib
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build')
    parser.add_argument('--project', choices=['folio-system', 'folio-business'], default='folio-system')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-f0-9]{12}', args.build):
        parser.error('BUILD_ID must be twelve hexadecimal characters')
    build = args.build
    PROJECT = ROOT / 'dev/samples/native' / args.project
    result = subprocess.run(['node', '--input-type=module', '-e',
        'const {verify}=await import(process.argv[1]);const r=await verify(process.argv[2]);'
        'console.log(JSON.stringify({valid:r.valid,buildId:r.buildId,reasons:r.reasons}));if(!r.valid)process.exit(1);',
        (ROOT / 'hb/core/gate.mjs').as_uri(), str(PROJECT)], check=True, capture_output=True, text=True)
    current = json.loads(result.stdout)
    if current['buildId'] != build:
        raise SystemExit(f'Refusing stale preview {build}; current verified build is {current["buildId"]}')
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
    prefix = 'specimen' if args.project == 'folio-system' else 'business-specimen'
    shutil.copyfile(raster / 'sheet.png', ROOT / f'dev/folio-css/{prefix}.png')
    (ROOT / f'dev/folio-css/{prefix}.json').write_text(json.dumps({
        'build_id': build,
        'pdf_sha256': gate['languages']['zh-CN']['pdf_sha256'],
        'page_count': gate['languages']['zh-CN']['pages'],
        'family_css_sha256': hashlib.sha256((PROJECT / 'design.css').read_bytes()).hexdigest(),
        'preview': f'../samples/native/{args.project}/preview.html',
        'source': f'../samples/native/{args.project}/book.html',
    }, indent=2) + '\n')
    print(f'Updated Folio showcase specimen from {build}')

if __name__ == '__main__':
    main()

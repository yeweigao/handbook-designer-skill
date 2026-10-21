#!/usr/bin/env python3
"""Translate reader copy while preserving image/layout identifiers and editable marginalia."""
import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import yaml

HB = Path(__file__).resolve().parents[2] / 'hb'


def run(script, *args, expect=0):
    got = subprocess.run([sys.executable, str(HB / script), *map(str, args)],
                         capture_output=True, text=True)
    assert got.returncode == expect, got.stdout + got.stderr
    return got.stdout + got.stderr


def main():
    with tempfile.TemporaryDirectory(prefix='hb-editorial-content-') as td:
        project = Path(td)
        metadata = 'Internal production note.'
        note = 'Keep observations separate from assumptions.'
        translated_note = 'Les observations restent distinctes des suppositions.'
        main_copy = 'A complete observation records a visible detail.'
        spec = dict(book=dict(lang='en', style='editorial', fonts=dict(preset='sans')),
                    pages=[dict(layout='MARGINALIA', title='Observe carefully.', note=metadata,
                                sections=[dict(x=main_copy, note_title='Observation reminder',
                                               note=note)])])
        source = project / 'book.yaml'
        source.write_text(yaml.safe_dump(spec), encoding='utf-8')
        strings_path = project / 'strings.json'
        run('i18n.py', 'extract', source, strings_path)
        strings = json.loads(strings_path.read_text(encoding='utf-8'))
        assert note in strings, 'Visible marginalia was omitted from translation extraction'
        assert metadata not in strings, 'Page production metadata became translatable copy'
        strings[note] = translated_note
        strings_path.write_text(json.dumps(strings), encoding='utf-8')
        translated = project / 'translated'
        run('i18n.py', 'apply', source, strings_path, translated, 'fr')
        result = yaml.safe_load((translated / 'book.yaml').read_text(encoding='utf-8'))
        assert result['pages'][0]['sections'][0]['note'] == translated_note
        assert result['pages'][0]['note'] == metadata

        # Translators must never receive filenames, image options or surface identifiers.
        assets_spec = copy.deepcopy(spec)
        assets_spec['pages'] += [
            dict(layout='SEQUENCE', surface='dark', items=[
                dict(img='scene.jpg', k='SCENE', t='Main scene', x='Read the surroundings.'),
                dict(img=dict(src='detail.jpg', fit='contain', focus=[.25, .75]),
                     k='DETAIL', t='A close detail', x='Look at its edges.'),
                dict(img='ai:motion', k='MOTION', t='A flowing scene', x='Follow the water.')]),
            dict(layout='COLLAGE', surface='paper', images=['view-one.jpg', 'view-two.jpg']),
        ]
        assets_source = project / 'assets.yaml'
        assets_source.write_text(yaml.safe_dump(assets_spec), encoding='utf-8')
        assets_strings = project / 'assets-strings.json'
        run('i18n.py', 'extract', assets_source, assets_strings)
        extracted = json.loads(assets_strings.read_text(encoding='utf-8'))
        identifiers = {'SEQUENCE', 'COLLAGE', 'dark', 'paper', 'scene.jpg', 'detail.jpg',
                       'ai:motion', 'contain', 'view-one.jpg', 'view-two.jpg'}
        assert not identifiers.intersection(extracted), 'Image/layout identifiers became translatable copy'
        visible = {'SCENE', 'Main scene', 'Read the surroundings.',
                   'DETAIL', 'A close detail', 'Look at its edges.',
                   'MOTION', 'A flowing scene', 'Follow the water.', note, 'Observation reminder'}
        assert visible.issubset(extracted), 'A reader-facing k/t/x or marginal note was skipped'
        # Include hostile-to-structure translations deliberately: skipped values must still survive apply.
        mapping = {s: 'Translated: ' + s for s in visible | identifiers}
        assets_strings.write_text(json.dumps(mapping), encoding='utf-8')
        assets_out = project / 'assets-translated'
        run('i18n.py', 'apply', assets_source, assets_strings, assets_out, 'fr')
        converted = yaml.safe_load((assets_out / 'book.yaml').read_text(encoding='utf-8'))
        for before, after in zip(assets_spec['pages'][1:], converted['pages'][1:]):
            assert after['layout'] == before['layout'] and after['surface'] == before['surface']
            if 'images' in before:
                assert after['images'] == before['images']
            for old_item, new_item in zip(before.get('items', []), after.get('items', [])):
                assert new_item['img'] == old_item['img'], 'Image path/options were translated'
                for key in ('k', 't', 'x'):
                    assert new_item[key] == mapping[old_item[key]]
        assert converted['pages'][0]['sections'][0]['note'] == mapping[note]
        assert converted['pages'][0]['note'] == metadata

        # Exercise the actual layout and export path, not a mocked editor leaf list.
        run('hb.py', project)
        edit = project / 'out/edit_en.html'
        run('edit_page.py', project, edit)
        rendered = edit.read_text(encoding='utf-8')
        config = re.search(r'window\.HB_EDIT=(.*?);</script>', rendered, re.S)
        assert config, 'Editor configuration was not exported'
        leaves = json.loads(config.group(1))['leaves']
        paths = {leaf['path']: leaf['text'] for leaf in leaves}
        assert paths.get('pages[0].sections[0].note') == note
        assert 'pages[0].note' not in paths, 'Internal page note became editable printed copy'

        # Marginalia is already ordinary HTML text: both missing and added copy must be reported.
        reference = project / 'doc.md'
        reference.write_text(main_copy + '\n' + note + '\n', encoding='utf-8')
        output = run('check_copy.py', project)
        assert 'MISSING 0' in output
        html_path = project / 'book.html'
        html_source = html_path.read_text(encoding='utf-8')
        assert note in html_source
        html_path.write_text(html_source.replace(note, ''), encoding='utf-8')
        output = run('check_copy.py', project, expect=1)
        assert 'MISSING: ' + note in output
        html_path.write_text(html_source, encoding='utf-8')
        reference.write_text(main_copy + '\n', encoding='utf-8')
        output = run('check_copy.py', project)
        assert 'EXTRA: ' + note in output, 'Visible note was treated as decorative copy'

        # A shared reading title is one editable source for the opening and continuation.
        shared = 'Write what you see'
        spec['book']['series'] = {'essays': {'label': 'Field essay', 'items': {'01': shared}}}
        spec['pages'] = [dict(layout='READING', series_header=dict(series='essays', item='01'), text=['First passage.']),
                         dict(layout='READING', series_header=dict(series='essays', item='01', continuation=True), text=['Second passage.'])]
        source.write_text(yaml.safe_dump(spec), encoding='utf-8')
        run('i18n.py', 'extract', source, strings_path)
        extracted = json.loads(strings_path.read_text(encoding='utf-8'))
        assert shared in extracted and 'Field essay' in extracted
        assert 'essays' not in extracted and '01' not in extracted, 'Series references became translatable'
        strings_path.write_text(json.dumps({shared: 'Translated title', 'essays': 'wrong', '01': 'wrong'}), encoding='utf-8')
        run('i18n.py', 'apply', source, strings_path, translated, 'fr')
        converted = yaml.safe_load((translated / 'book.yaml').read_text(encoding='utf-8'))
        assert converted['book']['series']['essays']['items']['01'] == 'Translated title'
        assert converted['pages'][0]['series_header'] == spec['pages'][0]['series_header']
        run('hb.py', project)
        run('edit_page.py', project, edit)
        config = re.search(r'window\.HB_EDIT=(.*?);</script>', edit.read_text(encoding='utf-8'), re.S)
        leaves = json.loads(config.group(1))['leaves']
        path = 'book.series.essays.items.01'
        titles = [leaf for leaf in leaves if leaf['path'] == path]
        assert len(titles) == 1 and titles[0]['pages'] == [1, 2]
        assert not any(leaf['path'].endswith(('.series', '.item')) for leaf in leaves)
        changes = project / 'edits.json'
        changes.write_text(json.dumps([dict(path=path, lang='en', old=shared, new='Describe a detail')]), encoding='utf-8')
        output = run('sync_edits.py', project, changes)
        assert '跳过 0 处' in output, output
        run('hb.py', project)
        changed = html_path.read_text(encoding='utf-8')
        assert changed.count('Describe a detail') == 2 and shared not in changed
        reference.write_text('First passage.\nSecond passage.\nDescribe a detail.\n', encoding='utf-8')
        output = run('facts.py', project)
        assert '[无出处数字] 01' not in output, 'A structural series ID was treated as a factual claim'
        spec = yaml.safe_load(source.read_text(encoding='utf-8'))
        spec['book']['series']['essays']['items']['01'] = 'Observe 47 details'
        source.write_text(yaml.safe_dump(spec), encoding='utf-8')
        assert '[无出处数字] 47' in run('facts.py', project), 'A number in a shared reader title escaped fact checking'
        # A figure caption and the following label are separate reader strings.
        isolated = project / 'caption'; isolated.mkdir()
        (isolated / 'book.html').write_text('<section class="page" data-n="1"><figure><figcaption>Caption one.</figcaption></figure><div>Separate label.</div><p>Original paragraph.</p></section>', encoding='utf-8')
        (isolated / 'doc.md').write_text('Separate label.\nOriginal paragraph.\nCaption one.\n', encoding='utf-8')
        output = run('check_copy.py', isolated)
        assert 'MISSING 0' in output and 'EXTRA 0' in output, output
    print('EDITORIAL CONTENT: PASS — reader copy translates, asset/layout identifiers survive, notes edit and pass copy checks')


if __name__ == '__main__':
    main()

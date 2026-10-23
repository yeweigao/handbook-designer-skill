#!/usr/bin/env python3
"""Build the complete native Folio specimen from the same catalog as the website.

No screenshots, browser scaling, or second hand-maintained set of recipes. Each
catalog ID maps to one or more real A4 pages in coverage.json. Full-page recipes
become physical pages; the panorama becomes two adjacent pages in shared trim
coordinates. Fonts are frozen static faces, subset to this book's actual corpus.
Run dev/build-folio-css.py first. This creates author sources, not QA approval.
"""
from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SHOWCASE = ROOT / 'dev/folio-css'
DEFAULT_PROJECT = ROOT / 'dev/samples/native/folio-swiss'
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
INLINE = {'em', 'strong', 'a', 'br', 'sup', 'sub', 'span'}
SECTIONS = ('atoms', 'layouts', 'components', 'expressions', 'variations')
NAMES = {'atoms': '原子与规则', 'layouts': '布局关系', 'components': '内容组件', 'expressions': '表现与变奏', 'variations': '表现与变奏'}


class Node:
    def __init__(self, tag='', attrs=None, children=None):
        self.tag, self.attrs, self.children = tag, dict(attrs or []), list(children or [])

    @property
    def classes(self):
        return self.attrs.get('class', '').split()

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()

    def text(self):
        return ''.join(child.text() if isinstance(child, Node) else child for child in self.children)

    def serialize(self):
        inner = ''.join(c.serialize() if isinstance(c, Node) else html.escape(c, quote=False) for c in self.children)
        if not self.tag:
            return inner
        attrs = ''.join(f' {k}="{html.escape(v, quote=True)}"' for k, v in self.attrs.items())
        if self.tag in VOID:
            return f'<{self.tag}{attrs}>'
        return f'<{self.tag}{attrs}>{inner}</{self.tag}>'


class Fragment(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def element(tag, text='', classes='', **attrs):
    if classes:
        attrs['class'] = classes
    return Node(tag, attrs, [text] if text else [])


def add_class(node, *classes):
    node.attrs['class'] = ' '.join(dict.fromkeys(node.classes + list(classes)))


def style_map(text):
    return dict((p.split(':', 1)[0].strip(), p.split(':', 1)[1].strip()) for p in text.split(';') if ':' in p)


def set_style(node, **changes):
    styles = style_map(node.attrs.get('style', ''))
    for key, val in changes.items():
        if val is None:
            styles.pop(key, None)
        else:
            styles[key] = val
    node.attrs['style'] = ';'.join(f'{k}:{v}' for k, v in styles.items())


def corpus_text(node):
    return ''.join('\n' if isinstance(c, Node) and c.tag == 'br' else corpus_text(c) if isinstance(c, Node) else c for c in node.children)


def annotate(root, prefix):
    """Mark real leaf content, preserving allowed inline markup and recipe roles."""
    segments = []

    def visit(node, role='body', deco=False, svg=False):
        cls = node.classes
        deco = deco or node.attrs.get('data-role') == 'deco' or node.attrs.get('aria-hidden') == 'true'
        svg = svg or node.tag == 'svg'
        role = node.attrs.get('data-role', role)
        if not node.attrs.get('data-role'):
            if any(c in cls for c in ('fl-caption', 'fl-aux', 'fl-kicker', 'fl-meta', 'fl-foot', 'fl-legend', 'fl-dim', 'fl-dim-v', 'fl-proof', 'fl-size-aux')):
                role = 'aux'
            elif any(c in cls for c in ('fl-key', 'fl-size-key', 'fl-size-small', 'fl-index-n', 'fl-index-end')):
                role = 'key'
            elif node.tag in ('h1', 'h2', 'h3', 'h4') or any(c in cls for c in ('fl-number', 'fl-hero', 'fl-display', 'fl-h1', 'fl-h2', 'fl-h3', 'fl-term', 'fl-size-giant', 'fl-size-colossal')):
                role = 'display'
            elif node.tag == 'th':
                role = 'aux'
        children = [c for c in node.children if isinstance(c, Node)]
        inline_only = all(c.tag in INLINE for c in node.walk() if c is not node)
        readable = corpus_text(node).strip()
        # A container containing only inline elements is one editable content node.
        direct_text = any(isinstance(c, str) and c.strip() for c in node.children)
        leaf_block = node.tag in ('p','h1','h2','h3','h4','h5','h6','td','th','figcaption','blockquote')
        if node.tag and not svg and not deco and inline_only and readable and (leaf_block or direct_text or not children):
            ident = f'{prefix}-{len(segments)+1:03d}'
            node.attrs['data-source-id'] = ident
            node.attrs['data-role'] = role
            segments.append({'id': ident, 'kind': 'heading' if node.tag in ('h1','h2','h3','h4') else 'cell' if node.tag in ('td','th') else 'para', 'text': corpus_text(node), 'origin': {'page': None, 'line': None}})
            return
        for child in children:
            visit(child, role, deco, svg)
    visit(root)
    return segments


def registry_for(path):
    for parent in path.parents:
        candidate = parent / 'sources/assets.json'
        if candidate.exists():
            data = json.loads(candidate.read_text())
            for ident, entry in data.get('assets', {}).items():
                if (parent / entry.get('file', '')).resolve() == path:
                    return ident, entry
        if parent == ROOT:
            break
    raise ValueError(f'No asset provenance found for {path}')


def localize(root, project, entry_id, assets):
    edits, old_edits = [], {}

    def copy_asset(value):
        if value.startswith(('data:', '#')):
            return value, None
        path = (SHOWCASE / value).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError(f'{entry_id}: missing or non-repository asset {value}')
        key, record = registry_for(path)
        target = project / 'assets/images' / path.name
        if target.exists() and target.read_bytes() != path.read_bytes():
            target = target.with_name(hashlib.sha256(path.read_bytes()).hexdigest()[:8] + '-' + path.name)
        if not target.parent.exists():
            target.parent.mkdir(parents=True)
        if not target.exists():
            shutil.copy2(path, target)
        rel = target.relative_to(project).as_posix()
        record = dict(record, file=rel)
        assets[key] = record
        return rel, key

    for node in root.walk():
        node.attrs.pop('data-source-id', None)
        node.attrs.pop('data-repeat', None)
        node.attrs.pop('loading', None)
        if node.tag == 'img' and node.attrs.get('src'):
            node.attrs['src'], key = copy_asset(node.attrs['src'])
            if key:
                node.attrs['data-asset'] = key
            ident = f'{entry_id}-image-{len(edits)+1}'
            if node.attrs.get('data-edit-id'):
                old_edits[node.attrs['data-edit-id']] = ident
            node.attrs['data-edit-id'] = ident
            edits.append(ident)
        if 'style' in node.attrs:
            node.attrs['style'] = re.sub(r'url\([\s\"\']*([^\)\"\']+)[\s\"\']*\)', lambda m: f'url({copy_asset(m.group(1).strip())[0]})', node.attrs['style'])
        if 'id' in node.attrs:
            old = node.attrs['id']
            node.attrs['id'] = f'{entry_id}-{old}'
            for other in root.walk():
                for attr in ('aria-labelledby', 'href', 'xlink:href'):
                    if other.attrs.get(attr) == old:
                        other.attrs[attr] = node.attrs['id']
                    if other.attrs.get(attr) == '#' + old:
                        other.attrs[attr] = '#' + node.attrs['id']
    for node in root.walk():
        if node.attrs.get('data-overlap'):
            node.attrs['data-overlap'] = ' '.join(old_edits.get(x, x) for x in node.attrs['data-overlap'].split())
        if 'fl-l-overlay' in node.classes:
            image_ids = [x.attrs['data-edit-id'] for x in node.walk() if x.tag == 'img']
            for child in node.walk():
                if 'fl-l-copy' in child.classes:
                    child.attrs['data-overlap'] = ' '.join(image_ids)
    return edits


BOOK_CSS = '''/* Generated specimen framing; recipe typography and geometry come from design.css.
No scale(), zoom, fit-to-page or text shrinking is used in printed pages. */
.specimen-area { display:flex; flex-direction:column; }
.specimen-heading { margin-bottom:28px; }
.specimen-heading h1 { margin-top:14px; }
.specimen-heading .specimen-summary { margin-top:14px; max-width:42em; }
.specimen-example { position:relative; min-width:0; flex:none; margin-block:auto; }
.specimen-notes { margin-top:auto; padding-top:28px; display:grid; grid-template-columns:1fr 1fr; gap:28px; }
.specimen-notes p { overflow-wrap:anywhere; }
.specimen-notes .specimen-classes { grid-column:1/-1; font-size:11px; line-height:1.5; }
.specimen-footer { display:flex; justify-content:space-between; gap:28px; margin-top:21px; padding-top:7px; border-top:1px solid var(--fl-stroke); }
.specimen-native-meta { position:absolute; left:calc(var(--bleed) + 19mm); right:calc(var(--bleed) + 19mm); bottom:calc(var(--bleed) + 9mm); display:flex; justify-content:space-between; gap:14px; padding:7px 10px; background:var(--fl-paper); color:var(--fl-ink); }
.specimen-native-meta * { color:inherit; }
.specimen-native-note { position:absolute; left:calc(var(--bleed) + 19mm); right:calc(var(--bleed) + 19mm); top:calc(var(--bleed) + 9mm); }
.specimen-cover-title { margin-top:84px; }
.specimen-cover-copy { margin-top:auto; max-width:32em; }
.specimen-index { list-style:none; padding:0!important; display:grid; grid-template-columns:1fr 1fr; gap:14px 28px; }
.specimen-index li { display:flex; align-items:baseline; justify-content:space-between; gap:14px; border-bottom:1px solid var(--fl-stroke); padding-bottom:7px; }
.specimen-section-no { margin-top:84px; }
'''


def metadata(entry, group):
    heading = Node('header', {'class': 'specimen-heading'})
    heading.children = [element('p', NAMES.get(group, group) + ' / ' + entry['id'], 'fl-kicker'), element('h1', entry['title'], 'fl-h1', **{'data-outline':'1'}), element('p', entry['description'], 'fl-key specimen-summary', **{'data-role':'key'})]
    notes = Node('aside', {'class':'specimen-notes'})
    notes.children = [element('p', '组合关系 / ' + entry.get('grammar',''), 'fl-key', **{'data-role':'key'}), element('p', '适用边界 / ' + entry.get('limits',''), 'fl-key fl-text-muted', **{'data-role':'key'}), element('p', 'CSS / ' + ' · '.join(entry.get('classes', [])), 'fl-caption specimen-classes', **{'data-role':'aux'})]
    return heading, notes


def footer(number, text='FOLIO / COMPLETE SPECIMEN'):
    return Node('footer', {'class':'specimen-footer'}, [element('span', text, 'fl-caption'), element('span', f'{number:03d}', 'fl-caption fl-font-number')])


def prepare_fonts(project, corpus, cache=None):
    """Reuse static fonts when available; otherwise initialize from local family sources."""
    from fontTools import subset
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    module_spec = importlib.util.spec_from_file_location('folio_family', ROOT/'hb/core/family.py')
    family_tool = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(family_tool)
    manifest = project / '.font-source.json'
    family = json.loads((ROOT / 'families/folio/family.json').read_text())
    source = Path(cache) if cache else Path('/private/tmp/folio-type-test')
    fonts = []
    if (source / 'project.json').exists():
        fonts = json.loads((source/'project.json').read_text())['fonts']
    required = {(f['family'],str(w)):f for f in family['fonts'] for w in f['weights']}
    cached = {(f['family'],f['weight']):f for f in fonts}
    fonts = [{'family':name,'weight':weight,'style':'normal','file':f'assets/fonts/{name.replace(" ","")}-{weight}.ttf'} for name,weight in required]
    signature = hashlib.sha256((corpus + json.dumps(family,sort_keys=True) + 'font-corpus-v2').encode()).hexdigest()
    existing = json.loads(manifest.read_text()) if manifest.exists() else {}
    target_dir = project / 'assets/fonts'
    if not target_dir.exists():
        target_dir.mkdir(parents=True)
    if existing.get('signature') != signature or any(not (project/f['file']).exists() for f in fonts):
        chars = set(map(ord, corpus)) | set(range(32,127)) | {0xA0,0x2013,0x2014,0x2022}
        for face in fonts:
            record = required[(face['family'],face['weight'])]
            original = Path(family_tool.find_source(record['source']))
            font = TTFont(original)
            # A previous GB2312-only static cache can miss U+2212 or new copy.
            # Reuse it only when it contains every relevant glyph of the source.
            cached_face = cached.get((face['family'],face['weight']))
            if cached_face and (source/cached_face['file']).is_file():
                static = TTFont(source/cached_face['file'])
                needed = chars & set(font.getBestCmap() or {})
                if needed <= set(static.getBestCmap() or {}):
                    font.close(); font = static
                else:
                    static.close()
            options = subset.Options()
            options.name_IDs = ['*']
            options.name_legacy = True
            options.name_languages = ['*']
            options.layout_features = ['*']
            worker = subset.Subsetter(options=options)
            worker.populate(unicodes=chars)
            worker.subset(font)
            if 'fvar' in font:
                axes = {a.axisTag:a.defaultValue for a in font['fvar'].axes}
                axes['wght'] = float(face['weight'])
                font = instancer.instantiateVariableFont(font,axes,updateFontNames=False)
                family_tool.name_static_instance(font,face['family'],int(face['weight']))
            font.save(project/face['file'])
            font.close()
        for record in family['fonts']:
            if record.get('license'):
                notice=ROOT/'families/licenses'/record['license']
                shutil.copy2(notice,target_dir/notice.name)
        manifest.write_text(json.dumps({'signature':signature,'note':'Static source faces subset to this exact specimen corpus; regenerate after changing text.'},indent=2)+'\n')
    return fonts


def build(project, font_cache=None):
    raw = (SHOWCASE/'catalog.js').read_text()
    catalog = json.loads(raw.split('window.FOLIO_CATALOG = ',1)[1].strip().removesuffix(';'))
    # `variations` and `expressions` are one chapter; never emit two dividers with
    # the same Chinese name if a recipe was filed under the CSS layer name.
    entries = []
    for section in SECTIONS:
        target = 'expressions' if section=='variations' else section
        entries.extend((target, entry) for entry in catalog.get(section, []))
    ids = [e['id'] for _,e in entries]
    if len(ids)!=len(set(ids)):
        raise ValueError('Catalog IDs must be globally unique')
    project.mkdir(parents=True,exist_ok=True)
    if not (project/'sources').exists():
        (project/'sources').mkdir()
    pages, mapping, assets, segments = [], {}, {}, []

    def add_page(node, ident):
        add_class(node, 'page')
        node.attrs['data-page-id'] = ident
        node.attrs['id'] = ident
        pages.append(node)
        segments.extend(annotate(node, ident))
        return len(pages)

    cover = Fragment('<section class="page fl-type-light"><div class="fl-area specimen-area"><p class="fl-kicker">FOLIO / COMPLETE SPECIMEN</p><h1 class="fl-display specimen-cover-title" data-outline="1">秩序与自由。<br>全部能力，<br>在纸面上展开。</h1><p class="fl-lead fl-mt-5">Swiss 结构 · Bold / Light 排印 · 数字同族</p><div class="specimen-cover-copy"><p class="fl-body">本册从交互展示的同一份目录生成。每个原子、布局、组件与表现配方都有可查找的页码；摄影、文字与企业信息共享一套底层。</p><p class="fl-key fl-mt-3">内容与经营数字为演示样本。照片保留登记来源，不代表本项目实拍。完整覆盖见 coverage.json。</p></div></div></section>').root.children[0]
    cover.children[0].children.append(footer(1,f'FOLIO {catalog.get("version","")} / {len(entries)} ENTRIES'))
    add_page(cover,'specimen-cover')

    for group in SECTIONS:
        group_entries = [e for g,e in entries if g==group]
        if not group_entries:
            continue
        divider = Fragment(f'<section class="page fl-type-bold"><div class="fl-area specimen-area"><p class="fl-kicker">{html.escape(group.upper())}</p><h1 class="fl-display specimen-section-no" data-outline="1">{html.escape(NAMES[group])}</h1><p class="fl-lead fl-mt-4">{len(group_entries)} 个目录项。每个例子保留真实字号与构图关系。</p><div class="specimen-index-anchor fl-mt-6"></div></div></section>').root.children[0]
        # Index pages hold up to 24 items; a section that overflows is split evenly so
        # a continuation page never carries a near-empty remainder.
        per_page = 24
        count = max(1, -(-len(group_entries) // per_page))
        chunks = [group_entries[round(i * len(group_entries) / count):round((i + 1) * len(group_entries) / count)] for i in range(count)]
        for index, chunk in enumerate(chunks):
            idx_page = divider if index == 0 else Fragment(f'<section class="page fl-type-light"><div class="fl-area specimen-area"><p class="fl-kicker">{html.escape(group.upper())}</p><h1 class="fl-h1">{html.escape(NAMES[group])} / 续</h1><div class="specimen-index-anchor fl-mt-5"></div></div></section>').root.children[0]
            anchor = next(n for n in idx_page.walk() if 'specimen-index-anchor' in n.classes)
            ul = Node('ol',{'class':'specimen-index'})
            for entry in chunk:
                ul.children.append(Node('li',{},[element('span',entry['title'],'fl-key'),element('span',entry['id'],'fl-caption')]))
            anchor.children.append(ul)
            idx_page.children[0].children.append(footer(len(pages)+1,NAMES[group]))
            add_page(idx_page,f'index-{group}-{index+1}')
        for entry in group_entries:
            entry_id=entry['id']
            fragment=Fragment(entry['html']).root
            image_ids=localize(fragment,project,entry_id,assets)
            native=[n for n in fragment.walk() if 'page' in n.classes]
            page_numbers=[]
            if native:
                if len(native)==2 and len(pages)%2==0:
                    # The first native spread page must be an even-numbered left page.
                    spacer=Fragment('<section class="page fl-type-light"><div class="fl-area specimen-area"><p class="fl-kicker">面对页 / SPREAD</p><h1 class="fl-display specimen-section-no">接下来，<br>展开一幅景观。</h1><p class="fl-body fl-mt-5">两页共用同一图像坐标；裁切后的左右画面连续，文字避开中缝。</p></div></section>').root.children[0]
                    spacer.children[0].children.append(footer(len(pages)+1))
                    add_page(spacer,entry_id+'-lead-in')
                for i,node in enumerate(native):
                    for key in ('width','height','position','--trim-w','--trim-h','--media-w','--media-h','--bleed'):
                        set_style(node,**{key:None})
                    add_class(node,'fl-type-light')
                    if len(native)==2:
                        node.attrs['data-side']='left' if i==0 else 'right'
                        node.attrs['data-spread']=entry_id
                        set_style(node,**{'--fl-panorama-top':'0mm','--fl-panorama-height':'200mm','--fl-focus-x':'50%','--fl-focus-y':'50%'})
                        for child in node.walk():
                            if 'fl-area' in child.classes:
                                set_style(child,top='215mm')
                    else:
                        node.attrs.pop('data-spread',None)
                        node.attrs.pop('data-side',None)
                    # Precisely authorize the photographic reading relationship only.
                    for child in node.walk():
                        if any(c in child.classes for c in ('fl-l-copy','fl-l-caption')) and image_ids:
                            child.attrs['data-overlap']=' '.join(image_ids)
                    meta_attrs={'class':'specimen-native-meta'}
                    # Only declare an overlap when there is an actual image target; an
                    # empty data-overlap fails contract validation on text/colour pages.
                    if image_ids:
                        meta_attrs['data-overlap']=' '.join(image_ids)
                    meta=Node('div',meta_attrs,[element('span',entry['title']+' / '+entry_id,'fl-caption'),element('span',f'{len(pages)+1:03}','fl-caption fl-font-number')])
                    node.children.append(meta)
                    ident=f'{entry_id}-{i+1}' if len(native)>1 else entry_id
                    page_numbers.append(add_page(node,ident))
            else:
                heading,notes=metadata(entry,group)
                area=Node('div',{'class':'fl-area specimen-area'},[heading,Node('div',{'class':'specimen-example'},fragment.children),notes,footer(len(pages)+1)])
                node=Node('section',{'class':'page fl-type-'+('bold' if len(pages)%3==0 else 'light')},[area])
                page_numbers.append(add_page(node,entry_id))
            mapping[entry_id]={'section':group,'title':entry['title'],'pages':page_numbers,'page_ids':[pages[p-1].attrs['data-page-id'] for p in page_numbers],'source_sha256':hashlib.sha256(entry['html'].encode()).hexdigest()}

    document='<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8"><title>Folio 完整设计系统样刊</title></head><body>\n'+'\n'.join(p.serialize() for p in pages)+'\n</body></html>\n'
    (project/'book.html').write_text(document)
    (project/'book.css').write_text(BOOK_CSS)
    shutil.copy2(ROOT/'families/folio/folio.css',project/'design.css')
    corpus='\n'.join(s['text'] for s in segments)
    fonts=prepare_fonts(project,corpus,font_cache)
    family=json.loads((ROOT/'families/folio/family.json').read_text())
    meta={'contract':1,'title':'Folio 完整设计系统样刊 · 秩序与自由','entry':'book.html','styles':['design.css','book.css'],'languages':['zh-CN'],'default_language':'zh-CN','canvas':family['canvas'],'binding':'digital','first_page':'right','content_mode':'carry','fonts':fonts,'family':{'name':'folio','version':family['version'],'sha256':hashlib.sha256((project/'design.css').read_bytes()).hexdigest()}}
    (project/'project.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    (project/'coverage.json').write_text(json.dumps({'catalog_version':catalog.get('version'),'catalog_sha256':hashlib.sha256(raw.encode()).hexdigest(),'entries':len(entries),'page_count':len(pages),'mapping':mapping},ensure_ascii=False,indent=2)+'\n')
    write_specimen_index(json.loads((project/'coverage.json').read_text()))
    page_map={ident:{'id':entry['page_ids'][0],'page':entry['pages'][0],'label':entry['title']} for ident,entry in mapping.items()}
    (SHOWCASE/'specimen-map.js').write_text('// Generated coverage locations only; not a PDF approval record.\nwindow.FOLIO_SPECIMEN = '+json.dumps(page_map,ensure_ascii=False,indent=2)+';\n')
    (project/'sources/segments.json').write_text(json.dumps({'contract':1,'source':'source.md','segments':segments},ensure_ascii=False,indent=2)+'\n')
    (project/'sources/source.md').write_text('# Folio 完整样刊 / 目录文案\n\n由本仓展示目录生成。经营、行程和分析内容均为示例，不代表真实机构业绩或已核验计划。\n\n'+'\n\n'.join(f'<!-- {s["id"]} -->\n{s["text"]}' for s in segments)+'\n')
    (project/'sources/assets.json').write_text(json.dumps({'contract':1,'assets':assets},ensure_ascii=False,indent=2)+'\n')
    (project/'sources/chart-data.json').write_text(json.dumps({e['id']:e['data'] for _,e in entries if 'data' in e},ensure_ascii=False,indent=2)+'\n')
    (project/'brief.md').write_text('# 完整样刊任务\n\n展示本仓 Folio CSS 的全部目录能力，页数由覆盖范围决定。与 dev/folio-css/index.html 共用 catalog.js；不维护第二份例子，不缩放整页或偷偷缩字。每项通过 coverage.json 映射到真实页码。文字、图表数值、行程与经营内容为演示创作。所有资源均在项目内冻结。\n\n字体采用本机已准备好的开源静态字面（Noto Serif SC / Noto Sans SC / Inter，OFL）并按样刊字符集子集化。生成不等于通过技术或视觉验收。\n')
    (project/'page-plan.md').write_text('# 页序与覆盖\n\n依次为原子与规则、布局关系、内容组件、表现与变奏。普通配方一项一页；出血页面提升为真实物理页；全景为左右相邻两页。章节索引允许显式续页。全部目录映射见 coverage.json。\n')
    (project/'README.md').write_text('# Folio 完整设计系统样刊\n\n此目录由 `python3 dev/folio-css/build-specimen.py` 根据交互展示的同一份目录生成。修改配方请编辑 dev/folio-css 中的源 JSON，先运行 dev/build-folio-css.py，再重建本册。作者源为 book.html 与 book.css，家族 CSS 与字体已冻结；coverage.json 映射每一目录项到书页。表现与变奏章先有 philosophy-variations.md 的视觉主张（受控变量），再逐页落版；主张只管判断标准，不定尺寸与模数。主张不进成品，留在项目目录，供改版时对照。\n\n构建完后依次执行 validate、check、实际看全部最终 PDF、review，再更新展示预览。生成器不写任何通过或视觉批准声明。\n')
    print(f'Built {project.relative_to(ROOT) if project.is_relative_to(ROOT) else project}: {len(entries)} entries → {len(pages)} pages, {len(segments)} text segments, {len(assets)} images')


def write_specimen_index(coverage):
    """Publish a readable map of every catalog item without rebuilding book sources."""
    lines = ['# Folio 2.2 完整样刊目录', '',
             f"{coverage['entries']} 个展示条目，对应 {coverage['page_count']} 页 A4 样刊。",
             '原子部分索引全部公开类及其刻度，例子演示典型组合；不代表穷举所有排列。', '',
             '[交互展示](index.html) · [翻看完整样刊](../samples/native/folio-swiss/preview.html) · [机器可读覆盖表](../samples/native/folio-swiss/coverage.json)', '']
    for section in SECTIONS:
        items = [entry for entry in coverage['mapping'].values() if entry['section'] == section]
        if not items:
            continue
        lines += [f'## {NAMES[section]}', '', '| 页码 | 示例 |', '|---|---|']
        for entry in items:
            pages = '–'.join(map(str, entry['pages']))
            title = entry['title'].replace('|', ' / ')
            lines.append(f"| {pages} | [{title}](../samples/native/folio-swiss/preview.html#{entry['page_ids'][0]}) |")
        lines.append('')
    lines += ['历史版本的构图对照见 [1.1 样册页序](specimen-map.md)。', '']
    (SHOWCASE / 'specimen-index.md').write_text('\n'.join(lines))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,default=DEFAULT_PROJECT)
    parser.add_argument('--font-cache',type=Path,help='Existing native project with all current static font faces; default reuses local typography smoke-test project when available')
    args=parser.parse_args()
    build(args.project.resolve(),args.font_cache)


if __name__=='__main__':
    main()

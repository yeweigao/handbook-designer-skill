"""Optional, monochrome brand artwork. Geometry stays in a project SVG, not the engine."""
from pathlib import Path
from html import escape
import math
import xml.etree.ElementTree as ET

ET.register_namespace('', 'http://www.w3.org/2000/svg')
ALLOWED = {'svg', 'g', 'path', 'polygon', 'polyline', 'rect', 'line', 'circle', 'ellipse'}


def numbers(value, size, name):
    if not isinstance(value, (list, tuple)) or len(value) != size:
        raise ValueError('brand_graphic.' + name + ' needs ' + str(size) + ' numbers')
    out = [float(x) for x in value]
    if not all(math.isfinite(x) for x in out):
        raise ValueError('brand_graphic.' + name + ' must be finite')
    return out


def validate_spreads(records, width):
    """Validate the effective pair after every physical page has been rendered."""
    errors = []
    for n, item in records.items():
        side = item['spread']
        if not side:
            continue
        mate = n + 1 if side == 'left' else n - 1
        other = records.get(mate)
        if not other or other['spread'] != ('right' if side == 'left' else 'left'):
            errors.append(f'第{n}页 brand_graphic 共享跨页缺少第{mate}页配对 → 两页分别写 spread: left/right，独立构图则删除 spread')
            continue
        if side == 'right':
            continue
        a, b = item['matrix'], other['matrix']
        same = (item['variant'] == other['variant'] and item['opacity'] == other['opacity']
                and all(math.isclose(a[i], b[i], rel_tol=0, abs_tol=1e-7) for i in (0, 1, 2, 3, 5))
                and math.isclose(a[4] - b[4], width, rel_tol=0, abs_tol=1e-7))
        if not same:
            errors.append(f'第{n}–{mate}页 brand_graphic 共享变换不一致 → 两页使用相同 variant/view/frame/angle/opacity，右页由引擎平移一页宽')
    return errors


def render(n, page, book, project, width, height, color, records=None):
    spec = book.get('brand_graphic')
    choice = page.get('brand_graphic')
    if not spec or choice in (None, False):
        return ''
    if isinstance(choice, str):
        choice = {'variant': choice}
    name = choice.get('variant')
    variants = spec.get('variants', {})
    if name not in variants:
        raise ValueError('brand_graphic unknown variant: ' + str(name))
    q = dict(variants[name], **choice)
    relative = Path(spec['file'])
    path = (Path(project) / relative).resolve()
    # subset/i18n deliberately share the configured photos directory with their source project.
    roots = (Path(project).resolve(), (Path(project) / book.get('photos', 'photos')).resolve())
    if relative.is_absolute() or '..' in relative.parts or not any(path.is_relative_to(root) for root in roots):
        raise ValueError('brand_graphic SVG must be relative to the project or its configured photos directory')
    root = ET.fromstring(path.read_text(encoding='utf-8'))
    # This layer accepts geometric paths only; no scripts, foreign objects or external references.
    for node in root.iter():
        if node.tag.split('}')[-1] not in ALLOWED:
            raise ValueError('brand_graphic SVG contains a non-geometric element')
        for key in node.attrib:
            if key.lower().startswith('on') or key in ('style', 'href') or 'href' in key:
                raise ValueError('brand_graphic SVG contains an active or external attribute')
        for key in ('fill', 'stroke'):
            if key in node.attrib and node.attrib[key] != 'none':
                node.attrib[key] = 'currentColor'
    view = numbers(q.get('view', [float(v) for v in root.attrib['viewBox'].split()]), 4, 'view')
    frame = numbers(q.get('frame', [0, 0, 1, 1]), 4, 'frame')
    if min(view[2:]) <= 0 or min(frame[2:]) <= 0:
        raise ValueError('brand_graphic view/frame width and height must be positive')
    opacity = float(q.get('opacity', spec.get('opacity', .05)))
    angle = float(q.get('angle', 0))
    if not math.isfinite(opacity) or not 0 <= opacity <= 1 or not math.isfinite(angle):
        raise ValueError('brand_graphic opacity must be 0–1 and angle finite')
    spread = q.get('spread')
    if spread not in (None, 'left', 'right'):
        raise ValueError('brand_graphic.spread must be left or right')
    if (spread == 'left' and n % 2 != 0) or (spread == 'right' and (n % 2 != 1 or n < 3)):
        raise ValueError('brand_graphic spread must use an even left page and the following odd right page')
    canvas_width = width * (2 if spread else 1)
    x, y, w, h = [frame[i] * (canvas_width if i % 2 == 0 else height) for i in range(4)]
    # Focus/placement is an affine transform of the COMPLETE source, never a nested SVG crop.
    scale = max(w / view[2], h / view[3])
    tx = x + (w - scale * view[2]) / 2 - scale * view[0]
    ty = y + (h - scale * view[3]) / 2 - scale * view[1]
    cx, cy = x + w / 2, y + h / 2
    co, si = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    co = 0 if abs(co) < 1e-12 else co
    si = 0 if abs(si) < 1e-12 else si
    matrix = [scale * co, scale * si, -scale * si, scale * co,
              cx + co * (tx - cx) - si * (ty - cy) - (width if spread == 'right' else 0),
              cy + si * (tx - cx) + co * (ty - cy)]
    transform = 'matrix(' + ' '.join(f'{v:.10g}' for v in matrix) + ')'
    children = ''.join(ET.tostring(child, encoding='unicode') for child in root)
    # Group opacity prevents intersections becoming darker through repeated alpha compositing.
    over_image = '1' if q.get('over_image', False) else '0'
    z_index = 3 if over_image == '1' else 1
    stroke_width = float(root.attrib.get('stroke-width', 1))
    if not math.isfinite(stroke_width) or stroke_width < 0:
        raise ValueError('brand_graphic stroke width must be finite and non-negative')
    if records is not None:
        records[n] = dict(spread=spread, matrix=matrix, opacity=opacity, variant=name)
    return (f'<svg class="cn-brand-graphic deco" data-deco="1" aria-hidden="true" '
            f'data-variant="{escape(str(name), quote=True)}" data-spread="{spread or ""}" data-over-image="{over_image}" viewBox="0 0 {width} {height}" '
            f'xmlns="http://www.w3.org/2000/svg" style="position:absolute;inset:0;width:{width}px;height:{height}px;'
            f'z-index:{z_index};pointer-events:none;color:{color}">'
            f'<defs><mask id="brand-mask-{n}" maskUnits="userSpaceOnUse" x="0" y="0" width="{width}" height="{height}">'
            f'<rect width="{width}" height="{height}" fill="white"/></mask></defs>'
            f'<g mask="url(#brand-mask-{n})"><g class="cn-brand-ink" opacity="{opacity}" '
            f'transform="{transform}" fill="none" stroke="currentColor" '
            f'stroke-width="{stroke_width}">{children}</g></g></svg>')

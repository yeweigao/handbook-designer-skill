"""Small, deterministic SVG charts for print. Python standard library only.

Authoring helper, not a runtime layout registry. Values remain in source JSON;
call render_chart(spec) or `python3 hb/core/charts.py input.json -o chart.svg`.
Charts use real text and Folio colour roles; include units, source, period and
sample/actual status in the surrounding figure caption. Minimum width is 600px.
"""
import argparse
import html
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def number(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise ValueError("Chart values must be finite numbers, not booleans")
    return float(v)


def render_chart(spec):
    if not isinstance(spec, dict):
        raise ValueError("Chart specification must be an object")
    kind = spec.get("type")
    if kind not in ("bar", "line", "stacked", "waterfall"):
        raise ValueError("type must be bar, line, stacked or waterfall")
    width = number(spec.get("width", 640))
    height = number(spec.get("height", 340))
    if not 600 <= width <= 1600 or not 280 <= height <= 1200:
        raise ValueError("Use width 600–1600 and height 280–1200; do not shrink label text")
    ident = str(spec.get("id", "chart"))
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", ident):
        raise ValueError("id must be an SVG-safe unique identifier")
    title = spec.get("title", "Chart")
    precision = spec.get("precision", 0)
    if isinstance(precision, bool) or not isinstance(precision, int) or not 0 <= precision <= 4:
        raise ValueError("precision must be 0–4")
    esc = lambda value: html.escape(str(value), quote=True)
    fmt = lambda value: f"{value:,.{precision}f}"
    ink = "var(--fl-text,#202B32)"
    muted = "var(--fl-text-muted,#56616A)"
    accent = "var(--fl-text-accent,#164BE8)"
    stroke = "var(--fl-stroke,#B7BEC6)"
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height:g}" width="{width:g}" height="{height:g}" role="img" aria-labelledby="{ident}-title" style="display:block;max-width:100%;height:auto;font-family:var(--fl-font-body, sans-serif);font-size:14px">',
             f'<title id="{ident}-title">{esc(title)}</title>']

    def text(x, y, value, anchor="start", color=ink, weight=400):
        parts.append(f'<text x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}" fill="{color}" font-size="14" font-weight="{weight}" data-role="key">{esc(value)}</text>')

    def line(x1, y1, x2, y2, color=stroke, dash=False):
        parts.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{color}" stroke-width="1"' + (' stroke-dasharray="4 4"' if dash else '') + '/>')

    def rect(x, y, w, h, color, **data):
        attrs = ' '.join(f'data-{k.replace("_", "-")}="{v:g}"' for k, v in data.items())
        parts.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{max(0,w):.3f}" height="{max(0,h):.3f}" fill="{color}" {attrs}/>')

    def labels_values():
        labels = spec.get("labels", [])
        if not isinstance(labels, list) or not labels or any(not isinstance(s, str) or not s.strip() for s in labels):
            raise ValueError("labels must be a nonempty list of nonempty strings")
        return labels

    def values(v, size):
        if not isinstance(v, list) or len(v) != size:
            raise ValueError("Every values list must match labels length")
        return [number(x) for x in v]

    if kind == "bar":
        labels = labels_values()
        vals = values(spec.get("values"), len(labels))
        if len(labels) > 9 or height < 38 * len(labels) + 62:
            raise ValueError("Too many bars for readable labels; increase chart height")
        lo, hi = min(0, *vals), max(0, *vals)
        if not math.isfinite(hi - lo):
            raise ValueError("Numeric range overflow; express values in a larger unit")
        if lo == hi:
            hi = 1
        left, right, top, bottom = 128, width - 68, 24, height - 40
        x = lambda v: left + (v - lo) / (hi - lo) * (right - left)
        line(x(0), top - 10, x(0), bottom + 7, muted)
        step = (bottom - top) / len(vals)
        highlight = spec.get("highlight", 0)
        if isinstance(highlight, bool) or not isinstance(highlight, int) or not 0 <= highlight < len(vals):
            raise ValueError("highlight must be an existing bar index")
        for i, (label, value) in enumerate(zip(labels, vals)):
            y = top + step * i
            text(0, y + step * .52, label)
            rect(min(x(0), x(value)), y + 2, abs(x(value) - x(0)), step * .66,
                 accent if i == highlight else muted, value=value, zero=x(0))
            text(x(value) + (8 if value >= 0 else -8), y + step * .52, fmt(value), "start" if value >= 0 else "end")
        text(x(0), height - 8, "0", "middle", muted)
    elif kind in ("line", "stacked"):
        labels = labels_values()
        series = spec.get("series", [])
        if not isinstance(series, list) or not 1 <= len(series) <= 3:
            raise ValueError("Use one to three series for legible direct labels")
        if any(not isinstance(s, dict) for s in series):
            raise ValueError("Every series must be an object")
        data = [values(s.get("values"), len(labels)) for s in series]
        if any(not isinstance(s.get("name"), str) or not s["name"].strip() for s in series):
            raise ValueError("Every series requires a name")
        if len(labels) > 8:
            raise ValueError("Use at most eight category labels; choose a larger or separate chart")
        colors = [accent, muted, ink]
        left, right, top, bottom = 58, width - 74, 55, height - 52
        if kind == "line":
            if len(labels) < 2:
                raise ValueError("A line needs at least two observations")
            lo, hi = min(0, *sum(data, [])), max(0, *sum(data, []))
            if lo == hi:
                hi = lo + 1
            if "range" in spec:
                limits = values(spec["range"], 2)
                lo, hi = limits
                if lo >= hi or any(v < lo or v > hi for v in sum(data, [])):
                    raise ValueError("Explicit range must increase and include every value")
            if not math.isfinite(hi - lo):
                raise ValueError("Numeric range overflow; express values in a larger unit")
            y = lambda v: bottom - (v - lo) / (hi - lo) * (bottom - top)
            x = lambda i: left + i / (len(labels) - 1) * (right - left)
            for value in (lo, (lo + hi) / 2, hi):
                line(left, y(value), right, y(value))
                text(left - 10, y(value) + 5, fmt(value), "end", muted)
            for i, label in enumerate(labels):
                text(x(i), height - 19, label, "middle", muted)
            for s, vals in enumerate(data):
                text(left + s * 180, 21, series[s]["name"], color=colors[s], weight=700)
                points = ' '.join(f'{x(i):.3f},{y(v):.3f}' for i, v in enumerate(vals))
                parts.append(f'<polyline points="{points}" fill="none" stroke="{colors[s]}" stroke-width="2.5"' + (' stroke-dasharray="6 4"' if s else '') + '/>')
                for i, v in enumerate(vals):
                    parts.append(f'<circle cx="{x(i):.3f}" cy="{y(v):.3f}" r="3.5" fill="{colors[s]}"/>')
                text(right + 9, y(vals[-1]) + 5, fmt(vals[-1]), color=colors[s])
        else:
            if height < len(labels) * 48 + 100:
                raise ValueError("Increase stacked chart height to keep rows readable")
            if any(v < 0 for v in sum(data, [])):
                raise ValueError("Stacked values must be nonnegative")
            totals = [sum(vals[i] for vals in data) for i in range(len(labels))]
            if any(not math.isfinite(v) for v in totals):
                raise ValueError("Stack total overflow; express values in a larger unit")
            percent = spec.get("percent", True)
            if not isinstance(percent, bool):
                raise ValueError("percent must be a boolean")
            if percent and any(not math.isclose(v, 100, abs_tol=1e-7) for v in totals):
                raise ValueError("Each percent stack must total 100; inputs are not silently normalized")
            scale = max(totals) or 1
            left = 90
            for s in range(len(series)):
                text(left + s * 170, 20, series[s]["name"], color=colors[s], weight=700)
            step = (bottom - top) / len(labels)
            for i, label in enumerate(labels):
                text(0, top + i * step + 23, label)
                offset = 0
                for s, vals in enumerate(data):
                    barw = vals[i] / scale * (right - left)
                    rect(left + offset, top + i * step, barw, 29, colors[s], value=vals[i])
                    # Values stay below the bar, never on a low-contrast fill.
                    if barw >= 35:
                        text(left + offset + barw / 2, top + i * step + 47, fmt(vals[i]) + ('%' if percent else ''), "middle")
                    elif vals[i] != 0:
                        raise ValueError("Segment too small for a direct label; use a table or combine categories explicitly")
                    offset += barw
                text(right + 10, top + i * step + 23, fmt(totals[i]) + ('%' if percent else ''))
    else:
        start = number(spec.get("start"))
        changes = spec.get("changes", [])
        if not isinstance(changes, list) or not 1 <= len(changes) <= 6:
            raise ValueError("Waterfall needs one to six changes")
        total = start
        bars = [(str(spec.get("start_label", "Start")), 0., start, start, True)]
        for change in changes:
            if not isinstance(change, dict):
                raise ValueError("Each change must be an object")
            if not isinstance(change.get("label"), str) or not change["label"].strip():
                raise ValueError("Each change requires a label")
            value = number(change.get("value"))
            nxt = total + value
            if not math.isfinite(nxt):
                raise ValueError("Cumulative total overflow")
            bars.append((change["label"], total, nxt, value, False))
            total = nxt
        if "expected_total" in spec and not math.isclose(total, number(spec["expected_total"]), abs_tol=1e-8, rel_tol=1e-9):
            raise ValueError(f"Waterfall does not close: computed {total:g}")
        bars.append((str(spec.get("end_label", "End")), 0., total, total, True))
        lo = min(0, *(min(b[1], b[2]) for b in bars))
        hi = max(0, *(max(b[1], b[2]) for b in bars))
        if not math.isfinite(hi - lo):
            raise ValueError("Numeric range overflow; express values in a larger unit")
        if lo == hi:
            hi = 1
        left, right, top, bottom = 48, width - 22, 40, height - 51
        y = lambda v: bottom - (v - lo) / (hi - lo) * (bottom - top)
        step = (right - left) / len(bars)
        bw = step * .57
        line(left - 10, y(0), right, y(0), muted)
        text(left - 15, y(0) + 5, "0", "end", muted)
        for i, (label, begin, end, value, is_total) in enumerate(bars):
            x = left + step * i
            rect(x, y(max(begin, end)), bw, abs(y(end) - y(begin)), ink if is_total else (accent if value >= 0 else muted), start=begin, end=end, value=value)
            text(x + bw / 2, y(max(begin, end)) - 10, ("+" if value > 0 and not is_total else "") + fmt(value), "middle", weight=700 if is_total else 400)
            text(x + bw / 2, height - 19, label, "middle")
            if i < len(bars) - 1:
                line(x + bw, y(end), left + step * (i + 1), y(end), dash=True)
    parts.append('</svg>')
    return '\n'.join(parts)


def render_figure(spec):
    """Auditable HTML figure: SVG geometry plus positioned ordinary text.

    The native print auditor measures HTML text. Keep labels as first-class HTML
    content instead of accepting unverified SVG text; use render_chart for a
    standalone vector asset. This wrapper has a fixed authored size: do not scale
    it down to make a chart fit. Its labels remain editable and selectable.
    """
    root = ET.fromstring(render_chart(spec))
    ns = '{http://www.w3.org/2000/svg}'
    labels = []
    for node in list(root):
        if node.tag == ns + 'title':
            root.remove(node)
        elif node.tag == ns + 'text':
            a = node.attrib
            anchor = a.get('text-anchor', 'start')
            shift = {'start': '0', 'middle': '-50%', 'end': '-100%'}[anchor]
            style = (f'position:absolute;left:{a["x"]}px;top:{float(a["y"])-16:g}px;'
                     f'transform:translateX({shift});margin:0;white-space:nowrap;'
                     f'font-size:14px;line-height:22px;font-weight:{a.get("font-weight",400)};'
                     f'color:{a["fill"]}')
            labels.append(f'<p data-role="key" style="{style}">{html.escape(node.text or "")}</p>')
            root.remove(node)
    root.attrib.pop('aria-labelledby', None)
    root.attrib.pop('role', None)
    root.set('aria-hidden', 'true')
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    svg = ET.tostring(root, encoding='unicode')
    return (f'<div style="position:relative;width:{root.attrib["width"]}px;height:{root.attrib["height"]}px;'
            'font-family:var(--fl-font-body);font-weight:400">' + svg + ''.join(labels) + '</div>')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    try:
        svg = render_chart(json.loads(args.input.read_text(encoding="utf-8")))
    except (ValueError, TypeError, KeyError) as exc:
        parser.exit(2, f"Invalid chart: {exc}\n")
    if args.output:
        args.output.write_text(svg + '\n', encoding="utf-8")
    else:
        print(svg)

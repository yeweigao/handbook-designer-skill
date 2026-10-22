#!/usr/bin/env python3
"""版面适配回归（adapt.yaml）：声明过的去编号前缀 / 不进册子的段落不算 MISSING，没声明的照旧报；
声明写错、没命中、或前缀仍印在成品里要报出来；plan.py 能把「亮点一：」「备注：」这类候选报给人。
纯文本，不需要浏览器和图片库。"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HB = Path(__file__).resolve().parents[2] / 'hb'
DOC = """# 学校介绍

### 亮点一：高端品质
全程五星级住宿，专业导师陪同。

### 亮点二：小班教学
每班不超过十二人，导师一对一点评。

### 亮点三：名校对接
与三所海外名校建立合作关系。

备注：此页最终稿待校长确认后再定。

时间：每周六上午九点
"""
BOOK = """<html><body>
<section class="page" data-n="1"><h1>学校介绍</h1><h2>高端品质</h2><p>全程五星级住宿，专业导师陪同。</p>
<h2>小班教学</h2><p>每班不超过十二人，导师一对一点评。</p></section>
<section class="page" data-n="2"><h2>名校对接</h2><p>与三所海外名校建立合作关系。</p><p>时间：每周六上午九点</p></section>
</body></html>"""
ADAPT = """strip:
  - match: '^(亮点|特色)[一二三四五六七八九十\\d]+[：:]\\s*'
    why: 宣传册里编号没意义，只留冒号后的标题
omit:
  - text: '备注：此页最终稿待校长确认'
    why: 文档内部备注
"""


def check(project):
    r = subprocess.run([sys.executable, str(HB / 'check_copy.py'), str(project)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def count(out, key):
    m = re.search(rf'^{key} (\d+)', out, re.M)
    return int(m.group(1)) if m else None


def main():
    fails = []

    def expect(cond, msg):
        if not cond:
            fails.append(msg)

    with tempfile.TemporaryDirectory(prefix='hb-adapt-') as td:
        P = Path(td)
        (P / 'doc.md').write_text(DOC, encoding='utf-8')
        (P / 'book.html').write_text(BOOK, encoding='utf-8')

        # 1. 没有 adapt.yaml：前缀和备注都算缺字（不声明就不敢省）
        rc, out = check(P)
        expect(rc == 1 and (count(out, 'MISSING') or 0) >= 4, f'无 adapt.yaml 应报缺字，实际 rc={rc}\n{out}')

        # 2. 声明之后：不缺字，报告写出来，三行前缀 + 一行备注都在里面
        (P / 'adapt.yaml').write_text(ADAPT, encoding='utf-8')
        rc, out = check(P)
        expect(rc == 0 and count(out, 'MISSING') == 0, f'声明后应不缺字，实际 rc={rc}\n{out}')
        expect('ADAPT strip 3 omit 1' in out, f'应统计去前缀 3 行、省略 1 行\n{out}')
        expect('ADAPT WARN' not in out, f'命中且成品里没有前缀，不该有警告\n{out}')
        rep = (P / '.qa' / 'adapt-report.md')
        expect(rep.exists(), '应写出 .qa/adapt-report.md')
        if rep.exists():
            t = rep.read_text(encoding='utf-8')
            expect('亮点一：高端品质' in t and '高端品质' in t and '备注：此页最终稿待校长确认' in t, '报告要列出原文、成品采用、被省略的行')

        # 3. 「时间：…」这种 标签:值 不会被误剥（还得照原文印出来），成品少了它就是缺字
        (P / 'book.html').write_text(BOOK.replace('<p>时间：每周六上午九点</p>', ''), encoding='utf-8')
        rc, out = check(P)
        expect(rc == 1 and count(out, 'MISSING') == 1, f'标签:值没声明就不能省，应只缺 1 处\n{out}')
        (P / 'book.html').write_text(BOOK, encoding='utf-8')

        # 4. 成品里还印着声明要去掉的前缀 → 警告（不阻塞）
        (P / 'book.html').write_text(BOOK.replace('<h2>高端品质</h2>', '<h2>亮点一：高端品质</h2>'), encoding='utf-8')
        rc, out = check(P)
        expect('ADAPT WARN' in out and '亮点一：高端品质' in out, f'前缀仍印在成品里应警告\n{out}')
        (P / 'book.html').write_text(BOOK, encoding='utf-8')

        # 5. 声明了但没命中 → 警告（多半是正则写错）
        y = ADAPT.replace('omit:', "  - match: '^要点\\d+：'\n    why: 没有这种行\nomit:")
        (P / 'adapt.yaml').write_text(y, encoding='utf-8')
        rc, out = check(P)
        expect(rc == 0 and 'ADAPT WARN' in out and '要点' in out, f'没命中的 strip 应警告但不阻塞\n{out}')

        # 6. 格式错误 / omit 太短 → 硬错误
        (P / 'adapt.yaml').write_text('strip:\n  - why: 没写 match\n', encoding='utf-8')
        rc, out = check(P)
        expect(rc == 1 and 'ADAPT ERROR' in out, f'缺 match 应报 ADAPT ERROR\n{out}')
        (P / 'adapt.yaml').write_text("omit:\n  - text: '备注'\n", encoding='utf-8')
        rc, out = check(P)
        expect(rc == 1 and 'ADAPT ERROR' in out, f'omit 的 text 太短应报 ADAPT ERROR\n{out}')

        # 7. 整行去掉后只剩前缀的行不剥（避免把标题剥空）
        (P / 'adapt.yaml').write_text("strip:\n  - match: '^亮点[一二三]：'\n", encoding='utf-8')
        (P / 'doc.md').write_text('# 学校介绍\n\n亮点一：\n', encoding='utf-8')
        (P / 'book.html').write_text('<html><body><section class="page" data-n="1"><h1>学校介绍</h1><p>亮点一：</p></section></body></html>', encoding='utf-8')
        rc, out = check(P)
        expect(rc == 0 and count(out, 'MISSING') == 0, f'剥完会变空的行应保持原样\n{out}')
        (P / 'doc.md').write_text(DOC, encoding='utf-8')

        # 7b. 后缀也能剥：标题末尾的版本标记（Word 文件名式标题）
        (P / 'adapt.yaml').write_text("strip:\n  - match: '\\s*[（(]终稿v\\d+[）)]\\s*$'\n    why: 版本标记不印\n", encoding='utf-8')
        (P / 'doc.md').write_text('# 招生简章（终稿v3）\n\n正文一段。\n', encoding='utf-8')
        (P / 'book.html').write_text('<html><body><section class="page" data-n="1"><h1>招生简章</h1><p>正文一段。</p></section></body></html>', encoding='utf-8')
        rc, out = check(P)
        expect(rc == 0 and 'ADAPT strip 1 omit 0' in out, f'标题末尾的版本标记应能剥掉\n{out}')
        (P / 'doc.md').write_text(DOC, encoding='utf-8')

    # 8. plan.py：把编号前缀、备注、版本标记当候选报给人
    with tempfile.TemporaryDirectory(prefix='hb-adapt-plan-') as td:
        P = Path(td)
        (P / 'doc.md').write_text('# 招生简章（终稿v3）\n\n' + DOC.split('\n', 2)[2] + '\n（插图建议：校园全景）\n', encoding='utf-8')
        r = subprocess.run([sys.executable, str(HB / 'plan.py'), str(P)], capture_output=True, text=True)
        plan = (P / 'plan.md').read_text(encoding='utf-8') if (P / 'plan.md').exists() else ''
        expect(r.returncode == 0 and plan, f'plan.py 应能跑完\n{r.stdout}{r.stderr}')
        expect('【编号标签前缀】' in plan and 'adapt.yaml' in plan, '应报编号标签前缀候选')
        expect('【疑似非读者内容】' in plan and '备注：此页最终稿' in plan, '应报备注类候选')
        expect('【标题带版本标记】' in plan, '应报标题里的版本标记')

    # 9. 读者要照着做的序号（步骤一、Day 3）不报
    with tempfile.TemporaryDirectory(prefix='hb-adapt-keep-') as td:
        P = Path(td)
        (P / 'doc.md').write_text('# 实验手册\n\n步骤一：准备材料\n\n步骤二：混合溶液\n\nDay 1：抵达营地\n\nDay 2：山地徒步\n', encoding='utf-8')
        subprocess.run([sys.executable, str(HB / 'plan.py'), str(P)], capture_output=True, text=True)
        plan = (P / 'plan.md').read_text(encoding='utf-8') if (P / 'plan.md').exists() else ''
        expect('【编号标签前缀】' not in plan, '步骤一/Day 1 是读者要用的序号，不该报')

    # 10. doctor：美化（frozen）不许带 adapt.yaml；普通路线放行；声明有误是硬伤，没命中只是提示
    def doctor(copy_txt, frozen):
        with tempfile.TemporaryDirectory(prefix='hb-adapt-doc-') as td:
            P = Path(td)
            (P / '.qa').mkdir()
            (P / '.qa' / 'copy.txt').write_text(copy_txt, encoding='utf-8')
            (P / 'book.yaml').write_text('book:\n  frozen: %s\n' % ('true' if frozen else 'false'), encoding='utf-8')
            r = subprocess.run([sys.executable, str(HB / 'doctor.py'), str(P)], capture_output=True, text=True)
            return r.returncode, r.stdout + r.stderr

    base = 'MISSING 0\nORDER 0\nEXTRA 0\n'
    rc, out = doctor(base + 'ADAPT strip 3 omit 1（说明）\n', True)
    expect(rc == 1 and 'adapt.yaml' in out and '改动了原文' in out, f'frozen 带 adapt.yaml 应被拦下\n{out}')
    rc, out = doctor(base + 'ADAPT strip 0 omit 0（说明）\n', True)
    expect(rc == 0, f'frozen 且 adapt.yaml 一条都没生效，不该拦\n{out}')
    rc, out = doctor(base + 'ADAPT strip 3 omit 1（说明）\n', False)
    expect(rc == 0 and 'GATE: PASS' in out, f'普通路线带 adapt.yaml 应放行\n{out}')
    rc, out = doctor('ADAPT ERROR: adapt.yaml 读不了\n', False)
    expect(rc == 1 and '适配声明有误' in out, f'ADAPT ERROR 应是硬伤\n{out}')
    rc, out = doctor(base + 'ADAPT strip 3 omit 1（说明）\nADAPT WARN: strip「^要点」没有命中任何一行\n', False)
    expect(rc == 0 and '[适配声明]' in out and '要点' in out, f'ADAPT WARN 只是提示，不拦门禁\n{out}')

    if fails:
        print('适配回归失败：')
        for f in fails:
            print(' -', f)
        raise SystemExit(1)
    print('适配回归通过')


if __name__ == '__main__':
    main()

// 续页工具（S6）：node hb/core/cli.mjs paginate <项目> [--flow <名称>]
// 对默认语言按实际排版把 data-flow 内容流分配到文字框（必要时生成续页），写回作者源 book.html，
// 并输出差异 .qa/paginate/book.html.diff 与报告 .qa/paginate/report.json。只移动内容，不改样式。
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { loadProject } from './project.mjs';
import { serve } from './server.mjs';
import { launch, openPage, waitResources } from './browser.mjs';
import { assemble, runValidate } from './render.mjs';
import { flowInPage } from './checks/flow.mjs';

export async function paginate(root, opts = {}) {
  const ctx = loadProject(root);
  const { dir, p } = ctx;
  runValidate(dir);
  const work = path.join(dir, '.build', 'paginate');
  fs.mkdirSync(work, { recursive: true });
  const assembled = path.join(work, '.assembled.html');
  fs.writeFileSync(assembled, assemble(ctx, p.default_language, work));
  const qa = path.join(dir, '.qa', 'paginate');
  fs.mkdirSync(qa, { recursive: true });
  const { browser } = await launch();
  const server = await serve(dir);
  const blocked = [];
  try {
    const { context, page } = await openPage(browser, server.origin, blocked);
    await page.emulateMedia({ media: 'print' });
    await page.goto(`${server.origin}/${path.relative(dir, assembled).split(path.sep).join('/')}`, { waitUntil: 'networkidle' });
    const res = await waitResources(page);
    if (res.fontFail.length || res.imgFail.length) throw new Error(`资源未就绪，无法测量：${[...res.fontFail, ...res.imgFail].join('、')}`);
    const report = await page.evaluate(flowInPage, { flow: opts.flow, firstPage: p.first_page });
    const pagesHtml = await page.evaluate(() => [...document.querySelectorAll('body > .page')].map((el) => el.outerHTML).join('\n'));
    await context.close();
    report.written = false;
    if (!report.errors.length) {
      const file = path.join(dir, p.entry);
      const before = fs.readFileSync(file, 'utf8');
      const after = before.replace(/(<body\b[^>]*>)[\s\S]*(<\/body>)/i, (m, a, b) => `${a}\n${pagesHtml}\n${b}`);
      if (after !== before) {
        const prev = path.join(work, 'book.before.html');
        fs.writeFileSync(prev, before);
        fs.writeFileSync(file, after);
        const d = spawnSync('diff', ['-u', '--label', `${p.entry}（续排前）`, '--label', `${p.entry}（续排后）`, prev, file], { encoding: 'utf8' });
        fs.writeFileSync(path.join(qa, 'book.html.diff'), d.stdout || '');
        report.written = true;
      }
    }
    fs.rmSync(assembled, { force: true });
    fs.writeFileSync(path.join(qa, 'report.json'), JSON.stringify(report, null, 2) + '\n');
    return { ...report, file: path.relative(dir, path.join(qa, 'report.json')) };
  } finally {
    await server.close();
    await browser.close();
  }
}

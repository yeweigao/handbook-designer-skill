#!/usr/bin/env node
// 统一入口：node hb/core/cli.mjs <命令> <项目> [选项]
//   render  <项目> [--lang zh-CN] [--out .build/xxx]   渲染快照与 PDF，写 .build/<构建 ID>/
//   measure <项目> [--lang zh-CN] [--build <构建 ID>]  测量当前源对应构建（或指定构建），写 .qa/<构建 ID>/<语言>/measure.*
//   check   <项目> [--lang zh-CN]                     渲染 + 测量 + 最终 PDF 检查 + 栅格 + 原文覆盖 → .qa/<构建 ID>/gate.json
//   verify  <项目>                                    核对当前源与 PDF 是否仍与验收记录一致（导出前必跑）
//   paginate <项目> [--flow <名称>]                    默认语言续排：按实际排版分配 data-flow 内容并写回 book.html
import path from 'node:path';
import { render } from './render.mjs';
import { measure } from './measure.mjs';
import { check, verify } from './gate.mjs';
import { paginate } from './paginate.mjs';

function parse(argv) {
  const args = { _: [], langs: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--lang') args.langs.push(argv[++i]);
    else if (a === '--out') args.out = argv[++i];
    else if (a === '--build') args.build = argv[++i];
    else if (a === '--flow') args.flow = argv[++i];
    else args._.push(a);
  }
  return args;
}

async function main() {
  const args = parse(process.argv.slice(2));
  const [cmd, project] = args._;
  if (!['render', 'measure', 'check', 'verify', 'paginate'].includes(cmd) || !project) {
    console.error('用法：node hb/core/cli.mjs render|measure|check|verify|paginate <项目> [--lang <语言>] [--out <项目内目录>] [--build <构建 ID>] [--flow <名称>]');
    return 2;
  }
  try {
    if (cmd === 'check') {
      const g = await check(project, { langs: args.langs });
      console.log(`验收 ${g.build_id}：${g.status === 'deliverable' ? '可交付（技术检查）' : '不可交付'} → ${g.file}`);
      for (const [l, v] of Object.entries(g.languages)) console.log(`  ${l}: ${Object.entries(v.checks).map(([k, s]) => `${k}=${s}`).join(' ')}`);
      for (const b of g.blocking) console.log(`    ${String(b.status).toUpperCase()} [${b.lang}] ${b.id}${b.page ? ' ' + b.page : ''}${b.target ? ' ' + b.target : ''}: ${b.message}`);
      return g.status === 'deliverable' ? 0 : 1;
    }
    if (cmd === 'paginate') {
      const r = await paginate(project, { flow: args.flow });
      for (const f of r.flows) console.log(`  ${f.flow}: ${f.frames} 个文字框，新增续页 ${f.added_pages.length}，移除旧续页 ${f.removed_pages.length}，拆分 ${Object.keys(f.fragments).length} 段（句末 ${f.splits.sentence}、行尾 ${f.splits.line}）${f.forced.length ? `，强制按字拆 ${f.forced.length} 段` : ''}`);
      for (const h of r.hints) console.log(`  提示 ${h.code} ${h.page || ''}: ${h.message}`);
      for (const e of r.errors) console.log(`  ERROR ${e.code} ${e.page || ''} ${e.target || ''}: ${e.message}`);
      console.log(r.errors.length ? '续排失败，作者源未改动' : (r.written ? `已写回作者源（共 ${r.pages} 页），差异见 .qa/paginate/book.html.diff` : '无需改动'));
      return r.errors.length ? 1 : 0;
    }
    if (cmd === 'verify') {
      const v = await verify(project);
      console.log(`${v.valid ? '有效' : '无效'}：当前构建 ${v.buildId}`);
      for (const r of v.reasons) console.log(`  ${r}`);
      return v.valid ? 0 : 1;
    }
    if (cmd === 'measure') {
      const r = await measure(project, { langs: args.langs, build: args.build });
      console.log(`测量构建 ${r.buildId}`);
      for (const l of r.results) {
        console.log(`  ${l.lang}: ${l.status === 'pass' ? '通过' : '不通过'}（硬项失败 ${l.summary.fail}，硬项未验证 ${l.summary.unverified}，提示 ${l.summary.hints}）→ ${l.file}`);
        for (const i of l.items.filter((x) => x.status !== 'pass' && x.severity === 'hard')) console.log(`    ${i.status.toUpperCase()} ${i.id} ${i.page || ''} ${i.target || ''}: ${i.message}`);
      }
      return r.status === 'pass' ? 0 : 1;
    }
    const r = await render(project, { langs: args.langs, out: args.out });
    for (const w of r.warnings) console.log(`WARN  ${w.code}: ${w.message}`);
    console.log(`构建 ${r.build_id} → ${path.relative(process.cwd(), r.outDir)}`);
    for (const l of r.results) {
      console.log(`  ${l.lang}: ${l.status === 'pass' ? '通过' : '失败'}，${l.page_count} 页${l.pdf ? `，${l.pdf.path}` : ''}`);
      for (const e of l.errors) console.log(`    ERROR ${e.code}: ${e.message}`);
    }
    return r.status === 'pass' ? 0 : 1;
  } catch (e) {
    console.error(`ERROR ${e.code || cmd}: ${e.message}`);
    return 1;
  }
}

main().then((code) => process.exit(code));

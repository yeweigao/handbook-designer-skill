#!/usr/bin/env node
// 统一入口：node hb/core/cli.mjs <命令> <项目> [选项]
//   render <项目> [--lang zh-CN] [--out .build/xxx]   渲染快照与 PDF，写 .build/<构建 ID>/
import path from 'node:path';
import { render } from './render.mjs';

function parse(argv) {
  const args = { _: [], langs: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--lang') args.langs.push(argv[++i]);
    else if (a === '--out') args.out = argv[++i];
    else args._.push(a);
  }
  return args;
}

async function main() {
  const args = parse(process.argv.slice(2));
  const [cmd, project] = args._;
  if (cmd !== 'render' || !project) {
    console.error('用法：node hb/core/cli.mjs render <项目> [--lang <语言>] [--out <项目内目录>]');
    return 2;
  }
  try {
    const r = await render(project, { langs: args.langs, out: args.out });
    for (const w of r.warnings) console.log(`WARN  ${w.code}: ${w.message}`);
    console.log(`构建 ${r.build_id} → ${path.relative(process.cwd(), r.outDir)}`);
    for (const l of r.results) {
      console.log(`  ${l.lang}: ${l.status === 'pass' ? '通过' : '失败'}，${l.page_count} 页${l.pdf ? `，${l.pdf.path}` : ''}`);
      for (const e of l.errors) console.log(`    ERROR ${e.code}: ${e.message}`);
    }
    return r.status === 'pass' ? 0 : 1;
  } catch (e) {
    console.error(`ERROR ${e.code || 'render'}: ${e.message}`);
    return 1;
  }
}

main().then((code) => process.exit(code));

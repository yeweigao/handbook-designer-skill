#!/usr/bin/env node
// 统一入口：node hb/core/cli.mjs <命令> <项目> [选项]
//   render  <项目> [--lang zh-CN] [--out .build/xxx]   渲染快照与 PDF，写 .build/<构建 ID>/
//   measure <项目> [--lang zh-CN] [--build <构建 ID>]  测量当前源对应构建（或指定构建），写 .qa/<构建 ID>/<语言>/measure.*
import path from 'node:path';
import { render } from './render.mjs';
import { measure } from './measure.mjs';

function parse(argv) {
  const args = { _: [], langs: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--lang') args.langs.push(argv[++i]);
    else if (a === '--out') args.out = argv[++i];
    else if (a === '--build') args.build = argv[++i];
    else args._.push(a);
  }
  return args;
}

async function main() {
  const args = parse(process.argv.slice(2));
  const [cmd, project] = args._;
  if (!['render', 'measure'].includes(cmd) || !project) {
    console.error('用法：node hb/core/cli.mjs render|measure <项目> [--lang <语言>] [--out <项目内目录>] [--build <构建 ID>]');
    return 2;
  }
  try {
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

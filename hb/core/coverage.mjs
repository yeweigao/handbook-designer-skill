// 原文覆盖（S5）：gate.mjs 通过动态导入调用。逻辑在 coverage.py。
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const HERE = path.dirname(new URL(import.meta.url).pathname);

export async function coverage(dir, buildId, lang) {
  const r = spawnSync('python3', [path.join(HERE, 'coverage.py'), dir, buildId, lang], { encoding: 'utf8' });
  const file = path.join(dir, '.qa', buildId, lang, 'coverage.json');
  if (!fs.existsSync(file)) {
    return { status: 'fail', items: [{ id: 'coverage.run', status: 'unverified', severity: 'hard', page: null, target: null, evidence: {},
      message: `原文覆盖检查没有运行成功：${(r.stderr || r.stdout || '').trim().slice(0, 300)}` }] };
  }
  const rep = JSON.parse(fs.readFileSync(file, 'utf8'));
  return { status: rep.status, items: rep.items };
}

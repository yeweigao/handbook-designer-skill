// 读取并解析项目参数。结构合法性由 validate.py 负责，这里只做渲染需要的推导。
import fs from 'node:fs';
import path from 'node:path';

export function loadProject(root) {
  const dir = path.resolve(root);
  const p = JSON.parse(fs.readFileSync(path.join(dir, 'project.json'), 'utf8'));
  const c = p.canvas;
  const safe = Array.isArray(c.safe_mm) ? c.safe_mm : [c.safe_mm, c.safe_mm, c.safe_mm, c.safe_mm];
  const geom = {
    trimW: c.trim_mm[0], trimH: c.trim_mm[1], bleed: c.bleed_mm,
    mediaW: c.trim_mm[0] + 2 * c.bleed_mm, mediaH: c.trim_mm[1] + 2 * c.bleed_mm,
    safe: { top: safe[0], right: safe[1], bottom: safe[2], left: safe[3] },
  };
  return { dir, p, geom };
}

export const mmToPx = (mm) => (mm * 96) / 25.4;

// 只服务项目目录内文件的本地 HTTP 服务；记录每个请求，拒绝目录外与不存在的文件。
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif', '.avif': 'image/avif',
  '.ttf': 'font/ttf', '.otf': 'font/otf', '.woff': 'font/woff', '.woff2': 'font/woff2',
};

export async function serve(root) {
  const realRoot = fs.realpathSync(root);
  const log = [];
  const server = http.createServer((req, res) => {
    let rel;
    try { rel = decodeURIComponent(new URL(req.url, 'http://x').pathname).replace(/^\/+/, ''); }
    catch { res.writeHead(400).end(); return; }
    const full = path.resolve(realRoot, rel);
    let real = null;
    try { real = fs.realpathSync(full); } catch { /* 不存在 */ }
    if (!real) { log.push({ path: rel, status: 404 }); res.writeHead(404).end(); return; }
    if (real !== realRoot && !real.startsWith(realRoot + path.sep)) {
      log.push({ path: rel, status: 403 }); res.writeHead(403).end(); return;
    }
    if (!fs.statSync(real).isFile()) { log.push({ path: rel, status: 404 }); res.writeHead(404).end(); return; }
    log.push({ path: path.relative(realRoot, real).split(path.sep).join('/'), status: 200 });
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(real).toLowerCase()] || 'application/octet-stream',
      'Cache-Control': 'no-store' });
    fs.createReadStream(real).pipe(res);
  });
  await new Promise((ok) => server.listen(0, '127.0.0.1', ok));
  const origin = `http://127.0.0.1:${server.address().port}`;
  return { origin, log, close: () => new Promise((ok) => server.close(ok)) };
}

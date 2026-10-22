// 锁定版本的 Playwright Chromium。正式渲染不回退到系统 Chrome。
import { createRequire } from 'node:module';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const PW_VERSION = require('playwright/package.json').version;

// 无 root 的 Linux 环境里由 setup_env.sh 补到 ~/.local/hb-libs 的系统库（只影响能否启动，不影响排版）。
function extraLibDirs() {
  const dirs = (process.env.HB_LIB_DIR || '').split(':').filter(Boolean);
  const root = path.join(os.homedir(), '.local', 'hb-libs', 'root', 'usr', 'lib');
  if (fs.existsSync(root)) {
    for (const d of fs.readdirSync(root)) {
      const full = path.join(root, d);
      if (fs.statSync(full).isDirectory()) dirs.push(full);
    }
    dirs.push(root);
  }
  return dirs;
}

export async function launch() {
  const libs = extraLibDirs();
  const env = libs.length ? { ...process.env, LD_LIBRARY_PATH: [...libs, process.env.LD_LIBRARY_PATH].filter(Boolean).join(':') } : undefined;
  // HB_CHROMIUM：显式指定浏览器可执行文件（例如云端预装的 Chromium）。会记录在构建清单里，构建 ID 随之改变。
  const executablePath = process.env.HB_CHROMIUM || undefined;
  try {
    const browser = await chromium.launch({ executablePath, env,
      args: ['--no-sandbox', '--font-render-hinting=none', '--disable-lcd-text'] });
    return { browser, info: { playwright: PW_VERSION, chromium: browser.version(), executable: executablePath ? 'HB_CHROMIUM' : 'playwright-bundled' } };
  } catch (e) {
    const err = new Error(`无法启动锁定版本的 Chromium（playwright ${PW_VERSION}）。` +
      `请运行 bash hb/core/setup_env.sh。原始错误：${String(e.message || e).split('\n')[0]}`);
    err.code = 'browser.launch';
    throw err;
  }
}

// 打开一个固定参数的页面：只放行本地服务，其余请求全部拒绝并记录。
export async function openPage(browser, origin, blocked) {
  const context = await browser.newContext({
    viewport: { width: 1200, height: 1600 }, deviceScaleFactor: 1, locale: 'zh-CN', timezoneId: 'UTC',
    reducedMotion: 'reduce', colorScheme: 'light', javaScriptEnabled: true,
  });
  await context.route('**/*', (route) => {
    const url = route.request().url();
    if (url.startsWith(origin + '/')) return route.continue();
    blocked.push(url);
    return route.abort('blockedbyclient');
  });
  const page = await context.newPage();
  return { context, page };
}

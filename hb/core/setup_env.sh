#!/usr/bin/env bash
# 准备新运行时环境：bash hb/core/setup_env.sh
# 1) 安装锁定版本的 playwright；2) 下载它对应的 Chromium；3) Linux 下检查缺失的系统库，
#    无 root 时用 apt-get download 补到 ~/.local/hb-libs（browser.mjs 会自动使用）；4) 试启动。
set -euo pipefail
HB="$(cd "$(dirname "$0")/.." && pwd)"
cd "$HB"
[ -d node_modules/playwright ] || npm ci --no-audit --no-fund
if [ -z "${HB_CHROMIUM:-}" ]; then npx playwright install chromium; fi
if [ "$(uname)" = "Linux" ] && [ -z "${HB_CHROMIUM:-}" ]; then
  BIN=$(node -e "console.log(require('playwright').chromium.executablePath())")
  [ -x "$BIN" ] || BIN=$(ls -d "${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}"/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell 2>/dev/null | tail -1)
  LIBROOT="$HOME/.local/hb-libs"
  LIBPATH=$(find "$LIBROOT/root" -type d 2>/dev/null | tr '\n' ':' || true)
  MISSING=$(LD_LIBRARY_PATH="$LIBPATH${LD_LIBRARY_PATH:-}" ldd "$BIN" 2>/dev/null | awk '/not found/{print $1}' | sort -u || true)
  if [ -n "$MISSING" ]; then
    echo "缺少系统库：$MISSING"
    mkdir -p "$LIBROOT" && cd "$LIBROOT"
    for lib in $MISSING; do
      PKG=$(dpkg -S "*/$lib" 2>/dev/null | head -1 | cut -d: -f1 || true)
      [ -n "$PKG" ] || PKG=$(apt-cache search --names-only "^lib$(echo "$lib" | sed -E 's/^lib//; s/\.so.*//' | tr 'A-Z' 'a-z')[0-9]*$" | awk '{print $1}' | head -1)
      [ -n "$PKG" ] && apt-get download "$PKG" && dpkg-deb -x "$PKG"_*.deb root || echo "无法自动补 $lib，请安装系统依赖：npx playwright install-deps chromium"
    done
    cd "$HB"
  fi
fi
node --input-type=module -e "import { launch } from './core/browser.mjs'; const { browser, info } = await launch(); console.log('浏览器就绪', JSON.stringify(info)); await browser.close();"

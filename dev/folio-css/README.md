# Folio CSS 展示与维护

直接打开 [index.html](index.html)。无需启动开发服务器、安装前端框架或编译 CSS；也可以从仓库根目录运行 `python3 -m http.server 8765 --bind 127.0.0.1`，访问 `/dev/folio-css/`。

- 规则预览直接使用 `families/folio/design.css`，可操作网格比例、图片比例与焦点。
- 16 个布局目录项、8 个组件配方来自 `catalog.json`；`catalog.js` 是标准脚本形式的生成副本，让本地文件打开也可使用。
- 点击示例看完整结构、组合说明、适用边界与源码；结构视图只加轮廓及弱化照片，不改变布局。
- 组件只是普通 HTML 配方，没有额外组件 CSS。复制到新项目后换成本项目素材路径，并补齐内容 ID、data-role、编辑 ID、必要的出血/叠放声明。
- 展示的摄影引用自然营素材库，授权见该项目的 `sources/assets.json`。示例不表示同一地点或同一次活动。

## 改动后

```sh
python3 dev/build-folio-css.py
python3 dev/build-folio-css.py --check
node --test dev/tests/core/family-css.test.mjs
```

`HB_CHROMIUM` 可显式指定已有浏览器，不自动安装。修改分发 CSS 不会更新已有项目的冻结副本；对本次开发样册，主动同步 `design.css` 和 project 中的 SHA 后重建审稿。

```sh
node hb/core/cli.mjs check dev/samples/native/folio-system
# 对当前最终 PDF 逐页及面对页审稿，记录 review 后：
python3 dev/folio-css/update-preview.py <build-id>
```

`update-preview.py` 先运行 verify，并核对 PDF 哈希，再生成固定源预览 `preview.html`、整册栅格 `specimen.png` 与来源记录 `specimen.json`。预览不是作者源。打印样册使用本项目自己的冻结 CSS 和字体，不引用仓库里会变化的系统文件。

首版验证见 [verification.md](verification.md)。范围为当前 Chromium 与实际 PDF；没有把单册作者自评当独立审美校准。

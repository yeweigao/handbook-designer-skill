# handbook-designer

把 Word、PDF、PPT、Markdown 或文字材料做成多页手册、宣传册、画册、指南的 Skill。
直接创作 HTML/CSS/SVG，检查最终 PDF，交付可编辑 PDF、离线 HTML 与可重建源包。
底座是 Folio 瑞士主义家族 CSS：统一网格、双结构排印、摄影与信息图表。

## 用这个 Skill

**不要克隆整个仓库**，去 [Releases](https://github.com/yeweigao/handbook-designer-skill/releases) 下载 `handbook-designer-skill-v2.2.0.zip`：

```sh
unzip handbook-designer-skill-v2.2.0.zip          # 得到 handbook-designer-skill/
mv handbook-designer-skill <你的 skills 目录>/handbook-designer
bash <skill>/hb/core/setup_env.sh                 # 首次：安装锁定版本的 Chromium
python3 <skill>/hb/core/fonts.py install          # 首次：取回三个 OFL 字面
```

之后把材料交给 agent，入口是 `SKILL.md`。仓库里的 `dev/`、`docs/` 是开发资产，
包内不含，也不需要。

## 仓库地图

| 路径 | 运行时需要 | 说明 |
|---|---|---|
| `SKILL.md` | ✅ | 入口：路线、作者边界、交付判据 |
| `hb/core/` | ✅ | 渲染、检查、导出、字体、打包 |
| `families/` | ✅ | 正式 `folio.css`、API 与 HTML 配方；含历史家族兼容 |
| `references/` | ✅ | 契约、版式、审稿尺度等判断依据 |
| `workflows/` `templates/` `purposes/` `brands/` | ✅ | 工作流、模板、用途与品牌配置 |
| `dev/folio-css/` | — | 开发用交互展示；直接使用正式 folio.css，与正式配方同源 |
| `dev/samples/` | — | 样册源码：照片、字体、导出包**不入库**，见 [说明](https://github.com/yeweigao/handbook-designer-skill/blob/main/dev/samples/README.md) |
| `dev/tests/` `dev/fixtures/` | — | 契约测试与夹具 |
| `dev/audits/` | — | 实施与审计记录 |
| `dev/archive/` | — | 已退役的旧引擎，只作历史 |
| `docs/` | — | 给维护者的文档 |

源字体通过上面的 install 命令准备，具体项目使用自己的真实图片。仓库中的开发样册图片与导出包不属于安装包；只有维护者重建样册时才需要恢复其素材：

```sh
python3 dev/samples/fetch-assets.py --all      # 按 sources/assets.json 的来源记录取回照片
```

## 开发

```sh
python3 hb/core/pack_skill.py                  # 打出用户版 zip（dist/）
node hb/core/cli.mjs check dev/samples/native/folio-swiss     # 完整验收一本样册
python3 -m unittest discover -s dev/tests/core -p 'test_*.py'  # Python 测试
bash dev/tests/selftest.sh --quick             # 快速自检
```

写作流程见 [workflows/new.md](workflows/new.md)：以 `folio.css` 为主题，`book.css` 默认留空、必要时局部补丁，
再三页小样定风格，最后铺全册。技术检查只能证明物理与内容条件，视觉质量看最终 PDF 的每一页。

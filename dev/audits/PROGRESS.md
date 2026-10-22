# HTML/CSS 原生改造 · 进度与交接

分步说明见 [IMPLEMENTATION-STEPS](IMPLEMENTATION-STEPS.md)。新记录追加在最下方，不改写旧记录。

## 状态表

| 步骤 | 状态 | 最近更新 | 提交 |
|---|---|---|---|
| S1 契约与最小样例 | 完成 | 2026-10-22 | 见记录 |
| S2 渲染运行时 | 未开始 | | |
| S3 版面测量与可读性检查 | 未开始 | | |
| S4 最终 PDF 检查与验收绑定 | 未开始 | | |
| S5 内容提取与原文覆盖 | 未开始 | | |
| S6 长文续页工具 | 未开始 | | |
| S7 Campus 家族与真实样册 | 未开始 | | |
| S8 导出与离线交付 | 未开始 | | |
| S9 Folio 联动 | 未开始 | | |
| S10 Skill 文档与旧引擎退役 | 未开始 | | |
| S11 视觉参考资产 | 未开始 | | |
| S12 独立生成基准 | 未开始 | | |

状态取值：未开始 / 进行中 / 中断 / 完成 / 完成（有遗留）。

## 交接记录模板

每完成一步（或中途停下）复制下面的模板追加一条：

```markdown
### S<n> · <名称> · <完成 | 中断> · YYYY-MM-DD

- 改动范围：<新增 / 修改的文件，按目录列>
- 可复制命令：<从仓库根目录运行，能复现验收的命令>
- 完成判定逐条结果：
  - <判定 1>：pass / fail / unverified —— 证据：<输出摘要或文件路径>
- 契约变更：<无 / 改了什么、为什么、影响哪些步骤>
- 偏离计划的决定：<无 / 决定与理由>
- 新增依赖：<无 / 包名@版本与原因>
- 未完成与已知问题：<列表>
- 下一步从哪继续：<中断时必填：具体到文件和函数>
- 提交：<hash>
```

## 记录

### S0 · 准备 · 完成 · 2026-10-22

- 改动范围：新建分支 `html-native`；修订总计划（多语言共用作者源、可读性硬下限、长文续页、Folio 本地联动、可编辑 PDF 保留、经验层后移、审稿校准）；新增 `IMPLEMENTATION-STEPS.md` 与本文件。
- 环境（用户 Mac 上的 Linux 工作环境）：Node v22.23.2、Python 3.10.12、pdfinfo / pdftoppm / pdffonts / qpdf 可用；pyyaml、pillow、numpy、fonttools、pikepdf 已装；npm 与 pip 可联网；`hb/node_modules` 尚未安装（S2 处理）。
- 提交身份：本环境没有 git 全局身份，提交时用 `git -c user.name=yeweigao -c user.email=64359184+yeweigao@users.noreply.github.com commit ...`（与仓库既有提交一致）。
- 下一步：S1。

### S1 · 契约与最小样例 · 完成 · 2026-10-22

- 改动范围：
  - `references/contract.md`：contract 1 —— 项目目录、`project.json` 字段、渲染器生成的打印 CSS 与页面变量、作者 HTML 约定（页面、跨页、内容节点、片段、有意重复、角色、续排流、叠放、出血）、可读性下限表、多语言文案、内容模式、构建 ID、检查报告格式。
  - `hb/core/validate.py`：契约校验（标准库，Python 3.10）。
  - `dev/fixtures/contract/minimal-zh/`、`dev/fixtures/contract/bilingual/`：正例项目（含字体子集与 OFL 授权文本、合成跨页图）。
  - `dev/tests/core/test_validate.py`（正例 + 36 个反例 + 放宽授权 + 退出码）、`fixture_fonts.py`（样例字体子集）、`make_fixture_images.py`（合成图）、`font-licenses/`。
  - `.gitignore`：忽略 `.build/` 与样例的 `.qa/`。
- 可复制命令：
  - `python3 hb/core/validate.py dev/fixtures/contract/minimal-zh`
  - `python3 hb/core/validate.py dev/fixtures/contract/bilingual`
  - `python3 -m unittest discover -s dev/tests/core -p 'test_*.py'`
  - 改了样例文字后：`python3 dev/tests/core/fixture_fonts.py dev/fixtures/contract/<样例>`
- 完成判定逐条结果：
  - 两个正例退出码 0：pass —— 两者均「0 个错误，0 个警告」。
  - 反例退出码非 0 且指出文件与 ID：pass —— 36 个反例全部报出期望错误码；CLI 示例输出含 `book.html:28`、`copy/en.json` 与具体 ID。
  - 契约与总计划无冲突：pass（取舍见下）。
- 契约变更：首版，无。
- 偏离计划的决定：
  - 不建 JSON schema 文件、校验器用 Python 而非 Node：标准库自带 HTML 解析器，零新依赖；契约文档 + `validate.py` 是唯一权威，避免 schema 与代码两份真相。
  - 默认语言文案写在 `book.html`，`copy/` 只放其他语言，每种语言只有一个文案来源。
  - 字体只在 `project.json` 声明，作者 CSS 禁止 `@font-face`：S3 才能确定「声明过的字体」并识别系统回退。
  - 作者源禁止 `<style>` / `<link rel=stylesheet>`：样式只在 `styles` 列出的文件里，便于指纹与 Folio 写回。
  - 可读性下限按物理尺寸（px = 1/96 英寸），不随纸张缩放；降低只能经 `readability_waiver` 并始终报告。
  - 续页片段在多语言下的表示留给 S6 定义（契约只保留 `data-fragment`）。
- 新增依赖：无（fontTools、Pillow 已在 requirements 中，仅测试工具使用）。
- 未完成与已知问题：
  - `validate.py` 是静态检查，不知道实际渲染尺寸；页面尺寸、溢出、字体回退等由 S2/S3 在浏览器里检查。
  - 装订页数在作者阶段只报警告，硬检查在 S4 的 PDF 上做。
- 下一步：S2 渲染运行时。先 `cd hb && npm ci`（或 `npm install`）安装锁定的 playwright@1.64.1，并确认能拿到对应的 Chromium。

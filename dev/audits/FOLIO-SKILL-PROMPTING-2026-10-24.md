# Folio Skill：主题契约与提示词收口

日期：2026-10-24。基线：45142c1。目标是正常用户包独立可用，约束 agent 用 Folio 设计，而非把 Folio 当配色参考。

## 官方资料核对

- [OpenAI · Using GPT-6](https://developers.openai.com/api/docs/guides/latest-model)：建议移除重复指令、精简工具说明；保留真正编码产品要求或修复已测缺口的示例，并用同一组代表任务验证精简效果。没有支持“只写情绪就足够”的结论。
- [OpenAI · Build skills](https://developers.openai.com/plugins/build/skills)：skill 明确输入、输出、边界、不可猜的事实及按需参考；流程有依赖时仍需表达依赖，不能把验收步骤一起删掉。
- [Anthropic · Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5)：前端设计一节明确说，泛泛避免 AI 外观可能只是换成另一种默认样式；应给具体模式和约束，并迭代检查实际结果。此结论用于提示写法，不把网页例子里的禁用清单机械搬到印刷系统。
- [Anthropic · Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)：简洁、分层披露；自由度应与任务风险相称，用真实使用反馈验证。

以下是对本项目的应用判断，不冒称官方提供了 Folio 专用方案。

## 核心改动

入口从 5307 字符收至 2814，优先写结果、设计边界、必要证据与路由。常用命令移至按需参考；new 从九步重复清单收为输入/设计/交付三个成立条件。保留用户明确要求的三页小样与最多三轮；不新增审批。

主题是唯一共同语言：正式分发 `families/folio/folio.css`，项目冻结副本先加载，`book.css` 默认留空。新增以“阅读任务 → 现有能力缺口 → 局部补丁 → 最终证据”成立；不能借内联、语言覆盖或换类名重造另一套系统。共享主题维护与单册制作分开。

开发站继续使用正式 CSS；正式配方与网站由同一源目录生成。使用包不含开发站、测试或审计目录，所有创作参考在正式路径。旧项目的 design.css 不自动迁移。

## 提示词与代码各自的限度

设计意图、信息层级、留白是否有效由提示词与审稿判断；字体与内容、物理条件、冻结主题哈希和已支持的样式漂移用代码检查。静态规则不是完整 CSS 解析器，不能声称消灭全部任意样式或保证美观。主题哈希也不能防止有权改项目元数据的作者同时改哈希；提示契约明确禁止把这种做法当绕行。

代表性验证包括：用户包无 dev 的真实初始化/检查/导出，旧 design.css 兼容与零写入重入，正式配方覆盖一致，冻结文件篡改反例，实际浏览器回归。没有据此宣称跨模型审美成功率提高；模型行为及独立审美评测仍需真实创作任务。

## 本轮结果

- 正式安装包 99 个文件、约 0.3 MB，不含 dev/docs；包内 Markdown 本地链接全部解析。44 个 Python、20 个家族浏览器、14 个渲染/导出测试通过。
- 独立于仓库开发目录的三页样本 `be2ff550c562`，book.css 无声明，五项技术验收与四项正式导出检查通过；实际审阅三页最终栅格。实跑复用了已安装 Playwright/Chromium 和源字体缓存，无新安装。详见 [包验证证据](FOLIO-SKILL-PACKAGE-PROOF-2026-10-24.json)。
- 新上下文 agent 的小型只读试用：给予三页“观察城市”活动指南的材料，选用 new/quick、light 排印、六栏组合与纵向日程，按 ID 读取 6 个配方，最终 book.css 留空；没有把静态片段称作已验收成品。原始报告在 `/private/tmp/folio-skill-prompt-probe.md`。这只是一次路由/样式决策样本；测试明确限定正式参考、禁用 dev，未验证完整自主成书或跨模型审美效果。
- CSS 声明与原正式版一致，仅分发名称与维护注释变更；已有 100 页样刊保持冻结文件。运行时代码更新按契约改变工具指纹，旧 gate 不冒称仍对新运行时有效。

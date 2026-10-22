# 定稿美化

适用：用户要求保持定稿文字。`project.json` 设 `content_mode: frozen`，具体授权写 brief。冻结检查严格核对 MISSING / ORDER / EXTRA，拒绝 `sources/adapt.json`。

1. 提取原稿，核对原文件中的段落、页顺序和图片关系。按 [文案适配](../references/adaptation.md) 标明语义角色，保持文字、数字、限定条件与次序。
2. 如果用户明确要求一页对一页，在 page-plan 逐页记录原页→成品页，人工核对页数、顺序与图文归属；当前门禁核对内容与 PDF 页数一致性，**不会自动证明原稿逐页对应**。仅说“美化”时不擅自增加页对应承诺。
3. 直接创作 HTML/CSS，允许新构图。既定页对应约束下优先改分组与栏宽，放不下就报告具体页；已有授权允许拆页则记录后继续，否则先取得改变约束的决定。
4. 跑所有语言 `check`，执行 [visual-review](visual-review.md) 并导出。原稿自身错误按已有授权处理；没有改写授权就保留并指出。

用户通过 Folio 本人修改的文字由工具记录在 `sources/user-edits.json`，冻结模式也承认。agent 的改写不能写入该文件冒充用户编辑。

# Folio 完整设计系统样刊

此目录由 `python3 dev/folio-css/build-specimen.py` 根据交互展示的同一份目录生成。修改配方请编辑 dev/folio-css 中的源 JSON，先运行 dev/build-folio-css.py，再重建本册。作者源为 book.html 与 book.css，家族 CSS 与字体已冻结；coverage.json 映射每一目录项到书页。表现与变奏章先有 philosophy-variations.md 的视觉主张（受控变量），再逐页落版；主张只管判断标准，不定尺寸与模数。主张不进成品，留在项目目录，供改版时对照。

构建完后依次执行 validate、check、实际看全部最终 PDF、review，再更新展示预览。生成器不写任何通过或视觉批准声明。

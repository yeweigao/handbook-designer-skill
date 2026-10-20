# 路线 brand：建品牌包 / 用品牌包

品牌包 = 一个机构的配色、字体、logo、页脚、封底联系方式、口吻和禁忌，放在 `brands/<名字>/`，在 `brands/index.yaml` 登记。
书里写 `book.brand: <名字>`：品牌包的设置作为默认值，book.yaml 里写了的优先；logo 自动放在封面、封底（其他页写 `logo: true`），封底自动加联系方式（装饰文字，不算 EXTRA，交付时列为非原文元素）。

## 用现成的
`brands/index.yaml` 里列着有哪些。用户说“用我们的品牌 / 和官网一致”且有对应的包 → 直接用，方向样张里至少一个方向是品牌包。
现有示例：**acme**（Acme Studio：虚构示例品牌，演示点缀档配色——白纸 + 浅底，电光靛蓝做标题和数字，深色做封面和章节页，Comfortaa 圆润几何字体，单色矢量 logo）。

## 新建
需要的材料（缺的问用户，或从官网 / 旧物料里取）：logo（单色 SVG 最好）、主色 + 强调色、字体（中文 / 西文）、公司全称、网址、地址 / 电话、口吻、禁忌。
```bash
bash $HB/new_brand.sh <名字> "<品牌显示名>" [logo.svg] [主色] [强调色]
```
→ `brands/<名字>/brand.yaml`（结构照 acme 示例）、`logo.svg`（没给 logo 就用 Comfortaa 生成文字标占位：`hb/wordmark.py` 也能单独用，`--mark A` 加圆形字母标）、`preview.jpg` 样张、index.yaml 登记一条。
然后打开 brand.yaml 补全：
- `book.colors`：按角色写（style.md §8）：至少 `primary` 主色、`accent` 强调色、`background`、`body_text`。
- `color_mode`：品牌色几乎都该用 `accent`（点缀）——品牌色只做标题、数字、细线，大面积是白纸和浅色；只有品牌本身就是强烈撞色（如橙 × 黑）才用 `clash`。拿不准写 `auto`，构建时会打印判断理由。
- `book.fonts`：从 `python3 hb/fonts.py list` 里选；品牌字体不在列表里且是开源授权 → 放进 hb/fonts 并在 fonts.py 登记；商用授权字体不要嵌入，选最接近的开源字体并告诉用户。
- `logo`：`mono: true`（单色，自动跟着当页字色变）；彩色 logo 写 `mono: false` 并给 `dark:` 深底版本。
- `contact`、`voice`、`dont`。
- 重新出样张核对：`python3 $HB/directions.py <临时目录> "X=brand:<名字>" --title "<品牌显示名>"`，看 logo、配色、字体。

## 可选：发展品牌图形语言

需要强化全册品牌识别时，按references/style.md §7.1考虑logo衍生暗纹、角部构图、章节锚点或跨页超级图形。先写本册内容与源形的应用方案，再按references/blocks.md的brand_graphic落版；项目SVG放在项目photos/_assets/，与正式logo分开保留。该扩展逐项目、逐页显式启用，品牌包的配色/字体/logo默认仍照常使用。

注意：仓库公开或打包分发时，客户的真实品牌包不应提交入库（`.gitignore` 默认已忽略 `/brands/*`，仅保留 `acme` 虚构示例）。

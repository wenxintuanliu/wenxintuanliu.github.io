---
title: Markdown 样式示例：科研文章组件画廊
type: method
subtitle: Hidden writing-system preview
category: Style Guide
status: seedling
publishedAt: 2026-05-31
updatedAt: 2026-05-31
readingMinutes: 6
tags: [写作系统]
hidden: true
projects: [cyl4, cylinder-hodmd]
references: [chirpy]
referenceItems:
  - chirpy | Chirpy Jekyll Theme | https://github.com/cotes2020/jekyll-theme-chirpy
relatedProjects: [cyl4, cylinder-hodmd]
summary: 隐藏入口文章，用真实 Markdown 展示本站支持的标题、公式、图像、对照滑块、callout、代码块、表格、脚注和引用样式。
---

## 文章结构

这篇文章是隐藏入口，用来预览手写 Markdown 在网站中的真实效果。正文风格参考 Chirpy 的技术写作取向：固定目录、代码块工具栏、数学公式、提示块、引用、脚注和可维护的文章元数据 [cite:chirpy]。

普通正文保持较大的行距，适合解释科研图像。你可以用 **粗体强调结论**，用 *斜体标记术语*，用 `inline code` 标记变量或路径，也可以用 ==高亮背景== 标出需要读者马上注意的句子。

> 引用块用于放置来自论文、代码注释或实验记录的短句。它不承担结论，而是给正文提供上下文。

## Callout 块

:::note Note 标题
`:::note` 适合写数据来源、命名约定、变量单位或读者容易忽略的前提。
:::

:::tip Tip 标题
`:::tip` 适合写操作建议。例如新增项目时，用脚本生成一个 Markdown 文件，然后只改 front matter 和正文。
:::

:::warning Warning 标题
`:::warning` 适合写容易误用的设置，比如色阶是否固定、误差图是否被极端值拉伸。
:::

:::important Important 标题
`:::important` 用于强调文章的核心判断。重要结论最好同时有图、公式或复现实验支撑。
:::

:::danger Danger 标题
`:::danger` 适合标记不可直接复用的脚本、旧数据路径或会覆盖结果的命令。
:::

:::result Result 标题
`:::result` 适合放在图后，给出与图像直接对应的结论，而不是重复图注。
:::

## 数学公式

行内公式写作示例：速度场可以记为 $X(t)\in\mathbb{R}^{N\times 2}$。块级公式用于核心方法：

$$
z(t)=f_\theta(X(t),G),\qquad
\hat{X}(t)=g_\phi(z(t),p).
$$

多行公式也可以直接手写：

$$
\mathcal{L}
=\|\hat{X}-X\|_2^2
+\lambda\|z_{t+1}-2z_t+z_{t-1}\|_2^2 .
$$

## 代码块

代码块会显示语言标签和复制按钮，适合记录复现实验命令、后处理脚本和最小示例：

```python
from pathlib import Path
import numpy as np

root = Path("assets/projects/cyl4")
latent = np.load(root / "example_latent.npz")
print(latent["z"].shape)
```

```bash
python3 postprocess/cyl4/generate_assets.py
python3 tools/validate_site.py
```

## 表格

| 组件 | Markdown 写法 | 适用场景 |
|---|---|---|
| 图像 | `Markdown 图片语法` | 手写文章中的独立图 |
| 证据图 | `![alt](path "caption")` | 正文中直接插入论文式图像 |
| 对照图 | `{{ compare:path_a,path_b }}` | 两张图之间做滑块对比 |
| 提示块 | `:::note 标题` | 数据、风险、结论、操作提示 |

## 图像

普通 Markdown 图片会自动生成论文式编号和图注：

![GCN-AE reconstruction example](assets/projects/cyl4/gcn-ae-reconstruction-t0450.png "GCN-AE 重构质量图作为普通 Markdown 图片示例。")

## Compare 短代码

`{{ compare:left,right }}` 可以直接比较两张图，适合用来检查重构、预测或不同后处理方案的差异：

{{ compare:assets/projects/cyl4/gcn-ae-reconstruction-t0450.png,assets/projects/cylinder-hodmd/reconstruction_t0151_src0151_d50.png }}

## 脚注与引用

脚注适合补充不想打断正文的实现细节。比如本站的样式系统仍然是 vanilla HTML/CSS/JS，不依赖 Jekyll 本体。[^vanilla]

引用用于和文章附录中的 `references` 对齐，例如 Chirpy 的技术写作能力包含目录、更新时间、代码高亮、数学公式和 Feed 等方向 [cite:chirpy]。

[^vanilla]: 这个隐藏示例页仍由同一套静态 registry、Markdown parser 和页面组件渲染。

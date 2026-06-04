# Content authoring

这个目录用于手写内容，结构参考 Chirpy 的 posts / tabs / front matter 约定，但站点仍然是 vanilla JS 静态站。

- `content/projects/*.md`: 项目正文。默认一个项目就是一个 Markdown 文件。
- `content/methods/*.md`: 方法文章和长文。默认一个方法就是一个 Markdown 文件。
- `content/example/*.md`: 站点写作样式示例，作为独立版块维护，平时不用修改。
- `content/assets/`: 以后可以放手写文章专用图片。Markdown 图片也可以直接引用现有 `assets/projects/...`。

## 最简单流程

新建项目：

```bash
python3 tools/new_content.py project example "项目标题" --category "Project" --summary "一句话摘要"
```

它会自动创建：

- `content/projects/example.md`
- `data/registry.json` 中的项目入口

生成的 Markdown 是完整模板，已经包含 front matter、研究问题、方法、图像证据、公式、表格、callout、结果、局限性、复现、数据可用性、引用和互链示例。之后你只需要删改不需要的段落，并在 Markdown 里直接写正文和图片路径：

```markdown
![图像说明](figure-01.png "这段会变成论文式图注。")
![图像说明](assets/projects/example/figure-01.png "站点内路径也可以。")
![图像说明](/home/chunfengfusu/web/research-showcase/assets/projects/example/figure-01.png "站点根目录内的完整路径也可以。")
```

不需要再去 `project.json` 里登记图片路径。

新建方法：

```bash
python3 tools/new_content.py method my-method "方法标题" --category "Method" --summary "一句话摘要"
```

它会自动创建 `content/methods/my-method.md` 并登记到 `data/registry.json`。

## `data/` 目录现在只做必要索引

日常手写内容时，`data/` 不再负责管理正文图片路径。

- 必要：`data/registry.json` 登记项目、方法和导航入口；脚本会自动追加。
- 可选：`data/content.json` 保留阅读路径等全站级索引。
- 不推荐：为了普通正文图片去 JSON 里手工登记路径。

完整绝对路径仅支持站点根目录内的文件，例如：

```markdown
![测试](/home/chunfengfusu/web/research-showcase/assets/profile.png "站点内完整路径。")
```

浏览器无法直接发布 `/home/chunfengfusu/NekRS_run/...` 这种站点外文件；这类图像需要复制或软链接到 `web/research-showcase` 内，再在 Markdown 里引用。

Front matter 示例：

```markdown
---
title: 文章标题
type: project
subtitle: 可选副标题
category: Methods
status: working
publishedAt: 2026-05-30
updatedAt: 2026-05-30
tags: [项目文章]
pinned: false
hero: assets/projects/my-project/hero.gif
methods: [spectral-element]
projects: [cyl4]
references: [nekrs-theory]
referenceItems:
  - nekrs-theory | NekRS Theory Documentation | https://nekrs.readthedocs.io/en/latest/theory.html
relatedProjects: [cyl4]
relatedArticles: [spectral-element-notes]
relatedMethods: [spectral-element]
summary: 一句话摘要，会出现在列表页和详情页。
---
```

支持的正文样式：

- `##` / `###` 标题会自动进入右侧目录。
- `![alt](path "caption")` 会渲染为带图注的论文式图片。
- 如果 Markdown 位于 `content/projects/my-project.md`，相对路径会以 `content/projects/` 为基准解析。
- `{{ compare:left,right }}` 会插入图像对照滑块，`left/right` 直接写图片路径。
- `[cite:key]` 会跳到附录引用；引用 key 必须写在 front matter 的 `referenceItems`。
- `[^key]` 和 `[^key]: 注释内容` 会生成脚注。
- `==重点句子==` 会渲染为高亮背景。
- `$$ ... $$`、Markdown 表格和 fenced code block 会按科研写作样式渲染。
- `:::note 标题`、`:::tip 标题`、`:::warning 标题`、`:::important 标题`、`:::danger 标题`、`:::result 标题` 可以做轻量提示块。
- 普通段落、列表、引用、链接、粗体、斜体、行内代码和行内公式 `$...$` 都可用。
- 首页 `All rights reserved.` 后的头像图标是隐藏样式示例入口，指向 `pages/method.html?id=markdown-style-gallery`。

维护约定：

- 手写正文放在 `content/projects` 或 `content/methods`；不要在页面组件里写正文。
- 手写文章图片可以直接用完整路径或 `assets/projects/<id>` 路径；不需要额外登记图片清单。
- 新增项目或方法后运行 `python3 tools/validate_site.py`，检查路径、引用、互链和 front matter。

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Markdown-first project or method entry.")
    parser.add_argument("kind", choices=["project", "method"], help="content type to create")
    parser.add_argument("id", help="stable url id, e.g. my-new-project")
    parser.add_argument("title", help="display title")
    parser.add_argument("--category", default="", help="category shown in cards")
    parser.add_argument("--summary", default="", help="one-sentence summary")
    parser.add_argument("--status", default="working", choices=["seedling", "working", "evergreen", "archived"])
    parser.add_argument("--pinned", action="store_true", help="pin this entry in indexes")
    args = parser.parse_args()

    registry_path = ROOT / "data/registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))

    if args.kind == "project":
        create_project(args, registry)
    else:
        create_method(args, registry)

    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"created {args.kind}: {args.id}")
    print("next: write Markdown, reference images directly in the .md, then run python3 tools/validate_site.py")
    return 0


def create_project(args, registry: dict) -> None:
    ensure_unique(args.id, registry.get("projects", []), "project")
    content = content_path(args, "projects")
    (ROOT / content).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / content).write_text(project_template(args), encoding="utf-8")
    registry.setdefault("projects", []).append(
        {
            "id": args.id,
            "title": args.title,
            "category": args.category or "Project",
            "content": content,
            "featured": False,
        }
    )


def create_method(args, registry: dict) -> None:
    ensure_unique(args.id, registry.get("methodArticles", []), "method article")
    content = content_path(args, "methods")
    (ROOT / content).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / content).write_text(method_template(args), encoding="utf-8")
    registry.setdefault("methodArticles", []).append(
        {
            "id": args.id,
            "title": args.title,
            "category": args.category or "Method",
            "content": content,
            "featured": False,
        }
    )


def content_path(args, folder: str) -> str:
    return f"content/{folder}/{args.id}.md"


def ensure_unique(content_id: str, entries: list[dict], label: str) -> None:
    if any(entry.get("id") == content_id for entry in entries):
        raise SystemExit(f"{label} id already exists: {content_id}")


def frontmatter(args, content_type: str) -> str:
    today = date.today().isoformat()
    is_project = content_type == "project"
    return f"""---
title: {args.title}
type: {content_type}
subtitle: ""
category: {args.category or ("Project" if is_project else "Method")}
status: {args.status}
publishedAt: {today}
updatedAt: {today}
readingMinutes: 6
tags: [{"项目文章" if is_project else "数值方法"}]
pinned: {"true" if args.pinned else "false"}
hero: ""
methods: []
projects: []
references: []
referenceItems: []
relatedProjects: []
relatedArticles: []
relatedMethods: []
dataAvailability: ""
summary: {args.summary or "一句话说明这篇内容解决什么问题。"}
---
"""


def project_template(args) -> str:
    return frontmatter(args, "project") + f"""
## 研究问题

用 2-4 段说明这个项目研究什么问题、为什么值得展示，以及读者应该先看哪张图。尽量写成论文摘要后的引入，而不是只列参数。

:::note 写作提示
这一节回答“问题是什么”。如果有相关方法，可以直接链接，例如 `[谱元法](pages/method.html?id=spectral-element-notes)`。
:::

## 方法

说明数据来源、计算设置、后处理流程和关键假设。可以写核心变量和公式：

$$
X(t)=\\left[u(t),v(t)\\right]\\in\\mathbb{{R}}^{{N\\times 2}} .
$$

| 项目 | 建议填写内容 |
| --- | --- |
| 数据来源 | 原始算例目录、场文件、采样平面 |
| 数值方法 | 求解器、离散格式、时间推进 |
| 后处理 | 生成图片或 GIF 的脚本 |
| 检查项 | 色阶、坐标轴、误差定义、单位 |

## 图像证据

把真实图片路径写在 Markdown 里即可，不需要再写 `project.json`。下面是常用写法，替换成真实图片后，把代码块去掉即可渲染成论文式图注。

```markdown
![主图说明](assets/projects/{args.id}/hero.png "这里写 Fig 1 的论文式图注。")

![完整路径图片](/home/chunfengfusu/web/research-showcase/assets/projects/{args.id}/figure-01.png "完整路径也可以，但必须位于站点目录内。")
```

如果要做两张图的滑块对比：

```markdown
{{{{ compare:assets/projects/{args.id}/before.png,assets/projects/{args.id}/after.png }}}}
```

:::warning 路径限制
`/home/chunfengfusu/NekRS_run/...` 这种站点外路径不能直接在浏览器发布。先复制或软链接到 `web/research-showcase` 内，再引用。
:::

## 结果

:::result 当前结论
这里用一两句话给出与图像直接对应的结论。结论应该能被上面的图像、公式或表格支撑。
:::

可以用 `==高亮句子==` 标记最关键的发现，但不要替代证据说明。

## 误差与局限性

- 误差如何定义：
- 哪些区域或工况误差最大：
- 当前结果不能说明什么：
- 后续需要补充哪些对照：

## 复现记录

```bash
# 在这里记录生成图像或结果的命令
python3 postprocess/{args.id}/generate_assets.py
```

## 数据可用性

说明网页资产保存在哪里，原始数据是否随站点发布，不能发布的本地路径如何记录。

## 引用与互链

如果正文使用 `[cite:key]`，请在 front matter 中同时填写：

```yaml
references: [key]
referenceItems:
  - key | 文献或项目标题 | https://example.com
relatedProjects: [cyl4]
relatedArticles: [spectral-element-notes]
relatedMethods: [spectral-element]
```
"""


def method_template(args) -> str:
    return frontmatter(args, "method") + f"""
## 方法目标

说明这个方法解决什么问题、适用于什么数据结构、在本站哪些项目中出现。方法页应该可迁移，不要只复述某一个项目。

## 核心公式

$$
y=f_\\theta(x)
$$

逐项解释符号、输入输出、假设和单位。如果有多个阶段，可以拆成小节。

## 使用场景

| 场景 | 说明 |
| --- | --- |
| 适合 | 写清楚数据、网格、时间序列或模型条件 |
| 不适合 | 写清楚会误用的边界 |
| 需要检查 | 写清楚误差、稳定性或参数敏感性 |

:::important 方法边界
这里写这个方法不能保证什么。例如“编码器能重构快照”不等于“模型能长期预测”。
:::

## 图像或流程图

方法页也可以直接插图。替换成真实图片后去掉代码块：

```markdown
![方法流程](assets/projects/{args.id}/workflow.png "方法流程、变量和输出之间的关系。")
```

## 最小示例

```python
def demo(x):
    return x
```

## 项目互链

如果这个方法对应某些项目，在 front matter 中填写：

```yaml
projects: [cyl4]
relatedProjects: [cyl4]
relatedMethods: []
relatedArticles: []
```

正文中也可以直接链接：

```markdown
[查看对应项目](pages/project.html?id=cyl4)
```

## 引用

如果使用 `[cite:key]`，在 front matter 中填写：

```yaml
references: [key]
referenceItems:
  - key | 文献标题 | https://example.com
```
"""


if __name__ == "__main__":
    raise SystemExit(main())

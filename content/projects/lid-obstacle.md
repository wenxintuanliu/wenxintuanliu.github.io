---
title: 顶盖驱动方腔流的含障碍物数值模拟
type: project
subtitle: Nek5000 / Lid-Driven Cavity Flow with Obstacle
category: High-fidelity cavity flow
status: working
publishedAt: 2026-05-10
updatedAt: 2026-05-30
readingMinutes: 8
tags: [项目文章]
titleShort: 顶盖驱动方腔流含障碍物模拟
hero: assets/projects/lid-obstacle/vorticity-z010-spectral512.gif
methods: [spectral-element]
projects: [cyl4]
references: [nek5000-theory]
referenceItems:
  - nek5000-theory | Nek5000 Theory Documentation | https://nek5000.github.io/NekDoc/theory.html
relatedProjects: [cyl4]
relatedArticles: [spectral-element-notes]
relatedMethods: [spectral-element]
dataAvailability: 平均流线图和涡量 GIF 已发布在 assets/projects/lid-obstacle/；原始瞬时场路径保留在后处理脚本中。
summary: 顶盖驱动方腔流在 Re = 1000、3200、5000 下进行无障碍物与含障碍物对比。
---


## 对照方式

页面展示 `Re = 1000 / 3200 / 5000` 下无障碍物与含障碍物的平均流线图，并用 `z = 0.1` 切片涡量 GIF 展示含障碍物流动的瞬态结构 [cite:nek5000-theory]。

![Vorticity evolution on z = 0.1](assets/projects/lid-obstacle/vorticity-z010-spectral512.gif "含障碍物算例在 z = 0.1 平面的瞬态涡量演化，障碍物区域被置空以避免误读。")

![Re = 1000, no obstacle](assets/projects/lid-obstacle/mean-streamline-re1000-base.webp "Averaged streamline plot, y = 0.5")

![Re = 1000, with obstacle](assets/projects/lid-obstacle/mean-streamline-re1000-obstacle.webp "Averaged streamline plot, y = 0.5")

![Re = 3200, no obstacle](assets/projects/lid-obstacle/mean-streamline-re3200-base.webp "Averaged streamline plot, y = 0.5")

![Re = 3200, with obstacle](assets/projects/lid-obstacle/mean-streamline-re3200-obstacle.webp "Averaged streamline plot, y = 0.5")

![Re = 5000, no obstacle](assets/projects/lid-obstacle/mean-streamline-re5000-base.webp "Averaged streamline plot, y = 0.5")

![Re = 5000, with obstacle](assets/projects/lid-obstacle/mean-streamline-re5000-obstacle.webp "Averaged streamline plot, y = 0.5")

:::note 阅读提示
平均流线图用于比较长期结构，涡量动画用于观察瞬态剪切层。
:::



---
title: MFC 多相流工作流：冲击波、界面与固定画布后处理
type: method
subtitle: Compressible Multiphase Workflow
category: Method
status: working
publishedAt: 2026-05-30
updatedAt: 2026-05-30
readingMinutes: 5
tags: [数值方法]
projects: [swm]
methods: [compressible-multiphase]
references: [mfc-code]
referenceItems:
  - mfc-code | MFC: an open-source high-order multi-component flow solver | https://github.com/MFlowCode/MFC
relatedProjects: [swm]
relatedArticles: [spectral-element-notes]
relatedMethods: [compressible-multiphase]
summary: 这篇方法文章记录 MFC 多相流算例如何从分块 HDF5/Silo 输出进入网页图像、动画和诊断证据。
---

## 为什么单独记录工作流

MFC 算例的难点不只是生成一张图，而是把分块输出、变量重排、固定画布动画和诊断图组织成一条可追溯链路。这样项目页展示的每个结论都能回到源文件和后处理脚本 [cite:mfc-code]。

```bash
python3 postprocess/swm/generate_assets.py
```

## 固定画布

冲击波、多相界面和涡量结构都很依赖时间比较。动画如果每一帧的标题、色标或画布大小发生跳动，读者会把版式变化误读成物理变化。

:::result 页面原则
动画负责展示演化，静态图负责定位关键时刻，项目正文负责解释为什么这些证据支持结论。
:::

## 与项目的关系

这篇方法文章对应 `swm` 项目。项目文章展示具体研究问题和图像证据；方法文章只保留可以迁移到下一个 MFC 算例的后处理经验。

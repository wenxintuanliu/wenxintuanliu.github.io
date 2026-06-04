---
title: 谱元法网页化方法：从高阶场文件到可读证据
type: method
subtitle: Spectral Element Notes
category: Methods
status: working
publishedAt: 2026-05-30
updatedAt: 2026-05-30
readingMinutes: 6
tags: [数值方法]
projects: [lid-obstacle]
methods: [spectral-element]
references: [nek5000-theory, nekrs-theory]
referenceItems:
  - nek5000-theory | Nek5000 Theory Documentation | https://nek5000.github.io/NekDoc/theory.html
  - nekrs-theory | NekRS Theory Documentation | https://nekrs.readthedocs.io/en/latest/theory.html
relatedProjects: [lid-obstacle]
relatedArticles: [compressible-multiphase-workflow]
relatedMethods: [spectral-element]
summary: 这篇方法文章说明为什么本站的 Nek/NekRS 项目优先使用 pysemtools probes 做谱元插值，而不是把高阶场文件当作普通散点数据处理。
---

## 为什么要保留“计算到图像”的链路

谱元法的网页展示不能只追求好看的图片。每张图都应该能回到计算场、采样平面、插值方式和导出脚本，否则页面只是在展示图像，而不是展示研究证据 [cite:nek5000-theory]。

| 内容类型 | 页面职责 |
| --- | --- |
| 项目文章 | 解释研究问题、证据和限制 |
| 方法文章 | 记录可迁移的采样、插值和导出流程 |

当前 `lid-obstacle` 项目把网页资产视为后处理产物：原始场文件由 Nek5000 生成，采样由 pysemtools Probes 完成，最终 PNG/GIF 只是可读层。

:::result 可检查的结果
项目页中的图像、采样设置、源文件编号和复现命令要能互相对应。这样以后新增图像或修正参数时，不需要重新设计页面结构。
:::

## 手写内容的最低要求

- 保留采样平面、网格分辨率、时间点和源文件编号。
- 图注写清楚图像展示的变量、切片和后处理方法。
- 项目页把关键参数、复现命令和限制条件放在正文或附录中，而不是藏在脚本里。

![Lid cavity vorticity](assets/projects/lid-obstacle/vorticity-z010-spectral512.gif "Nek5000 顶盖驱动方腔 z = 0.1 切片涡量时间序列。")

## 什么时候补交互

交互只在能帮助读者检查假设时加入。例如时间帧切换、工况切换和图像对照可以保留；纯装饰性动效不应该进入正文。

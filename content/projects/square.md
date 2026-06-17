---
title: 方柱绕流的非定常数值模拟
type: project
subtitle: Nek5000 / 方形截面柱体绕流
category: Computational Fluid Dynamics
status: seedling
publishedAt: 2026-06-03
updatedAt: 2026-06-04
readingMinutes: 5
tags: [项目文章]
pinned: false
hero: assets/projects/square/square_flow.gif
methods: [spectral-element]
projects: [cyl4, cylinder-hodmd, lid-obstacle]
references: [nek5000-docs]
referenceItems:
  - nek5000-docs | Nek5000 Documentation | https://nek5000.mcs.anl.gov/
relatedProjects: [cyl4, cylinder-hodmd, lid-obstacle]
relatedArticles: [spectral-element-notes]
relatedMethods: [spectral-element]
dataAvailability: 网页媒体资产保存在 assets/projects/square/；原始场文件（square0.f00*）位于 /home/chunfengfusu/Nek5000/run/square。
summary: Nek5000 求解二维方柱绕流的流场演化数据，展示涡脱落现象和尾迹结构分析。
---

## 研究背景与问题

方柱绕流（Flow past a square cylinder）是计算流体力学中经典的流体力学基准算例之一。与其圆形截面柱体不同，由于存在具有明显锐角的固定边界，方柱表面的分离点不再随着流动状态自由移动，而是固定在其迎风面的两个前缘角或者背风段的后缘角上。因此，方柱绕流产生的旋涡脱落特性（Vortex shedding）展现出了特有的拓扑结构与受力特征。

我们采用高精度谱元法开源流体求解器 **Nek5000** 对方柱绕流进行了数值模拟（仅仅是玩具模型）。

## 流场时空演化

数据包含了方柱近表面至下游远场区域的多次周期脱落时刻的数据。

下图展示了流场中绝对速度模（$|u|$）的时空演化情况，为了清晰捕捉方柱锐角带来的强剪切流场变化，通过抽取计算域内的瞬态切片制作了流动动画。在这里可以明显地观察到上下侧边界层在方柱角点发生分离，继而在尾迹区不稳定性放大并导致卡门涡街的呈现：

![方柱绕流速度模瞬态演化云图](assets/projects/square/square_flow.gif "方柱绕流二维截面速度模量演化动画（使用 Plasma 颜色映射）")

## 网格与求解

Nek5000 采用谱元法，网格在每一大单元（Hexahedral/Quadrilateral Element）内部利用 Gauss-Lobatto-Legendre (GLL) 积分点构建高阶多项式插值。
- 在方柱所在的中心区域（$x \in [-0.5, 0.5]$， $y \in [-0.5, 0.5]$），网格进行了适当的加密，以便精确捕获钝体前缘的分离剪切层。
- 求解过程基于不可压 Navier-Stokes 方程。速度采用速度连续的 $P_N$ 逼近，压力采用 $P_{N-2}$ 。


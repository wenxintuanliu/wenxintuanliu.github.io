---
title: 谱元法：高阶单元里的不可压流动
type: method
subtitle: Spectral Element Method
category: Methods
status: working
publishedAt: 2026-05-30
updatedAt: 2026-07-04
readingMinutes: 9
tags: [数值方法]
projects: [lid-obstacle, ldc, square, be, cyl4]
methods: [spectral-element]
references: [patera-sem, nek5000-theory, nekrs-theory, nekrs-paper, karniadakis-sherwin]
referenceItems:
  - patera-sem | A spectral element method for fluid dynamics: laminar flow in a channel expansion | https://doi.org/10.1016/0021-9991(84)90128-1
  - nek5000-theory | Nek5000 Theory Documentation | https://nek5000.github.io/NekDoc/theory.html
  - nekrs-theory | NekRS Theory Documentation | https://nekrs.readthedocs.io/en/latest/theory.html
  - nekrs-paper | NekRS, a GPU-Accelerated Spectral Element Navier-Stokes Solver | https://arxiv.org/abs/2104.05829
  - karniadakis-sherwin | Spectral/hp Element Methods for Computational Fluid Dynamics | https://global.oup.com/academic/product/spectralhp-element-methods-for-computational-fluid-dynamics-9780198528692
relatedProjects: [lid-obstacle, ldc, square, be, cyl4]
relatedArticles: [compressible-multiphase-workflow]
relatedMethods: [spectral-element]
summary: 从不可压 Navier-Stokes 方程、GLL 节点和弱形式出发，整理谱元法的高阶离散结构。
---

## 从方程开始

谱元法同时保留了有限元的几何适应能力和谱方法的高阶精度。Patera 最早把 spectral element method 系统用于流体问题 [cite:patera-sem]，后来这条路线在 Nek5000 和 NekRS 中发展成成熟的不可压 Navier-Stokes 求解框架 [cite:nek5000-theory] [cite:nekrs-paper]。

不可压流动的基本方程为

$$
\nabla \cdot \mathbf{u} = 0 .
$$

$$
\frac{\partial \mathbf{u}}{\partial t}
+ \mathbf{u}\cdot\nabla\mathbf{u}
=
-\nabla p
+ \nu \nabla^2 \mathbf{u}
+ \mathbf{f} .
$$

若以长度尺度、速度尺度和时间尺度无量纲化，黏性项通常写成

$$
\frac{1}{Re}\nabla^2 \mathbf{u}.
$$

其中 Reynolds 数为

$$
Re = \frac{U L}{\nu}.
$$

这个量决定了问题的大致性格：低 Reynolds 数下，黏性控制主要结构；高 Reynolds 数下，边界层、剪切层和小尺度涡结构开始变得敏感。谱元法的高阶精度，恰好适合在相对规整但又带复杂边界的几何里解析这些结构。

## 单元内部不是线性的

谱元法先把区域分成若干四边形或六面体单元。与低阶有限元不同，每个单元内部使用高阶 Lagrange 基函数。以三维六面体单元为例，在参考坐标中写作

$$
(r,s,t) \in [-1,1]^3 .
$$

速度近似为

$$
\mathbf{u}_h^e(r,s,t)
=
\sum_{i=0}^{N}
\sum_{j=0}^{N}
\sum_{k=0}^{N}
\mathbf{u}_{ijk}^e
\ell_i(r)\ell_j(s)\ell_k(t).
$$

这里的基函数满足插值条件

$$
\ell_i(r_j) = \delta_{ij}.
$$

节点通常取 Gauss-Lobatto-Legendre 点。这样，一个单元里有

$$
(N+1)^3
$$

个三维节点。宏观单元数增加会改进几何和局部分辨率，多项式阶数增加会提高单元内部的解析能力。两者共同决定有效自由度和可解析尺度。

## GLL 求积

谱元法常把插值点和积分点放在同一组 GLL 节点上。单元积分可近似为

$$
\int_{\Omega^e} q(\mathbf{x})\,d\Omega
\approx
\sum_{i=0}^{N}
\sum_{j=0}^{N}
\sum_{k=0}^{N}
w_i w_j w_k
q(r_i,s_j,t_k)
J^e(r_i,s_j,t_k).
$$

其中 Jacobian 为

$$
J^e =
\det
\left(
\frac{\partial \mathbf{x}}{\partial(r,s,t)}
\right).
$$

这件事看似只是数值积分，其实影响很大。它让质量矩阵接近对角结构，也让张量积运算可以高效实现。Nek5000 和 NekRS 的速度，很大程度来自这种高阶结构和张量积算子的配合 [cite:nekrs-theory]。

## 弱形式

令测试函数为

$$
\mathbf{v}_h,\quad q_h .
$$

不可压方程的弱形式可以写成

$$
\left(
\mathbf{v}_h,
\frac{\partial \mathbf{u}_h}{\partial t}
\right)
+
\left(
\mathbf{v}_h,
\mathbf{u}_h\cdot\nabla\mathbf{u}_h
\right)
+
\nu
\left(
\nabla \mathbf{v}_h,
\nabla \mathbf{u}_h
\right)
-
\left(
\nabla\cdot\mathbf{v}_h,
p_h
\right)
=0 .
$$

不可压约束为

$$
\left(
q_h,
\nabla\cdot\mathbf{u}_h
\right)
=0 .
$$

这两个式子对应谱元法的一个基本事实：场数据不是散点集合，而是定义在一组高阶单元空间里的函数。后处理时如果无视单元映射和高阶插值，只把节点当散点重新插值，容易在单元边界和壁面附近制造额外误差。

## 采样应当尊重高阶空间

如果需要在某个点取值，首先应找到该点所在单元，再映射回参考坐标。设采样点对应的参考坐标为

$$
(r_p,s_p,t_p).
$$

则速度值应由单元内的高阶插值给出：

$$
\mathbf{u}_h(\mathbf{x}_p)
=
\sum_{i=0}^{N}
\sum_{j=0}^{N}
\sum_{k=0}^{N}
\mathbf{u}_{ijk}^e
\ell_i(r_p)\ell_j(s_p)\ell_k(t_p).
$$

中心线、切片、平均剖面和流线图，本质上都依赖这个步骤。高阶求解器的后处理不只是“画图”，而是在离散函数空间中重新评价解。

## 时间平均和涡量

很多流动结构不是瞬时场能说明的。时间平均速度定义为

$$
\overline{\mathbf{u}}(\mathbf{x})
=
\frac{1}{T_2-T_1}
\int_{T_1}^{T_2}
\mathbf{u}(\mathbf{x},t)\,dt .
$$

二维切片上的法向涡量常写作

$$
\omega_z
=
\frac{\partial v}{\partial x}
-
\frac{\partial u}{\partial y}.
$$

在谱元法中，这些导数也来自高阶基函数，而不是来自像素图上的差分。只要网格、时间步和统计窗口合理，涡量图和平均流线图就不仅是视觉结果，也可以作为数值证据。

## 我对谱元法的理解

谱元法并不神秘。它的优点可以概括为三句话。

第一，几何由单元处理；第二，单元内部由高阶多项式处理；第三，导数、积分和采样都尽量在同一个高阶空间里完成。

这种方法的代价也很清楚：网格质量、边界层分辨率、时间推进和滤波设置都会直接影响结果。高阶方法给出了更高的精度上限，同时也要求离散参数写得足够清楚。Karniadakis 和 Sherwin 的 spectral/hp element 体系对这一点讲得很清楚 [cite:karniadakis-sherwin]。

---
title: Re=1000 与 Re=10000 三维顶盖驱动方腔流
type: project
subtitle: Nek5000 / 3D lid-driven cavity benchmark and high-Re case
category: High-fidelity cavity flow
status: working
publishedAt: 2026-07-03
updatedAt: 2026-07-04
readingMinutes: 8
tags: [项目文章]
pinned: false
hero: assets/projects/ldc/center_line_re1000xi_albensoeder_kuhlmann.png
methods: [spectral-element]
projects: [lid-obstacle, be]
references: [botella-peyret-ldc, bouffanais-ldc, albensoeder-kuhlmann-ldc, nek5000-theory]
referenceItems:
  - botella-peyret-ldc | Benchmark spectral results on the lid-driven cavity flow | https://doi.org/10.1016/S0045-7930(98)00002-4
  - bouffanais-ldc | Large-eddy simulation of the lid-driven cubic cavity flow by the spectral element method | https://doi.org/10.1016/j.jcp.2007.03.032
  - albensoeder-kuhlmann-ldc | Albensoeder and Kuhlmann (2005) three-dimensional lid-driven cavity benchmark | local benchmark data cited in figure comparison
  - nek5000-theory | Nek5000 Theory Documentation | https://nek5000.github.io/NekDoc/theory.html
relatedProjects: [lid-obstacle, be]
relatedArticles: [spectral-element-notes]
relatedMethods: [spectral-element]
dataAvailability: 图像与配置文件保存在 assets/projects/ldc/；Re=1000 与 Re=10000 的 Nek5000 配置文件分别保存在 assets/projects/ldc/1000/ 与 assets/projects/ldc/10000/。
summary: 使用 Nek5000 谱元法计算三维顶盖驱动方腔流；Re=1000 与 Albensoeder-Kuhlmann 基准数据对比，Re=10000 采用高阶正则化顶盖速度并记录中心线与 y=0.5 截面结构。
---

## 问题

顶盖驱动方腔流是一个很适合检查数值方法细节的算例。几何简单，所有壁面都在单位立方体内，但顶盖与静止侧壁交界处会带来强剪切和角点奇异；雷诺数升高以后，腔体内部还会出现更薄的边界层、更强的二次涡以及明显的三维结构。

这里整理两个三维工况：Re=1000 用标准顶盖速度做基准验证，Re=10000 采用高阶正则化顶盖速度来减弱角点不连续对计算的影响。方腔内不可压 Navier-Stokes 方程写作

$$
\nabla\cdot \mathbf{u}=0,\qquad
\frac{\partial \mathbf{u}}{\partial t}
+\mathbf{u}\cdot\nabla\mathbf{u}
=-\nabla p+\frac{1}{Re}\nabla^2\mathbf{u}.
$$

速度以顶盖中心速度 $U_0$ 无量纲化，长度以方腔边长 $L$ 无量纲化，因此

$$
Re=\frac{U_0L}{\nu}.
$$

## 顶盖边界

Re=1000 工况使用标准顶盖边界：顶盖沿 x 方向以单位速度运动，其余壁面为无滑移静止壁面。这个设置保留了经典 lid-driven cavity 的角点不连续，因此更适合直接和 Albensoeder 与 Kuhlmann 的三维基准数据对比 [cite:albensoeder-kuhlmann-ldc]。

Re=10000 工况中，顶盖速度在靠近侧壁时平滑衰减到零，采用 Botella-Peyret 和 Bouffanais 等文献中常见的高阶正则化多项式形式 [cite:botella-peyret-ldc] [cite:bouffanais-ldc]：

$$
u(x,y,z=1)=U_0
\left[1-(2x-1)^{18}\right]^2
\left[1-(2y-1)^{18}\right]^2,
\qquad v=w=0 .
$$

这个分布在顶盖中心区域接近 $U_0$，在四周侧壁附近平滑降到零。正则化顶盖主要用于减弱高雷诺数下的角点不连续，方腔主驱动仍然来自顶盖中心区域。

![顶盖高阶正则化速度剖面](assets/projects/ldc/多项式顶盖.png "Re=10000 工况采用的高阶多项式顶盖速度剖面；中心区域接近 U0，靠近侧壁时平滑衰减。")

## 网格与求解

两个工况都使用 Nek5000 谱元法 [cite:nek5000-theory]。配置文件保存在 `assets/projects/ldc/1000/` 和 `assets/projects/ldc/10000/`，每个目录都包含 `ldc.msh`、`ldc.par`、`ldc.usr` 和 `SIZE`。宏观六面体单元在 x、y、z 三个方向采用双曲正切拉伸，让更多单元靠近壁面和角点区域。宏观网格节点可写成

$$
x_i=\frac{L}{2}\left[
1+\frac{\tanh\left(\zeta\left(\frac{2i}{N-1}-1\right)\right)}
{\tanh(\zeta)}
\right],
\qquad 0\le i\le N-1 .
$$

其中 $N$ 是该方向的宏观节点数，$\zeta$ 控制拉伸强度。Re=1000 工况取 $N=11$、$\zeta=1.3$，对应 $10^3$ 个宏观六面体单元；Re=10000 工况取 $N=25$、$\zeta=1.5$，对应 $24^3=13824$ 个宏观六面体单元。两个网格均为 Gmsh 2.2 格式，physical group 中 `volume` 为体单元，`v` 为运动顶盖，`walls` 为静止壁面。

从 `ldc.msh` 统计得到，Re=1000 网格包含 4961 个 Gmsh 节点、1000 个 HEX20 体单元和 600 个 QUAD8 边界面，其中运动顶盖边界面 100 个、静止壁面边界面 500 个。Re=10000 网格包含 60625 个 Gmsh 节点、13824 个 HEX20 体单元和 3456 个 QUAD8 边界面，其中运动顶盖边界面 576 个、静止壁面边界面 2880 个。`SIZE` 中两个工况均取 `lx1=8`，也就是每个方向 8 个 GLL 点、速度多项式阶数为 7；Re=1000 的全局单元上限为 1100，Re=10000 的全局单元上限为 13900。

求解器设置上，两者都求解不可压 Navier-Stokes 方程，开启 dealiasing，压力残差阈值为 1e-7，速度残差阈值为 1e-8，密度为 1。Nek5000 参数文件中使用负黏度写法指定雷诺数：Re=1000 对应 `viscosity=-1000`，Re=10000 对应 `viscosity=-10000`。Re=1000 固定时间步长为 0.001，计算到 t=300；Re=10000 从 `ins.f00001` 继续计算，固定时间步长为 0.0004，计算到 t=2500。

输出和监测也按两个工况分别设置。Re=1000 在 t=299 到 300 的末段输出瞬时场，间隔为 1；Re=10000 在 t=2480 到 2500 的末段输出更密集的瞬时场，间隔为 0.02。两个工况都保留每 20 个无量纲时间的粗间隔场输出，每 0.004 采样 history points，并每 0.02 记录体平均动能。后处理主要关注 y=0.5 中截面，以及穿过腔体中心的速度剖面。

## Re=1000 基准验证

Re=1000 主要用于基准验证。我提取了 y=0.5 剖面上的两条中心线速度：一条是 $u(0.5,0.5,z)$，另一条是 $w(x,0.5,0.5)$，并与 Albensoeder 和 Kuhlmann 基于切比雪夫配点法给出的三维基准数据进行对比。

误差用相对偏差表示：

$$
\varepsilon_{\mathrm{rel}}=
\frac{|q_{\mathrm{Nek5000}}-q_{\mathrm{ref}}|}
{|q_{\mathrm{ref}}|}\times 100\%.
$$

在图中标出的三个代表位置，分别得到 0.007%、0.009% 和 0.005% 的相对误差。这个量级表明 Re=1000 工况不仅在整体流线形态上合理，也能在中心线速度这种更严格的基准量上对齐高精度结果。

![Re=1000 中心线速度与 Albensoeder-Kuhlmann 基准对比](assets/projects/ldc/center_line_re1000xi_albensoeder_kuhlmann.png "Re=1000 中心线速度剖面，在 (0.5,0.1242)、(0.1091,0.5)、(0.9096,0.5) 位置与基准数据的相对误差分别为 0.007%、0.009%、0.005%。")

y=0.5 平面上的矢量图显示，主涡占据方腔中心区域，角落附近出现次级回流。这与三维方腔流在中截面上的经典结构一致。

![Re=1000 的 y=0.5 中截面矢量场](assets/projects/ldc/1000plane_y05_vector_velocity.png "Re=1000 工况在 y=0.5 平面上的速度矢量与速度模分布。")

## Re=10000 结果

Re=10000 工况的中心线速度剖面比 Re=1000 更陡，近壁区域速度梯度明显增强。正则化顶盖让顶盖中心区域仍保持主要驱动作用，同时降低四个顶盖角附近的边界不连续强度，因此更适合观察高雷诺数下腔体内部的大尺度结构。

![Re=10000 中心线速度剖面](assets/projects/ldc/center_line_re10000.png "Re=10000 工况在 y=0.5 剖面上的中心线速度结果。")

从 y=0.5 截面看，主涡被更强的剪切层压缩，壁面附近速度变化更集中，角落回流结构也比 Re=1000 更清楚。同一套网格拉伸和谱元离散推进到更高雷诺数后，仍能给出比较干净的中心截面结构。

![Re=10000 的 y=0.5 中截面矢量场](assets/projects/ldc/10000plane_y05_vector_velocity.png "Re=10000 工况在 y=0.5 平面上的速度矢量与速度模分布。")

这两个工况放在一起，形成了一个由验证到高雷诺数计算的过渡：先用 Re=1000 和高精度基准数据检查 Nek5000 设置，再把同样的网格拉伸和谱元离散推进到 Re=10000。后续含障碍物方腔流和城市冠层算例，也可以拿它作为较干净的基线。

---
title: 方柱绕流的非定常数值模拟
type: project
subtitle: Nek5000 / Flow past a square cylinder at Re = 200
category: Computational Fluid Dynamics
status: seedling
publishedAt: 2026-06-03
updatedAt: 2026-07-04
readingMinutes: 7
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
dataAvailability: 图像与动画保存在 assets/projects/square/；Nek5000 配置、网格和原始场文件位于 /home/chunfengfusu/Nek5000/run/square。
summary: Nek5000 二维方柱绕流算例，Re=200，4008 个二次四边形谱元，记录方柱锐角分离后的周期尾迹和卡门涡街。
---

## 问题

方柱绕流是钝体绕流中很有代表性的基准问题。和圆柱不同，方柱表面的分离点受到前缘和后缘锐角约束，不会像圆柱那样随雷诺数和边界层状态连续移动。因此，方柱尾迹里的剪切层、涡脱落相位和回流区结构都带有更清楚的几何印记。

这个算例使用 Nek5000 求解二维不可压 Navier-Stokes 方程：

$$
\nabla\cdot \mathbf{u}=0,\qquad
\frac{\partial \mathbf{u}}{\partial t}
+\mathbf{u}\cdot\nabla\mathbf{u}
=-\nabla p+\frac{1}{Re}\nabla^2\mathbf{u}.
$$

以方柱边长 $D=1$ 和入口速度 $U_\infty=1$ 无量纲化，黏性系数取 $\nu=0.005$，因此

$$
Re=\frac{U_\infty D}{\nu}=200.
$$

这个雷诺数下尾迹已经进入非定常涡脱落，同时流动结构还不至于过分复杂，适合用来检查网格、边界条件、重启计算和后处理动画是否一致。

## 网格

计算域为 $x\in[-5,15]$、$y\in[-5,5]$。方柱位于中心区域，边长为 1；上游给出 5D 的入口发展距离，下游保留 15D 的尾迹空间，便于观察涡列从近尾迹向远尾迹输运。

网格文件为 Gmsh 2.2 格式，physical group 包含 `Inlet`、`Outlet`、`Farfield`、`Square` 和 `Fluid`。统计 `square.msh` 得到：

- Gmsh 节点数：12356
- 流体体单元：4008 个 QUAD8 二次四边形单元
- 边界线单元：332 个二次线单元
- 边界划分：入口 52、出口 52、远场 164、方柱壁面 64

Nek5000 读取 `square.re2` 后确认全局流体单元数为 4008。速度网格取 `lx1=7`，压力网格为 `lx2=5`，对应 $P_N-P_{N-2}$ 谱元离散；dealiasing 使用 `lxd=10`。日志中给出的 GLL 最小/最大网格间距为 $1.16\times 10^{-3}$ 到 $1.26\times 10^{-1}$，网格在方柱角点和近尾迹区域明显加密。

## 求解设置

边界条件按网格物理编号映射为：

$$
\begin{aligned}
\Gamma_{\mathrm{in}} &: \mathbf{u}=(1,0),\\
\Gamma_{\mathrm{out}} &: \text{outlet},\\
\Gamma_{\mathrm{far}} &: \text{symmetry},\\
\Gamma_{\mathrm{wall}} &: \mathbf{u}=(0,0).
\end{aligned}
$$

`square.usr` 中入口和初始场均设为 $u=1,\ v=0$。`square.par` 中时间推进采用 BDF3，时间步长为 $4\times10^{-4}$，速度和压力残差阈值均为 $10^{-8}$。计算从已有场 `square0.f00028` 重启，重启时刻为 $t=99$，继续推进 500000 步，最终到达约 $t=299$。输出间隔为 5000 步，因此后处理目录中保留了 100 个场文件。

这组设置围绕一个经典非定常尾迹问题展开：从 Gmsh 二次网格、Nek5000 谱元计算、重启长时间积分，到最后的速度模动画。

## 流场演化

下图记录速度模 $|\mathbf{u}|$ 的瞬态演化。方柱上下两侧剪切层从锐角处分离，在近尾迹中交替卷起，并向下游形成周期性的卡门涡街。

![方柱绕流速度模瞬态演化云图](assets/projects/square/square_flow.gif "Re=200 方柱绕流二维速度模演化动画；流场由 Nek5000 的 square0.f* 输出文件渲染。")

从动画中可以看到，方柱几何把分离位置固定在角点附近，尾迹相位和几何边界的联系比圆柱绕流更直接。这个算例足够简单，可以检查谱元网格与边界条件；同时又有清楚的非定常脱落，能够检验高阶方法在钝体尾迹问题中的时间推进和场输出。

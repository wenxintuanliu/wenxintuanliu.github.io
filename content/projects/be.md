---
title: 444 交错立方体阵列的 Nek5000 / nekRS 复现
type: project
subtitle: Re = 5000 urban-like cubical obstacles benchmark
category: High-order CFD benchmark
status: working
publishedAt: 2026-07-04
updatedAt: 2026-07-04
readingMinutes: 9
tags: [项目文章, Nek5000, nekRS, 城市冠层, 湍流统计]
pinned: false
hero: assets/projects/be/mean_streamline_z0p5_be0.png
methods: [spectral-element]
projects: []
references: [coceal2006, nek5000-theory, nekrs-theory]
referenceItems:
  - coceal2006 | Coceal et al. 2006, Mean Flow and Turbulence Statistics Over Groups of Urban-like Cubical Obstacles | https://doi.org/10.1007/s10546-006-9076-2
  - nek5000-theory | Nek5000 Theory Documentation | https://nek5000.github.io/NekDoc/theory.html
  - nekrs-theory | NekRS Theory Documentation | https://nekrs.readthedocs.io/en/latest/theory.html
relatedProjects: [ldc, lid-obstacle]
relatedArticles: [spectral-element-notes]
relatedMethods: [spectral-element]
dataAvailability: 图像与 Nek5000 输入文件已整理在项目资产目录；nekRS 原始统计场体积较大，未随站点发布。
summary: 用 Nek5000 与 GPU 版 nekRS 复现 Coceal 等人 444 交错立方体阵列 DNS，比较网格、显式滤波与 hpfrt 正则化对平均速度和湍流统计的影响。
---

## 项目概览

　　这个项目围绕 Coceal、Thomas、Castro 和 Belcher 的城市冠层经典算例展开：在 $4H \times 4H \times 4H$ 的周期计算域中布置交错立方体粗糙元，研究平均流、湍流统计和建筑物阵列中的动量交换 [cite:coceal2006]。它比普通管道流或方腔流更接近真实复杂几何，也很适合检验高阶谱元方法在壁面、尖角和冠层回流区域中的表现。

　　我用两套求解器做了同一个基准问题。Nek5000 侧重网格与显式滤波的可控性，nekRS 侧重 GPU 高阶计算和 hpfrt 正则化的敏感性。两条路线都采用不可压 Navier-Stokes 方程，立方体高度取 $H=1$，计算域为 $x,y,z \in [0,4]$，运动黏度为 $\nu=1/500$，流动由 $x$ 方向体力驱动。

![nekRS be0 mean streamline at z/H = 0.5](assets/projects/be/mean_streamline_z0p5_be0.png "nekRS be0 工况在 $z/H=0.5$ 平面的平均流线图。彩色区域为平面内平均速度模，黑色曲线为平均流线，灰色区域为立方体固体区域。")

　　水平切片显示了交错阵列中很典型的冠层内流动结构：主流在建筑物之间被迫绕行，形成连续的高速蛇形通道；建筑物背风侧和通道扩张区出现低速回流。这也是这个算例有价值的地方：如果只看垂向平均剖面，会漏掉很多由几何排布引起的空间非均匀结构。

![nekRS be0 mean streamline at y/H = 2.0](assets/projects/be/mean_streamline_y2p0_be0.png "nekRS be0 工况在 $y/H=2.0$ 平面的平均流线图。彩色区域为 $x-z$ 平面内平均速度模，黑色曲线为平均流线，灰色区域为立方体固体区域。")

　　中截面给出了建筑物高度附近的回流和上方较均匀的主流。立方体顶部附近的剪切层把冠层内部低速区和上方高速区分开；只看一个垂向平均速度剖面，很难交代这部分三维结构。

## 基准对象

　　原论文把这类流动放在城市粗糙面和冠层流框架下讨论。平均速度不仅随高度变化，也随平面位置显著变化；因此在冠层内部，空间平均后的 dispersive stress 不能被简单忽略，而冠层上方则更多由 Reynolds stress 主导 [cite:coceal2006]。这个物理背景决定了复现工作不能只追求一个稳定的速度场，还要关注平均结构、网格分辨率和滤波设置是否共同支持统计判断。

　　本项目采用与论文 444 交错阵列一致的无量纲几何尺度。顶部为滑移/对称边界，地面和立方体表面为无滑移壁面，水平方向保持周期性。几何和边界固定后，主要变量就剩下求解器、网格和稳定化策略，Nek5000 与 nekRS 的差异也更容易分开看。

## 工况设计

| 工况 | 求解器 | 网格与阶数 | 滤波 / 正则化 | 作用 |
| --- | --- | --- | --- | --- |
| be444mi | Nek5000 | 二阶六面体网格，3840 个体单元，$H/4$ 级别分辨率，速度点阶数 9 | 显式滤波强度 0.05，滤波模态 2 个 | 作为 Nek5000 细网格对照 |
| be444xi | Nek5000 | 二阶六面体网格，480 个体单元，$H/2$ 级别分辨率，速度点阶数 9 | 显式滤波强度 0.05，滤波模态 2 个 | 检查粗网格对平均剖面的影响 |
| be444bian | Nek5000 | 二阶六面体网格，592 个体单元，$x/y$ 方向较粗，$z$ 向变间距，速度点阶数 8 | 显式滤波强度 0.05，滤波模态 2 个 | 观察竖向布点对冠层剪切层的影响 |
| nekRS be0 | nekRS | 4800 个谱元，多项式阶数 8 | 不启用 hpfrt | GPU 版无正则化基准 |
| nekRS be1 | nekRS | 与 be0 相同 | hpfrt，系数 5 | 弱正则化对照 |
| nekRS be2 | nekRS | 与 be0 相同 | hpfrt，系数 10 | 强正则化对照 |

　　这六个工况的设计思路比较清楚：Nek5000 侧把滤波固定住，主要看网格；nekRS 侧把网格固定住，主要看正则化强度。这样可以避免把“网格不够”“滤波过强”“求解器差异”混在一起讨论。

## 求解器对照

　　Nek5000 的优势在于输入结构清晰，适合逐项检查边界、体力、黏度和滤波设置。这里三个 Nek5000 工况都只求解不可压速度压力场，关闭标量输运，把注意力集中在平均速度和湍流统计上。细网格 be444mi 的单元数量明显高于 be444xi；be444bian 则保留较粗的水平布点，同时在竖直方向调整分布，用来观察冠层顶部剪切层是否更敏感。

　　nekRS 的优势在于高阶 GPU 计算和长时间统计。三个 nekRS 工况使用相同几何、相同黏度、相同体力和相同网格，只改变 hpfrt 正则化强度。be0 不加 hpfrt，be1 和 be2 分别采用较弱和较强的正则化。这个对照主要用来观察正则化对平均结构的影响幅度。

## 结果

![Nek5000 profile comparison](assets/projects/be/exact_profile_plot_multi_be.png "Nek5000 三个 444 交错阵列网格的剖面对比图。be444mi 为 $H/4$ 级别网格，be444xi 为 $H/2$ 级别网格，be444bian 为 $x/y$ 方向较粗且 $z$ 向变间距网格；三者均启用相同显式滤波。")

　　剖面对比图用 Nek5000 的三个网格工况检查平均统计量对网格分辨率和竖向布点的敏感性。对于这种带尖角障碍物的冠层流，近壁和建筑物顶部附近的局部误差很容易传导到整体剖面，因此同一几何下的网格对照是必要的。

　　两张平均流线图补充了剖面图看不到的信息。$z/H=0.5$ 平面给出冠层内部的横向绕流和局部回流，$y/H=2.0$ 平面给出建筑物高度附近的剪切层和上方主流。高速带不是笔直穿过计算域，而是被交错立方体持续偏转；平均流结构本身就是三维的，这也对应了原论文对 dispersive stress 的讨论。

　　在目前这组结果中，Nek5000 的细网格和 nekRS 的无 hpfrt 工况给出了可以互相参照的平均流结构；粗网格与竖向变间距工况主要反映剖面量的网格敏感性，nekRS 的 be1/be2 则用于观察 hpfrt 对统计量的影响。

---
title: 圆柱绕流的 GCN-AE 降维与重构
type: project
subtitle: NekRS z=2 plane / Graph Convolutional Autoencoder
category: Graph Reduced-Order Modeling
status: seedling
publishedAt: 2026-05-09
updatedAt: 2026-07-04
readingMinutes: 8
tags: [项目文章]
pinned: true
hero: assets/projects/cyl4/flow-evolution.gif
methods: [graph-convolutional-network, autoencoder-rom, spectral-element]
projects: [cylinder-hodmd, lid-obstacle]
references: [kipf-gcn, autoencoder-rom]
referenceItems:

  - kipf-gcn | Semi-Supervised Classification with Graph Convolutional Networks | https://arxiv.org/abs/1609.02907
  - autoencoder-rom | Autoencoders and reduced-order modeling for nonlinear dynamical systems | https://doi.org/10.1016/j.jcp.2019.108973
relatedProjects: [cylinder-hodmd, lid-obstacle]
relatedArticles: [gcn-notes, autoencoder-notes, spectral-element-notes]
relatedMethods: [graph-convolutional-network, autoencoder-rom, spectral-element]
dataAvailability: 图像与动画保存在 assets/projects/cyl4/；原始 NekRS 算例、z=2 平面 HDF5 数据与 GCN-AE 模型输出来自 /home/chunfengfusu/NekRS_run/cyl。
summary: NekRS 三维圆柱绕流在 z=2 平面的图自编码实验；401 个快照、23778 个图节点、94356 条有向边，二维 latent 坐标重构验证段速度场。
---

## 学习目的

在学习线性降维技术时，我早听说并使用了在流体力学降维的重要工具 POD，也在很多论文中看过 POD 与其他技术的融合。但在 PIV 实验数据或者某些很混乱的数据中利用 DMD（以 POD/SVD 为基础），我发现流速的奇异值分布往往不是快速衰减，存在科尔格莫洛夫障壁，这就导致用很少的模态不能精确表达出现实流场，失去了“简洁”和“方便解释”的意义。

降维技术的吸引力在于，它试图用少量坐标保留原始流场中最主要的结构。后来查非结构网格数据的降维方法时，我开始接触 GCN-AE。NekRS 平面数据本来就不是规则图片，而是带节点连接关系的非均匀点集；图网络正好可以直接利用这种连接关系。

## 算例来源

这个项目完全基于同一套 NekRS 圆柱绕流算例。几何采用无量纲三维圆柱，直径 D=1，圆柱中心位于 x=0、y=0，展向长度为 4D。计算域为 x 从 -5D 到 15D，y 从 -5D 到 5D，z 从 0 到 4D；入口速度为 (1,0,0)，出口为 outflow，上下边界采用近似滑移/对称的远场处理，圆柱壁面为无滑移边界，z 方向为周期边界。当前参数文件中使用 NekRS 的 Re 写法，圆柱直径和入口速度取 1，对应 Re=100。

网格由 Gmsh 生成后转换为 NekRS 使用的 re2 文件。二维截面在圆柱附近采用 O-grid，外侧接矩形块；圆柱周向 32 个单元，壁面到 O-grid 外框径向 6 个单元，尾流方向外围块划分更长，z 方向挤出 6 层。三维网格共有 3900 个 HEX20 体单元、2056 个二次边界面，NekRS 谱元阶数为 6。圆柱边界的二阶边中点投影到真实圆弧上，因此近壁几何不是简单的直线近似。

时间推进采用 tombo3，时间步长为 0.002，压力和速度残差阈值分别为 1e-6 和 1e-7，并开启 dealiasing。这里使用已经发展起来的流场作为初始状态，从 t=120 继续计算到 t=200，每 0.2 个无量纲时间保存一次平面数据，因此后续 GCN-AE 使用的是 401 个连续快照。

## 平面数据与图结构

我从三维场中抽取 z=2 的中截面，只保留平面内速度分量 u 和 v。每个快照可以写成

$$
X(t)=\left[u(t),v(t)\right]\in\mathbb{R}^{23778\times 2}.
$$

这个平面包含 23778 个图节点和 94356 条有向边。图的邻接关系直接来自 NekRS 平面上的节点连接，所有节点都有相邻边，没有孤立点；节点入度主要在 2 到 5 之间。我没有先把流场插值成规则图片，而是保留谱元平面上的非均匀节点关系，让模型直接处理原始计算网格。

![NekRS z=2 平面速度模随时间演化](assets/projects/cyl4/flow-evolution.gif "NekRS z=2 平面速度模随时间演化，时间范围为 t=120 到 t=200。")

这段圆柱尾迹已经进入周期脱落状态：圆柱后方剪切层交替卷起，下游涡列保持清楚的相位推进。它不像完全湍流那样杂乱，也不是单个线性模态就能轻松表达的平面流场，适合作为图自编码器的试验对象。

![NekRS z=2 平面的图节点与邻接关系](assets/projects/cyl4/gcn-ae-graph-preview.png "z=2 平面上的 23778 个图节点和抽样显示的邻接边；圆形空白区域为圆柱截面。")

## GCN-AE 设置

模型使用 GCNConv 编码器读取速度场和静态图结构，再通过 mean/RMS readout 得到整张流场的低维状态。解码器把 latent 坐标和节点坐标一起作为输入，并用 Fourier 坐标特征帮助恢复空间分布。这里我把 latent dimension 设为 2，是一个比较严格的瓶颈：如果尾迹主要由周期相位控制，二维坐标应当足够形成接近闭合的相图；如果二维坐标不够，重构误差和相图都会很快暴露出来。

训练段使用前 301 个快照，验证段使用后 100 个快照。网络宽度为 64，GCN 层数为 2，坐标解码器隐藏层宽度为 256；训练时除了全场重构误差，还加入了很弱的 latent speed、latent acceleration 和 oscillator 约束，使隐变量不要在相邻快照之间产生不自然的跳动。

![GCN-AE 训练损失与最终重构误差](assets/projects/cyl4/gcn-ae-training-history.png "左侧为训练过程中的 total loss 和 reconstruction loss；右侧为训练段与验证段的最终相对 L2 重构误差。")

训练后，训练段全局相对 L2 误差为 3.05%，验证段为 3.05%；其中验证段 u 分量误差为 2.36%，v 分量误差为 9.30%。v 分量相对误差更大并不意外，因为横向速度幅值较小，而且对尾迹相位更敏感。

## 隐变量相图

二维 latent 坐标没有散成一团，而是形成了接近圆环的周期轨道。训练段和验证段在同一条轨道上继续前进，验证段没有突然跳到另一片区域，这一点比单独看训练误差更有意义。

![二维 latent phase portrait](assets/projects/cyl4/gcn-ae-latent-phase.png "二维 latent 相图，颜色表示无量纲时间；空心点为训练段和验证段分界。")

从数值上看，latent 角速度给出的周期约为 5.60 个无量纲时间，整个 t=120 到 t=200 的窗口中大约包含 14.3 个周期。训练段和验证段的半径变异系数分别约为 0.078 和 0.076。二维坐标基本沿同一条环形轨道推进，和圆柱尾迹的周期相位相对应。

## 重构质量

下面选取验证段最后一个快照，snapshot 400，对应 t=200。图中依次为 NekRS 参考速度模、GCN-AE 重构速度模和绝对误差。

![GCN-AE 重构质量：NekRS、GCN-AE 与绝对误差](assets/projects/cyl4/gcn-ae-reconstruction-t0400.png "验证段 snapshot 400 的速度模重构对比；误差集中在近尾迹和下游涡结构相位变化较快的位置。")

从图上看，二维瓶颈仍然能恢复主要剪切层和下游涡列，整体速度模分布与 NekRS 参考场接近。误差主要出现在圆柱后方的近尾迹和涡结构相位变化快的区域，这也符合我对这个问题的预期：大尺度周期结构比较容易被二维 latent 捕捉，而局部剪切层细节和横向速度分量更容易成为重构误差的来源。

这组结果给我的直接判断是：原始非均匀谱元节点可以直接组织成图，不必先插值成规则图像；在 Re=100 圆柱尾迹这种以周期脱落为主的流动中，二维 latent 坐标已经能形成清楚的相位变量。它还不能算完整的预测 ROM，但这个状态变量已经足够作为后续动力学识别的入口。

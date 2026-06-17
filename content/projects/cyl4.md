---
title: 圆柱绕流的 GCN-AE 降维与重构
type: project
subtitle: NekRS z=2 plane / Graph Convolutional Autoencoder
category: Graph Reduced-Order Modeling
status: seedling
publishedAt: 2026-05-09
updatedAt: 2026-06-09
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
dataAvailability: 网页媒体资产保存在 assets/projects/cyl4/；原始 HDF5 与模型输出位于 /home/chunfengfusu/NekRS_run/cyl2/z2_plane，本地路径在本文 front matter 中记录。
summary: NekRS 圆柱绕流 z=2 平面数据，501 个快照、23778 个图节点、二维速度分量 u/v。
---

## 学习目的

在学习线性降维技术时，我早听说并使用了在流体力学降维的重要工具————POD[lumely],并在很多论文中看过POD与其他技术的融合。但在PIV实验数据或者某些很混乱的数据中利用DMD(以POD(SVD)为基础)，我发现流速的奇异值分布往往不是快速衰减，存在科尔格莫洛夫障壁，这就导致用很少的模态不能精确表达出现实流场，失去了"简洁"和"方便解释"的意义。

降维技术是如此重要，能用较少的信息表达巨大的信息(超过我所想象的巨大)，神经网络的发展给它带来了机会。对于我非均匀数据(我经常使用nekRS),我从AI那了解到GCN-AE这一技术[]。

## 相关数据

这一页和 [圆柱绕流 HODMD 项目](pages/project.html?id=cylinder-hodmd) 用的是同一个 NekRS 圆柱绕流思路：从三维计算里抽出 `z = 2` 的平面，只是这里保留了 `t = 0` 到 `t = 100` 的更长时间序列。

$$
X(t)=\left[u(t),v(t)\right]\in\mathbb{R}^{N\times 2},\qquad N=23778 .
$$

每个时刻的状态就是这 `23778` 个节点上的二维速度。我把 [GCN 方法](pages/method.html?id=gcn-notes) 和 [Autoencoder 方法](pages/method.html?id=autoencoder-notes) 放在一起，AE 负责制造瓶颈，GCN 负责尊重非均匀网格上的邻接关系。

## 原始流场与图结构

HDF5 里保留了 `501` 个快照、`23778` 个节点、`94356` 条有向边，以及 `u/v` 两个速度分量。这段尾迹并不复杂到完全混乱：圆柱后方的剪切层周期性脱落，下游涡列向后输运，整体相位很清楚。但它也不简单到几个线性模态就一定可以舒服地表达。正是这种“有规律，但又不愿意被过度简化”的状态，把它拿来试 GCN-AE。

![原始 NekRS z=2 平面速度模云图随时间演化](assets/projects/cyl4/flow-evolution.gif "原始 NekRS z=2 平面速度模随时间演化；该 GIF 用于首页代表预览和项目卡片首图。")


一旦把数据硬塞进规则图像，后面的卷积网络当然更方便，但我也同时丢掉了“谱元计算本来长什么样”这个事实。GCN 的意义就在这里：它允许模型在原始节点关系上学习局部流动结构，而不是把网格问题先藏起来。

![NekRS z=2 平面的非结构图节点与邻接关系](assets/projects/cyl4/gcn-ae-graph-preview.png "NekRS z=2 平面的非结构图节点与邻接关系")

## GCN-AE 编码

这一版模型很朴素。编码器读入速度场和图结构，把整张流场压缩成低维坐标；解码器再结合这个 latent vector 和节点坐标，把速度场恢复到原来的平面上：

$$
z(t)=f_\theta(X(t),G),\qquad \hat{X}(t)=g_\phi(z(t),p),
$$

其中 $G$ 是静态图，$p$ 是节点坐标。我把 latent dimension 固定为 `8`，不是因为它已经被证明最优，而是先给模型一个足够窄的瓶颈，看看它会不会被迫学出尾迹相位和主要空间结构。

训练损失主要还是全场重构误差，只额外加了很弱的 latent acceleration regularization：

$$
\mathcal{L}
=\|\hat{X}-X\|_2^2
+\lambda\|z_{t+1}-2z_t+z_{t-1}\|_2^2 .
$$

这个正则项不是为了把动力学强行变成一条光滑曲线，而是稍微惩罚 latent 空间里不自然的抖动。训练历史里我最关心的也不是训练误差能降到多低，而是验证段有没有一起下降。如果验证误差不跟着走，那这个 AE 很可能只是在背快照。

![GCN-AE 训练与验证损失历史](assets/projects/cyl4/gcn-ae-training-history.png "GCN-AE 训练与验证损失历史")

## 隐变量轨迹

AE 的结果不能只看重构图。对 ROM 来说，latent space 本身也要像一个“状态空间”。如果 8 个坐标只是快照编号的复杂编码，那它重构得再好，也很难让我相信它学到了流动。

前四个 latent coordinates 的时间轨迹至少给了一个正面的信号：它们不是随机跳动的点，而是随时间连续演化，并且在训练/验证分界之后仍然保持周期性。换句话说，模型没有只在训练窗口里找到一套坐标暗号，它在验证段也沿着相似的相位轨道继续走。

![前四个 latent coordinates 的时间轨迹](assets/projects/cyl4/gcn-ae-latent-components.png "前四个 latent coordinates 随时间变化，虚线为训练/验证分界。")

相图会把这个感觉看得更直接一些。`z1-z2` 平面里能看到一段从初始过渡走向周期轨道的过程；虽然还有离群点和不够干净的段落，但主干结构已经不是一团散点。

![GCN-AE latent phase portrait](assets/projects/cyl4/gcn-ae-latent-phase.png "GCN-AE latent phase portrait；颜色表示从 t = 0 到 t = 100 的时间推进。")

:::result 当前判断
这一版 GCN-AE 学到的更像是随尾迹相位连续演化的低维坐标，而不是孤立快照索引。这还不能说明它已经具备可靠外推能力，但它至少给后续 ROM 或动力学识别提供了一个可以继续追问的状态变量。
:::

## 重构质量

最后还是要回到流场本身。下面选的是验证段 snapshot `450`，对应的时间大约是 `t = 90`。图里同时放了 NekRS 参考速度模、GCN-AE 重构速度模和绝对误差。

验证集全局相对 L2 误差为 `2.31e-2`；其中 `u` 分量相对误差约 `7.93e-3`，`v` 分量相对误差约 `1.01e-1`。这个结果对我来说不是“完美重构”，而是一个更有用的中间状态：大尺度尾迹被压进 8 维以后还能回来，但横向速度和相位敏感区域已经暴露出明显压力。

![GCN-AE 重构质量：参考速度模、重构速度模与绝对误差](assets/projects/cyl4/gcn-ae-reconstruction-t0450.png "同一验证快照的 NekRS 速度模、GCN-AE 重构速度模和绝对误差；图像保留真实非结构节点坐标。")

从图上看，主要剪切层和尾迹涡列的轮廓基本能恢复，说明 8 维瓶颈没有把最关键的流动结构完全压坏。误差集中在圆柱近尾迹和下游涡结构相位变化快的区域，这也比单独报一个全局误差更诚实：模型最先失手的地方，正是流场最敏感的地方。

## 我还不满意的地方

这页现在只是第一阶段的记录。我愿意相信 GCN-AE 有价值：

- 对 `latent_dim = 4 / 8 / 16 / 32` 做系统比较，看误差下降、相位结构和可解释性之间怎么取舍。
- 单独画 `u/v` 分量误差，尤其检查 `v` 分量为什么比 `u` 更难重构。
- 给圆柱近尾迹、下游涡列和远场分别做局部误差统计，不再只依赖全局相对 L2。
- 在确认 latent space 稳定之后，再接 SINDy、DMD 或 neural ODE 做外推；否则外推失败时，很难判断问题来自 AE 还是动力学模型。

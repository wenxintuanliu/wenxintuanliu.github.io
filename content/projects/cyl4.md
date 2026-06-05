---
title: 圆柱绕流的 GCN-AE 降维与重构
type: project
subtitle: NekRS z=2 plane / Graph Convolutional Autoencoder
category: Graph Reduced-Order Modeling
status: seedling
publishedAt: 2026-05-09
updatedAt: 2026-05-31
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

## 研究问题

圆柱绕流的 z=2 平面来自 NekRS 非结构谱元节点。这里的降维对象不是规则像素图，而是 `23778` 个节点上的二维速度场

$$
X(t)=\left[u(t),v(t)\right]\in\mathbb{R}^{N\times 2},\qquad N=23778 .
$$

目标是把完整流场编码成 8 维 latent vector，并在同一组非结构节点上解码回速度场。本页只展示 [GCN 方法](pages/method.html?id=gcn-notes) 与 [Autoencoder 方法](pages/method.html?id=autoencoder-notes) 的降维和重构效果；不展示 SINDy，也不展示 latent dynamics 外推。

## 原始流场与图结构

数据来自 `/home/chunfengfusu/NekRS_run/cyl2/z2_plane/data/cyl_z2_sindy.h5`。HDF5 保留 `501` 个快照、`23778` 个节点、`94356` 条有向边和 `u/v` 两个速度分量。Fig 1 先给出原始速度模的瞬态云图，让读者看到模型真正面对的周期尾迹，而不是先看到神经网络结果。

![原始 NekRS z=2 平面速度模云图随时间演化](assets/projects/cyl4/flow-evolution.gif "原始 NekRS z=2 平面速度模随时间演化；该 GIF 用于首页代表预览和项目卡片首图。")

GCN-AE 不把散点插值成规则网格，而是直接使用 z=2 平面的静态图结构。Fig 2 展示节点与邻接关系；这一步定义了图卷积的信息传播范围，也决定了 encoder 如何感知局部流动结构。

![NekRS z=2 平面的非结构图节点与邻接关系](assets/projects/cyl4/gcn-ae-graph-preview.png "NekRS z=2 平面的非结构图节点与邻接关系")

## GCN-AE 编码

训练脚本为 `/home/chunfengfusu/NekRS_run/cyl2/z2_plane/sindy/GNN_SINDY/01_train_gcn_autoencoder.py`。encoder 读入速度场与图结构，decoder 结合 latent vector 和节点坐标恢复速度：

$$
z(t)=f_\theta(X(t),G),\qquad \hat{X}(t)=g_\phi(z(t),p),
$$

其中 $G$ 是静态图，$p$ 是节点坐标。训练损失以全场重构误差为主，并加入很弱的 latent acceleration regularization：

$$
\mathcal{L}
=\|\hat{X}-X\|_2^2
+\lambda\|z_{t+1}-2z_t+z_{t-1}\|_2^2 .
$$

Fig 3 用训练历史检查模型是否稳定收敛。这里更关心验证段误差是否跟随训练误差下降，而不是单纯追求训练集拟合。

![GCN-AE 训练与验证损失历史](assets/projects/cyl4/gcn-ae-training-history.png "GCN-AE 训练与验证损失历史")

## 隐变量轨迹

如果 AE 只是在记忆快照，latent coordinates 往往会呈现离散、跳变或无序结构。Fig 4 显示前四个 latent coordinates 的时间演化；轨迹连续，并且能分辨训练/验证分界之后的周期演化。

![前四个 latent coordinates 的时间轨迹](assets/projects/cyl4/gcn-ae-latent-components.png "前四个 latent coordinates 随时间变化，虚线为训练/验证分界。")

:::result 当前结论
GCN-AE 学到的不是孤立快照索引，而是一个随尾迹相位连续演化的低维坐标。这使它可以作为后续 ROM 或动力学识别的状态变量，但本页暂不做外推。
:::

## 重构质量

Fig 5 使用验证段 snapshot `450`，同时展示 NekRS 参考速度模、GCN-AE 重构速度模和绝对误差。验证集全局相对 L2 误差为 `2.31e-2`；其中 `u` 分量相对误差约 `7.93e-3`，`v` 分量相对误差约 `1.01e-1`。

![GCN-AE 重构质量：参考速度模、重构速度模与绝对误差](assets/projects/cyl4/gcn-ae-reconstruction-t0450.png "同一验证快照的 NekRS 速度模、GCN-AE 重构速度模和绝对误差；图像保留真实非结构节点坐标。")

重构图说明主要剪切层和尾迹涡列可以被 8 维 latent vector 恢复。误差主要集中在圆柱近尾迹和下游涡结构相位变化区域；这比只报告一个全局误差更有解释力，也提示后续需要对 `v` 分量和近壁区域设置更细的诊断。

## 局限性

- 本页只验证 GCN-AE 降维与重构，不做 SINDy、DMD 或神经 ODE 外推。
- 当前重构诊断以速度模为主，后续应补充 `u/v` 分量误差图和局部误差统计。
- latent 维度固定为 8，还需要系统比较 latent dimension 对验证误差、相位结构和可解释性的影响。

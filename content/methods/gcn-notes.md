---
title: 图卷积网络：在非结构节点上做局部平均
type: method
subtitle: Graph Convolutional Network
category: Method
status: working
publishedAt: 2026-05-31
updatedAt: 2026-07-04
readingMinutes: 8
tags: [数值方法]
projects: [cyl4]
methods: [graph-convolutional-network, autoencoder-rom]
references: [defferrard-chebnet, kipf-gcn, bronstein-geometric-dl, brunton-ml-fluid]
referenceItems:
  - defferrard-chebnet | Convolutional Neural Networks on Graphs with Fast Localized Spectral Filtering | https://arxiv.org/abs/1606.09375
  - kipf-gcn | Semi-Supervised Classification with Graph Convolutional Networks | https://arxiv.org/abs/1609.02907
  - bronstein-geometric-dl | Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges | https://arxiv.org/abs/2104.13478
  - brunton-ml-fluid | Machine Learning for Fluid Mechanics | https://doi.org/10.1146/annurev-fluid-010719-060214
relatedProjects: [cyl4]
relatedArticles: [autoencoder-notes]
relatedMethods: [graph-convolutional-network, autoencoder-rom]
summary: 把非结构网格视作图，整理邻接矩阵、归一化图卷积、边权和全局读出的基本公式。
---

## 为什么不用普通卷积

普通卷积适合规则网格。图像上的一个像素有固定方向的邻居：左、右、上、下，卷积核可以在整张图上平移使用。非结构网格没有这种天然排列。节点的邻居数不同，边长不同，局部几何也不同。

把非结构场写成图，是一种很自然的折中。节点集合为

$$
V
=
\{1,2,\ldots,n\}.
$$

边集合为

$$
E
\subset
V\times V.
$$

图记为

$$
G=(V,E).
$$

每个节点带有特征。例如二维速度场中，节点特征可以写成

$$
\mathbf{h}_i^{(0)}
=
\begin{bmatrix}
u_i \\
v_i
\end{bmatrix}.
$$

如果还想保留坐标，可以另写

$$
\mathbf{x}_i
=
\begin{bmatrix}
x_i \\
y_i
\end{bmatrix}.
$$

图卷积的基本问题就是：如何让节点从邻居那里收集信息。

## 邻接矩阵

最简单的邻接矩阵为

$$
A_{ij}
=
\begin{cases}
1, & (i,j)\in E, \\
0, & (i,j)\notin E .
\end{cases}
$$

度矩阵为

$$
D_{ii}
=
\sum_{j=1}^{n}
A_{ij}.
$$

归一化图 Laplacian 写成

$$
L
=
I
-
D^{-1/2}
A
D^{-1/2}.
$$

这里的写法只表达结构。真正计算时，常使用带自环的邻接矩阵。

## GCN 的传播公式

加入自环：

$$
\widetilde{A}
=
A+I.
$$

对应的度矩阵为

$$
\widetilde{D}_{ii}
=
\sum_{j=1}^{n}
\widetilde{A}_{ij}.
$$

Kipf 和 Welling 的 GCN 传播公式可写成 [cite:kipf-gcn]

$$
H^{(l+1)}
=
\sigma
\left(
\widetilde{D}^{-1/2}
\widetilde{A}
\widetilde{D}^{-1/2}
H^{(l)}
W^{(l)}
\right).
$$

其中第 l 层节点特征为

$$
H^{(l)}
\in
\mathbb{R}^{n\times c_l}.
$$

权重矩阵为

$$
W^{(l)}
\in
\mathbb{R}^{c_l\times c_{l+1}}.
$$

这个公式对应一次带归一化的邻域平均，然后再做通道变换。

## 从谱图卷积到局部近似

早期图卷积常从图 Laplacian 的谱分解出发 [cite:defferrard-chebnet]。若

$$
L
=
U\Lambda U^T,
$$

则图上的谱滤波可写作

$$
g_{\theta}
*_G
\mathbf{x}
=
U
g_{\theta}(\Lambda)
U^T
\mathbf{x}.
$$

问题是直接特征分解代价很高，而且滤波器不一定局部。Chebyshev 近似和 GCN 一阶近似，本质上都是为了把这个操作变成局部、便宜、可训练的邻域传播。

## 带权边

若节点之间距离差异明显，二值邻接矩阵太粗糙。可以用距离构造边权：

$$
A_{ij}
=
\exp
\left(
-
\frac{
\left\|
\mathbf{x}_i-\mathbf{x}_j
\right\|_2^2
}{
\sigma^2
}
\right).
$$

只在有边时使用这个权重：

$$
(i,j)\in E.
$$

也可以把相对坐标作为边特征：

$$
\mathbf{e}_{ij}
=
\begin{bmatrix}
x_j-x_i \\
y_j-y_i \\
\left\|
\mathbf{x}_j-\mathbf{x}_i
\right\|_2
\end{bmatrix}.
$$

更一般的消息传递写成

$$
\mathbf{m}_{ij}^{(l)}
=
\psi^{(l)}
\left(
\mathbf{h}_i^{(l)},
\mathbf{h}_j^{(l)},
\mathbf{e}_{ij}
\right).
$$

节点更新为

$$
\mathbf{h}_i^{(l+1)}
=
\phi^{(l)}
\left(
\mathbf{h}_i^{(l)},
\sum_{j\in\mathcal{N}(i)}
\mathbf{m}_{ij}^{(l)}
\right).
$$

这种写法属于更宽的 geometric deep learning 范围 [cite:bronstein-geometric-dl]。

## 图级表示

如果目标是把一个流场快照压成低维向量，就需要把节点特征汇总成图级表示。一个简单读出是平均池化：

$$
\mathbf{z}
=
\frac{1}{n}
\sum_{i=1}^{n}
\mathbf{h}_i^{(L)}.
$$

也可以同时保留最大响应：

$$
\mathbf{z}
=
\begin{bmatrix}
\frac{1}{n}
\sum_{i=1}^{n}
\mathbf{h}_i^{(L)}
\\
\max_i
\mathbf{h}_i^{(L)}
\end{bmatrix}.
$$

这个操作常被叫作 readout。它把节点级信息变成一个全局坐标。若用于自编码器，这个坐标就是 latent vector。

## 解码时最好给坐标

如果 decoder 只拿到全局向量，它还要记住每个节点的位置。更自然的做法是让 decoder 同时看到坐标：

$$
\widehat{\mathbf{h}}_i
=
g_{\phi}
\left(
\mathbf{z},
\mathbf{x}_i
\right).
$$

二维速度重构就是

$$
\begin{bmatrix}
\widehat{u}_i \\
\widehat{v}_i
\end{bmatrix}
=
g_{\phi}
\left(
\mathbf{z},
x_i,
y_i
\right).
$$

这种写法避免把所有节点硬拼成长向量。节点顺序可以变，但坐标仍然给出物理位置。

## 物理限制

GCN 的邻域平均不等于数值离散。它一般不保证不可压约束：

$$
\nabla\cdot\mathbf{u}
=
0.
$$

也不自动保证动量守恒、边界条件或能量稳定。机器学习方法用于流体问题时，需要明确这一层限制 [cite:brunton-ml-fluid]。

在这里，GCN 更接近非结构数据编码器。它保留邻接关系，并从局部结构中提取特征；但它不是流体求解器。若用于预测或控制，还需要额外的动力学约束和物理检查。

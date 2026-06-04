---
title: 图卷积网络：非结构流场上的局部信息聚合
type: method
subtitle: Graph Convolutional Network
category: Method
status: working
publishedAt: 2026-05-31
updatedAt: 2026-05-31
readingMinutes: 5
tags: [数值方法]
projects: [cyl4]
methods: [graph-convolutional-network, autoencoder-rom]
references: [kipf-gcn]
referenceItems:
  - kipf-gcn | Semi-Supervised Classification with Graph Convolutional Networks | https://arxiv.org/abs/1609.02907
relatedProjects: [cyl4]
relatedArticles: [autoencoder-notes]
relatedMethods: [graph-convolutional-network, autoencoder-rom]
summary: 说明为什么圆柱绕流 z=2 平面使用 GCN 处理非结构节点，而不是先插值成规则图像。
---

## 为什么用图

NekRS 的 z=2 平面不是规则像素网格，而是由谱元节点和邻接关系组成的非结构图。若直接插值成图片再训练 CNN，模型看到的是后处理图像，而不是原始计算节点。GCN 的优势在于它直接使用节点特征和边连接。

## 基本传播公式

给定图邻接矩阵 $A$、单位矩阵 $I$ 和节点特征 $H^{(l)}$，常用的归一化图卷积写作 [cite:kipf-gcn]：

$$
\tilde{A}=A+I,\qquad \tilde{D}_{ii}=\sum_j\tilde{A}_{ij},
$$

$$
H^{(l+1)}=\sigma\left(\tilde{D}^{-1/2}\tilde{A}\tilde{D}^{-1/2}H^{(l)}W_l\right).
$$

这个式子可以理解为“先把邻居节点和自己合并，再用度矩阵做归一化，最后乘可学习权重并经过非线性函数”。

## 在流场中的含义

在圆柱绕流项目中，节点特征是 `u/v` 速度分量，边来自 z=2 平面的静态图结构。GCN encoder 的任务不是识别图像纹理，而是聚合局部流场信息，得到能够被 decoder 还原的全局 latent vector。

:::note 使用边界
GCN 本身不保证物理守恒。它适合作为非结构数据编码器；若要做长期预测，还需要额外的动力学模型、稳定性约束或物理一致性检查。
:::

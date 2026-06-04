---
title: Autoencoder ROM：从高维流场到可解码隐变量
type: method
subtitle: Autoencoder Reduced-Order Representation
category: Method
status: working
publishedAt: 2026-05-31
updatedAt: 2026-05-31
readingMinutes: 5
tags: [数值方法]
projects: [cyl4]
methods: [autoencoder-rom, graph-convolutional-network]
references: [autoencoder-rom]
referenceItems:
  - autoencoder-rom | Data-driven physics-constrained deep learning for reduced-order modeling of nonlinear dynamical systems | https://doi.org/10.1016/j.jcp.2019.108973
relatedProjects: [cyl4]
relatedArticles: [gcn-notes]
relatedMethods: [autoencoder-rom, graph-convolutional-network]
summary: 记录 GCN-AE 如何把非结构速度场压缩为低维 latent coordinates，并通过 decoder 回到原始节点空间。
---

## 基本结构

自编码器由 encoder 和 decoder 两部分组成。对于圆柱绕流 z=2 平面，输入是非结构节点速度场 $X(t)$ 和图结构 $G$，输出是重构速度场 $\hat{X}(t)$：

$$
z(t)=f_\theta(X(t),G),
$$

$$
\hat{X}(t)=g_\phi(z(t),p),
$$

其中 $p$ 表示节点坐标。encoder 负责压缩，decoder 负责把 latent vector 映射回原始节点空间。

## 重构损失

最基本的训练目标是让重构接近原始快照：

$$
\mathcal{L}_{rec}=\frac{1}{T}\sum_{k=1}^{T}\|\hat{X}(t_k)-X(t_k)\|_2^2.
$$

在 GCN-AE 圆柱项目中，还加入了很弱的 latent acceleration regularization：

$$
\mathcal{L}_{acc}=\frac{1}{T-2}\sum_{k=2}^{T-1}\|z_{k+1}-2z_k+z_{k-1}\|_2^2.
$$

总损失为

$$
\mathcal{L}=\mathcal{L}_{rec}+\lambda\mathcal{L}_{acc}.
$$

## 如何阅读 AE 结果

AE 的成功不能只看训练 loss。对于科研展示，更重要的是三件事：验证集重构误差、重构误差在空间中的分布、latent coordinates 是否随时间连续。圆柱项目因此同时展示原始/重构/误差图和 latent components。

:::result 页面原则
AE 在本站中只作为降维和重构证据使用。若后续要做预测，应另开项目或章节明确说明动力学模型，而不是把预测能力暗含在 AE 结果里。
:::

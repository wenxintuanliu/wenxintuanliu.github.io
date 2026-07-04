---
title: Autoencoder ROM：把流场压到非线性坐标里
type: method
subtitle: Autoencoder Reduced-Order Modeling
category: Method
status: working
publishedAt: 2026-05-31
updatedAt: 2026-07-04
readingMinutes: 9
tags: [数值方法]
projects: [cyl4]
methods: [autoencoder-rom, graph-convolutional-network]
references: [autoencoder-rom, lee-carlberg-manifold, brunton-ml-fluid, benner-mor, eivazi-ae-rom]
referenceItems:
  - autoencoder-rom | Data-driven physics-constrained deep learning for reduced-order modeling of nonlinear dynamical systems | https://doi.org/10.1016/j.jcp.2019.108973
  - lee-carlberg-manifold | Model reduction of dynamical systems on nonlinear manifolds using deep convolutional autoencoders | https://doi.org/10.1016/j.cma.2020.112991
  - brunton-ml-fluid | Machine Learning for Fluid Mechanics | https://doi.org/10.1146/annurev-fluid-010719-060214
  - benner-mor | A Survey of Projection-Based Model Reduction Methods for Parametric Dynamical Systems | https://doi.org/10.1137/130932715
  - eivazi-ae-rom | Deep Neural Networks for Nonlinear Model Order Reduction of Unsteady Flows | https://arxiv.org/abs/2007.00936
relatedProjects: [cyl4]
relatedArticles: [gcn-notes]
relatedMethods: [autoencoder-rom, graph-convolutional-network]
summary: 从线性 POD 降维讲到自编码器流形，整理重构误差、隐变量光滑性和预测边界。
---

## 先从 POD 说起

降阶模型最朴素的想法，是用少数基向量表示高维状态。设一个流场快照为

$$
\mathbf{x}
\in
\mathbb{R}^{n}.
$$

POD 型线性表示写成

$$
\mathbf{x}
\approx
\overline{\mathbf{x}}
+
\Phi \mathbf{a}.
$$

其中基矩阵为

$$
\Phi
\in
\mathbb{R}^{n\times r}.
$$

低维系数为

$$
\mathbf{a}
\in
\mathbb{R}^{r}.
$$

这种表示清楚、稳定、容易解释，也是很多投影降阶方法的基础 [cite:benner-mor]。它的限制也很直接：解需要大致落在一个线性子空间附近。对强对流、移动涡、界面输运或大变形问题，线性子空间可能需要很多模态才能追上一个简单的平移。

## 自编码器的基本写法

自编码器把线性映射换成两个非线性映射。编码器为

$$
\mathbf{z}
=
f_{\theta}(\mathbf{x}).
$$

解码器为

$$
\widehat{\mathbf{x}}
=
g_{\phi}(\mathbf{z}).
$$

隐变量维度通常远小于原始维度：

$$
\dim(\mathbf{z})
\ll
\dim(\mathbf{x}).
$$

自编码器不预先给定一组固定线性基，而是从数据中学习一个低维坐标系。Lee 和 Carlberg 把这种思想解释为在非线性流形上做模型降阶 [cite:lee-carlberg-manifold]。

解码器张成的集合可以写成

$$
\mathcal{M}_{\phi}
=
\left\{
g_{\phi}(\mathbf{z})
\;|\;
\mathbf{z}\in\mathbb{R}^{r}
\right\}.
$$

训练的目标，是让快照尽量靠近这个流形。

## 重构损失

最常见的训练损失是均方重构误差：

$$
\mathcal{L}_{\mathrm{rec}}
=
\frac{1}{N_s}
\sum_{k=1}^{N_s}
\left\|
g_{\phi}
\left(
f_{\theta}(\mathbf{x}_k)
\right)
-
\mathbf{x}_k
\right\|_2^2.
$$

如果写得短一些，就是

$$
\widehat{\mathbf{x}}_k
=
g_{\phi}
\left(
f_{\theta}(\mathbf{x}_k)
\right).
$$

$$
\mathcal{L}_{\mathrm{rec}}
=
\frac{1}{N_s}
\sum_{k=1}^{N_s}
\left\|
\widehat{\mathbf{x}}_k
-
\mathbf{x}_k
\right\|_2^2.
$$

对流体数据来说，普通欧氏范数不一定总是最合适。若节点代表的控制体积不同，或网格明显非均匀，更自然的误差应带权：

$$
\left\|
\mathbf{e}
\right\|_{M}^{2}
=
\mathbf{e}^{T} M \mathbf{e}.
$$

其中误差为

$$
\mathbf{e}
=
\widehat{\mathbf{x}}
-
\mathbf{x}.
$$

相对误差可写成

$$
\varepsilon_M
=
\frac{
\left\|
\widehat{\mathbf{x}}
-
\mathbf{x}
\right\|_{M}
}{
\left\|
\mathbf{x}
\right\|_{M}
}.
$$

仅报告训练损失是不够的。训练损失小，可能只是平均意义上小；空间误差分布能直接指出模型在哪些位置失真。

## 隐变量不应乱跳

非定常流动是连续演化的。若快照时间间隔很小，隐变量也应平滑变化。一个简单的二阶差分正则为

$$
\mathcal{L}_{\mathrm{acc}}
=
\frac{1}{N_s-2}
\sum_{k=2}^{N_s-1}
\left\|
\mathbf{z}_{k+1}
-
2\mathbf{z}_{k}
+
\mathbf{z}_{k-1}
\right\|_2^2.
$$

总损失可写成

$$
\mathcal{L}
=
\mathcal{L}_{\mathrm{rec}}
+
\lambda
\mathcal{L}_{\mathrm{acc}}.
$$

这个正则用来抑制隐变量的高频抖动。隐变量若完全没有时间结构，后续再谈动力学建模就很困难。

## 空间误差比 loss 更直观

如果状态包含二维速度分量，可以把每个节点的误差写成

$$
e_i
=
\sqrt{
\left(
\widehat{u}_i-u_i
\right)^2
+
\left(
\widehat{v}_i-v_i
\right)^2
}.
$$

分量相对误差为

$$
\varepsilon_u
=
\frac{
\left\|
\widehat{\mathbf{u}}
-
\mathbf{u}
\right\|_2
}{
\left\|
\mathbf{u}
\right\|_2
}.
$$

$$
\varepsilon_v
=
\frac{
\left\|
\widehat{\mathbf{v}}
-
\mathbf{v}
\right\|_2
}{
\left\|
\mathbf{v}
\right\|_2
}.
$$

空间误差图比单条 loss 曲线更有信息量。流体问题中，近壁区、剪切层、涡核、界面附近的误差显然比远场误差更值得在意。

## 重构不是预测

自编码器本身只学习一个往返映射：

$$
\mathbf{x}_k
\rightarrow
\mathbf{z}_k
\rightarrow
\widehat{\mathbf{x}}_k .
$$

它并没有自动学习时间推进：

$$
\mathbf{z}_k
\rightarrow
\mathbf{z}_{k+1}.
$$

如果要预测，还需要额外的低维动力学模型。离散形式可以写成

$$
\mathbf{z}_{k+1}
=
F_{\psi}
\left(
\mathbf{z}_k
\right).
$$

连续形式可以写成

$$
\frac{d\mathbf{z}}{dt}
=
\mathbf{F}_{\psi}
\left(
\mathbf{z}
\right).
$$

一些工作会把自编码器与神经网络动力学、LSTM 或 DMD 结合起来 [cite:autoencoder-rom] [cite:eivazi-ae-rom]。但在没有验证时间推进误差之前，只能说它完成了低维表示和重构，不能说它已经学会了流动演化。

## 误差检查

一个 AE-ROM 至少需要通过四个检查。

第一，训练集和验证集误差都要低，不能只记住训练快照。

第二，误差图不能集中在最关键的物理区域。

第三，隐变量轨迹要有连续性，最好能和主导流动相位对应。

第四，若声称能预测，就必须报告训练窗口外的误差。

机器学习在流体力学中的作用需要和具体任务绑定 [cite:brunton-ml-fluid]。在这里，自编码器首先是一个非线性坐标变换；只有加入并验证时间推进模型之后，才能讨论预测能力。

---
title: HODMD：用延迟坐标读出流动频率
type: method
subtitle: Higher Order Dynamic Mode Decomposition
category: Method
status: working
publishedAt: 2026-05-31
updatedAt: 2026-07-04
readingMinutes: 9
tags: [数值方法]
projects: [cylinder-hodmd]
methods: [higher-order-dmd]
references: [schmid-dmd, rowley-koopman, tu-dmd, leclainche-hodmd, kutz-dmd-book]
referenceItems:
  - schmid-dmd | Dynamic mode decomposition of numerical and experimental data | https://doi.org/10.1017/S0022112010001217
  - rowley-koopman | Spectral analysis of nonlinear flows | https://doi.org/10.1017/S0022112009992059
  - tu-dmd | On Dynamic Mode Decomposition: Theory and Applications | https://doi.org/10.3934/jcd.2014.1.391
  - leclainche-hodmd | Higher Order Dynamic Mode Decomposition | https://doi.org/10.1137/15M1054924
  - kutz-dmd-book | Dynamic Mode Decomposition: Data-Driven Modeling of Complex Systems | https://doi.org/10.1137/1.9781611974508
relatedProjects: [cylinder-hodmd]
relatedMethods: [higher-order-dmd]
summary: 由标准 DMD 写到 HODMD，记录延迟嵌入、频率识别和模态重构的基本公式。
---

## DMD 想解决什么

流场快照通常很大。一个时刻的速度、压力或涡量场可以看作一个高维向量，但我们真正关心的往往是少数频率、增长率和空间结构。DMD 的想法很直接：用相邻快照拟合一个线性推进算子，再从这个算子的特征值中读频率 [cite:schmid-dmd]。

给定快照

$$
\mathbf{x}_1,\mathbf{x}_2,\ldots,\mathbf{x}_m .
$$

构造两个矩阵

$$
X =
\left[
\mathbf{x}_1,
\mathbf{x}_2,
\ldots,
\mathbf{x}_{m-1}
\right].
$$

$$
Y =
\left[
\mathbf{x}_2,
\mathbf{x}_3,
\ldots,
\mathbf{x}_{m}
\right].
$$

DMD 假设

$$
Y \approx A X .
$$

最小二乘意义下，形式解为

$$
A = Y X^\dagger .
$$

直接构造这个矩阵通常没有必要，因为状态维度太高。实际计算时先对快照矩阵做截断奇异值分解：

$$
X \approx U_r \Sigma_r V_r^* .
$$

低维推进算子为

$$
\widetilde{A}
=
U_r^* Y V_r \Sigma_r^{-1}.
$$

若

$$
\widetilde{A} W = W \Lambda ,
$$

则 exact DMD 模态可写成

$$
\Phi
=
Y V_r \Sigma_r^{-1} W .
$$

这套写法后来被 Tu 等人系统整理，并与更一般的数据驱动算子近似联系起来 [cite:tu-dmd]。

## 特征值如何变成频率

DMD 给出的是离散时间特征值。若采样间隔为

$$
\Delta t ,
$$

则连续时间特征值为

$$
\omega_j
=
\frac{\log \lambda_j}{\Delta t}.
$$

把它拆成实部和虚部：

$$
\omega_j
=
\delta_j
+ i\,2\pi f_j .
$$

其中增长率为

$$
\delta_j = \operatorname{Re}(\omega_j),
$$

频率为

$$
f_j
=
\frac{\operatorname{Im}(\omega_j)}{2\pi}.
$$

若研究圆柱尾迹，常用 Strouhal 数写频率：

$$
St
=
\frac{f D}{U_\infty}.
$$

模态分解不能只停在一张彩色模态图上。频率、增长率和空间模态放在一起，结果才有明确的物理读法。

## 为什么要做延迟嵌入

标准 DMD 只看一步关系：

$$
\mathbf{x}_{k+1}
\approx
A\mathbf{x}_{k}.
$$

但是许多流动结构有相位记忆。一个快照本身未必足以判断下一步，因为它可能缺少速度方向、相位推进或隐藏变量信息。HODMD 的做法是把多个连续快照堆成一个延迟状态 [cite:leclainche-hodmd]。

延迟状态定义为

$$
\mathbf{q}_k
=
\begin{bmatrix}
\mathbf{x}_k \\
\mathbf{x}_{k+1} \\
\vdots \\
\mathbf{x}_{k+d-1}
\end{bmatrix}.
$$

这里的延迟阶数为

$$
d .
$$

再对这些延迟状态做 DMD。等价地，也可以把它理解成高阶递推：

$$
\mathbf{x}_{k+d}
\approx
R_1\mathbf{x}_{k}
+R_2\mathbf{x}_{k+1}
+\cdots
+R_d\mathbf{x}_{k+d-1}.
$$

这个形式比一步 DMD 更适合周期或准周期流动。多个相位同时进入回归后，主频和谐波的识别通常更稳定。

## Hankel 矩阵写法

实际计算中，延迟嵌入常写成 Hankel 型矩阵：

$$
X_d
=
\begin{bmatrix}
\mathbf{x}_1 & \mathbf{x}_2 & \cdots & \mathbf{x}_{m-d} \\
\mathbf{x}_2 & \mathbf{x}_3 & \cdots & \mathbf{x}_{m-d+1} \\
\vdots & \vdots & \ddots & \vdots \\
\mathbf{x}_d & \mathbf{x}_{d+1} & \cdots & \mathbf{x}_{m-1}
\end{bmatrix}.
$$

$$
Y_d
=
\begin{bmatrix}
\mathbf{x}_2 & \mathbf{x}_3 & \cdots & \mathbf{x}_{m-d+1} \\
\mathbf{x}_3 & \mathbf{x}_4 & \cdots & \mathbf{x}_{m-d+2} \\
\vdots & \vdots & \ddots & \vdots \\
\mathbf{x}_{d+1} & \mathbf{x}_{d+2} & \cdots & \mathbf{x}_{m}
\end{bmatrix}.
$$

随后求解

$$
Y_d \approx A_d X_d .
$$

后续代数计算和标准 DMD 相同，只是状态空间换成了延迟空间。

## 重构

得到模态后，流场可写成指数叠加：

$$
\widehat{\mathbf{x}}(t)
=
\sum_{j=1}^{r}
b_j \phi_j
\exp(\omega_j t).
$$

幅值可以由初始快照确定：

$$
\mathbf{b}
=
\Phi^\dagger \mathbf{x}_1 .
$$

也可以用整个训练窗口做最小二乘拟合。若定义 Vandermonde 矩阵

$$
V_{jk}
=
\lambda_j^{k-1},
$$

则快照矩阵近似为

$$
X
\approx
\Phi
\operatorname{diag}(\mathbf{b})
V .
$$

DMD 模态不是任意滤波结果，而是带有固定时间指数的空间结构。

## 误差比模态图更诚实

我看 HODMD 结果时，最不愿意只看模态图。模态图容易让人产生“分解成功”的错觉。更实在的量是重构误差：

$$
\varepsilon_{\mathrm{rec}}
=
\frac{
\left\|X-\widehat{X}\right\|_F
}{
\left\|X\right\|_F
}.
$$

如果有训练窗口外的快照，还应看外推误差：

$$
\varepsilon_{\mathrm{pred}}(t_k)
=
\frac{
\left\|\mathbf{x}_k-\widehat{\mathbf{x}}_k\right\|_2
}{
\left\|\mathbf{x}_k\right\|_2
}.
$$

训练窗口内误差很低，并不代表可以长期预测。对周期尾迹来说，外推首先考验频率是否准确；频率稍有偏差，相位误差就会随时间积累。

## 参数选择

HODMD 至少有三个敏感参数。

第一是延迟阶数。太小，方法接近普通 DMD；太大，可用样本列数减少，噪声也可能被放大。

第二是截断秩。秩太低会漏掉谐波；秩太高会把噪声当模态。

第三是采样间隔。最高可解析频率受 Nyquist 限制：

$$
f_{\max}
=
\frac{1}{2\Delta t}.
$$

频率分辨率受总采样窗口控制。若窗口长度为

$$
T ,
$$

则粗略有

$$
\Delta f
\sim
\frac{1}{T}.
$$

因此 HODMD 的参数需要和采样窗口一起检查。延迟阶数、截断秩和时间间隔不合适时，模态图即使好看，频率也可能没有物理意义。

## 与 Koopman 视角的关系

DMD 常被看作 Koopman 谱分析的有限维近似 [cite:rowley-koopman]。非线性系统为

$$
\mathbf{x}_{k+1}
=
F(\mathbf{x}_k).
$$

Koopman 算子作用在观测函数上：

$$
\mathcal{K} g
=
g \circ F .
$$

DMD 并不直接线性化状态方程，而是在数据选择的观测空间里近似这个线性算子。这个视角解释了为什么 DMD 可以从非线性尾迹中提取线性频率和模态，也解释了为什么观测变量、采样窗口和降维截断会影响结果 [cite:kutz-dmd-book]。

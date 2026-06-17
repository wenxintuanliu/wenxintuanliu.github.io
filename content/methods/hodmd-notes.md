---
title: HODMD：用延迟嵌入提取圆柱尾迹频率与模态
type: method
subtitle: Higher Order Dynamic Mode Decomposition
category: Method
status: working
publishedAt: 2026-05-31
updatedAt: 2026-05-31
readingMinutes: 7
tags: [数值方法]
projects: [cylinder-hodmd]
methods: [higher-order-dmd]
references: [schmid-dmd, leclainche-hodmd]
referenceItems:
  - schmid-dmd | Dynamic mode decomposition of numerical and experimental data | https://doi.org/10.1017/S0022112010001217
  - leclainche-hodmd | Higher Order Dynamic Mode Decomposition | https://doi.org/10.1137/15M1054924
relatedProjects: [cylinder-hodmd]
relatedMethods: [higher-order-dmd]
summary: 从标准 DMD 推到 Higher Order DMD，给出快照回归、延迟嵌入和连续时间重构公式。
---

## 标准 DMD 的起点

给定相邻快照矩阵

$$
X=[x_1,x_2,\ldots,x_{m-1}],\qquad Y=[x_2,x_3,\ldots,x_m],
$$

标准 DMD 拟合线性推进算子

$$
Y\approx AX,\qquad A_{\mathrm{ls}}=YX^\dagger.
$$

实际计算中通常先做截断 SVD：

$$
X\approx U_r\Sigma_rV_r^*,
$$

再在低维子空间中构造

$$
\tilde{A}=U_r^*YV_r\Sigma_r^{-1}.
$$

若 $\tilde{A}W=W\Lambda$，exact DMD 模态可以写为

$$
\Phi=YV_r\Sigma_r^{-1}W.
$$

## 从 DMD 到 HODMD

标准 DMD 假设一步关系

$$
v_{k+1}=Rv_k.
$$

Le Clainche 和 Vega 提出的 Higher Order DMD 使用更一般的高阶 Koopman 假设 [cite:leclainche-hodmd]：

$$
v_{k+d}=R_1v_k+R_2v_{k+1}+\cdots+R_dv_{k+d-1}.
$$

其中 $d$ 是 delay order。这个形式可以看成把多个时间滞后快照堆叠后再做 DMD，因此更适合周期、准周期以及空间复杂度有限但频率成分较多的系统。

## 连续时间重构

HODMD 得到的离散特征值可转换为连续时间增长率和频率：

$$
\omega_j=\frac{\log(\lambda_j)}{\Delta t}=\delta_j+i\nu_j.
$$

流场重构写作

$$
x(t)\approx\sum_{j=1}^{r}b_j\phi_j\exp(\omega_j t).
$$

这里 $\phi_j$ 是空间模态，$b_j$ 是幅值，$\delta_j$ 控制增长或衰减，$\nu_j$ 控制振荡频率。

## 在圆柱尾迹中的读法

圆柱尾迹的主导结构通常以共轭频率对出现。HODMD 项目中 d=50 的频率报告显示主频及其谐波，模态图则展示这些频率对应的空间结构。外推预测是否可信，不能只看模态是否好看，还要检查训练窗口外的相对误差。

:::note 实践提醒
HODMD 的结果会受 delay order、SVD 截断阈值、是否去均值、采样窗口长度影响。网页项目固定展示 d=50，是为了先建立一条可复现证据链，而不是声称它是唯一最优参数。
:::

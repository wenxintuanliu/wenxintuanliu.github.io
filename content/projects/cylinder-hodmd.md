---
title: 圆柱绕流的 HODMD 模态分解与外推
type: project
subtitle: Higher Order Dynamic Mode Decomposition on NekRS z=2 plane
category: Modal Decomposition
status: seedling
publishedAt: 2026-05-31
updatedAt: 2026-07-04
readingMinutes: 9
tags: [项目文章]
hero: assets/projects/cylinder-hodmd/eigenvalues_plot.png
methods: [higher-order-dmd]
projects: [cyl4]
references: [leclainche-hodmd, schmid-dmd]
referenceItems:
  - leclainche-hodmd | Higher Order Dynamic Mode Decomposition | https://doi.org/10.1137/15M1054924
  - schmid-dmd | Dynamic mode decomposition of numerical and experimental data | https://doi.org/10.1017/S0022112010001217
relatedProjects: [cyl4]
relatedArticles: [hodmd-notes]
relatedMethods: [higher-order-dmd]
dataAvailability: 图像与模态结果保存在 assets/projects/cylinder-hodmd/；HODMD 原始输出保存在 /home/chunfengfusu/NekRS_run/cyl/z2_plane_gnn/hodmd/output_z2。
summary: HODMD 使用延迟嵌入扩展 DMD，在 NekRS 圆柱绕流 z=2 平面中识别基频、谐波及可外推的周期尾迹结构。
---

## 问题

这个项目和 [圆柱绕流的 GCN-AE 降维与重构](pages/project.html?id=cyl4) 使用同一套 NekRS 圆柱绕流数据。这里不训练神经网络，而是直接处理 z=2 平面上的速度快照，检查数据里能否分离出圆柱尾迹的主导频率、空间模态，以及这些模态在训练窗口外是否仍能保持相位。

每个快照包含平面内速度分量 u 和 v，可以写成

$$
x_k=\begin{bmatrix}u_k\\v_k\end{bmatrix}\in\mathbb{R}^{2N},\qquad N=23778 .
$$

训练窗口使用第 1 到 301 个快照，对应物理时间 t=120 到 t=180；验证窗口使用第 302 到 401 个快照，对应 t=180.2 到 t=200。快照间隔为 0.2。圆柱尾迹在这个阶段已经进入周期脱落状态，适合用 DMD 类方法检查频率和相位结构。

## 方法

标准 DMD 用相邻快照近似一步线性推进。HODMD 的想法是把多帧历史放进同一个状态向量，让回归同时看到更长的时间记忆 [cite:leclainche-hodmd]。延迟嵌入后的状态可以写成

$$
\tilde{x}_k=
\begin{bmatrix}
x_k\\x_{k+1}\\\vdots\\x_{k+d-1}
\end{bmatrix},
\qquad
\tilde{x}_{k+1}\approx A\tilde{x}_k .
$$

等价地，也可以把它理解为一个高阶时间递推：

$$
x_{k+d}=R_1x_k+R_2x_{k+1}+\cdots+R_d x_{k+d-1}.
$$

我测试了 d=30、40、50、60、70 这些延迟阶数。它们给出的主导频率很接近，重构误差也在同一量级；最后采用 d=50，因为它在这组测试中误差最低，同时仍然处在训练快照数量的合理比例内。SVD 截断阈值为 1e-6，模态筛选阈值为 1e-2。

HODMD 得到的连续时间表达为

$$
x(t)\approx \sum_{m=1}^{M} a_m \phi_m
\exp\left((\delta_m+i\omega_m)t\right),
$$

其中 $\phi_m$ 是空间模态，$\omega_m$ 给出频率，$\delta_m$ 表示增长或衰减率。对圆柱尾迹来说，模态数量本身不是重点；更关键的是特征值是否贴近单位圆、频率是否成谐波关系、空间结构是否对应剪切层脱落和下游涡列传播。

## 谱结构

特征值谱中，主导模态成共轭对分布，并且靠近单位圆。训练窗口里的尾迹主要由近中性的周期振荡控制，快速衰减的瞬态结构占比很小。

![d=50 HODMD 特征值谱与单位圆](assets/projects/cylinder-hodmd/eigenvalues_plot.png "d=50 的 HODMD 谱给出近单位圆的成对共轭特征值，对应周期尾迹的主导振荡频率。")

频率报告中最清楚的三组频率为 0.1791、0.3581 和 0.5372。它们几乎构成 1:2:3 的谐波关系，分别对应圆柱尾迹的基频、二阶谐波和三阶谐波。肉眼能看到尾迹周期脱落，HODMD 则把这个周期性落到具体频率和空间模态上。

## 模态结构

基频模态给出圆柱后方最强的大尺度反对称摆动。这个结构决定了尾迹涡列交替脱落的主相位，也是重构和外推中最重要的空间骨架。

![HODMD mode 01：基频尾迹结构](assets/projects/cylinder-hodmd/mode_01_d50.png "基频模态给出圆柱后方最强的大尺度反对称尾迹结构，是后续重构和外推的主导空间成分。")

二阶谐波主要补充近尾迹剪切层和下游涡列的形状修正。它不像基频那样决定整体摆动方向，但会影响涡核附近的局部幅值和对称性。

![HODMD mode 03：二阶谐波结构](assets/projects/cylinder-hodmd/mode_03_d50.png "二阶谐波模态补充剪切层和下游涡列的高频结构，使单一基频之外的周期细节能够进入重构。")

三阶谐波集中在下游振荡区域，用来修正相位变化较快的位置。仅用一个正弦形态描述尾迹会过于粗糙；高阶谐波对恢复真实速度场仍然有贡献。

![HODMD mode 05：三阶谐波结构](assets/projects/cylinder-hodmd/mode_05_d50.png "三阶谐波模态集中在下游尾迹振荡区，用于修正高频相位和局部振幅。")

这组三个模态放在一起，可以看到一条清楚的结构关系：圆柱近尾迹剪切层脱落，基频控制大尺度交替摆动，高阶谐波补充剪切层和下游涡列的局部细节。

## 重构

训练窗口内的物理量相对均方根误差为 3.51e-3。下面选取训练窗口中的第 301 个快照作为局部检查；该快照的全局相对 L2 误差为 3.55e-3，其中 u 分量误差为 1.56e-3，v 分量误差为 1.48e-2。

![训练窗口内 HODMD 重构对照](assets/projects/cylinder-hodmd/reconstruction_t0151_src0151_d50.webp "训练窗口内的 HODMD 重构对照显示 u/v 分量和误差分布，snapshot 301 的全局相对 L2 误差为 3.55e-3。")

误差主要集中在剪切层和下游涡列相位敏感的位置。这个分布是合理的：u 分量的主流和回流结构更容易被低阶周期模态恢复，而 v 分量幅值较小、相位变化更敏感，所以相对误差更大。

## 外推

更关键的检查是训练窗口外推。外推时不重新拟合模型，只使用训练窗口识别出的模态、频率和增长率继续推进验证段。验证段整体 physical RRMSE 为 3.51e-3；第 351 个快照的全局相对 L2 误差为 3.48e-3，第 401 个快照为 3.46e-3。

![验证窗口内 HODMD 外推对照](assets/projects/cylinder-hodmd/compare_t0351_src0351_d50.webp "训练窗口外 source snapshot 351 的 HODMD 预测对照，全局相对 L2 误差为 3.48e-3。")

训练段和验证段误差几乎没有明显分离，d=50 HODMD 没有停留在训练快照拟合上，而是抓住了这个时间窗口中持续存在的周期动力学。对 Re=100 圆柱尾迹平面来说，这组结果可以作为线性模态方法的基准，再和 GCN-AE 一类非线性降维结果对照。

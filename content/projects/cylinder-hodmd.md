---
title: 圆柱绕流的 HODMD 模态分解与外推
type: project
subtitle: Higher Order Dynamic Mode Decomposition on NekRS z=2 plane
category: Modal Decomposition
status: seedling
publishedAt: 2026-05-31
updatedAt: 2026-05-31
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
dataAvailability: 网页媒体资产保存在 assets/projects/cylinder-hodmd/；HODMD 原始输出保存在 /home/chunfengfusu/NekRS_run/cyl/z2_plane_gnn/hodmd/output_z2。
summary: HODMD 使用延迟嵌入扩展 DMD，在圆柱绕流平面中识别多频振荡结构。
---

## 研究问题

圆柱尾迹包含稳定的基频和高阶谐波。标准 DMD 用相邻快照估计一步线性推进；HODMD 则把多帧历史放入延迟嵌入，用更高阶的时间信息提取 Koopman 近似模态 [cite:leclainche-hodmd]。

本项目使用 `/home/chunfengfusu/NekRS_run/cyl/z2_plane_gnn/hodmd` 中 `d=50` 的结果，回答两个问题：第一，HODMD 是否能给出清晰的尾迹频率和空间模态；第二，识别出的模态是否能在训练窗口之后稳定外推。

## 谱结构

延迟阶数为 `d=50` 时，HODMD 的高阶回归可以写成

$$
v_{k+d}=R_1v_k+R_2v_{k+1}+\cdots+R_dv_{k+d-1}.
$$

Fig 1 展示识别出的特征值与单位圆。被选中的特征值成对靠近单位圆，说明该圆柱尾迹主要由弱衰减或近中性的周期模态控制。

![d=50 HODMD 特征值谱与单位圆](assets/projects/cylinder-hodmd/eigenvalues_plot.png "d=50 的 HODMD 谱展示近单位圆的成对共轭特征值，对应周期尾迹的主导振荡频率。")

频率报告给出主导频率对 `0.1791`、`0.3581`、`0.5372`，近似对应基频、二阶谐波和三阶谐波。后续模态图不是孤立图片，而是从同一个谱分解中选出的空间证据。

## 模态结构

Fig 2 到 Fig 4 分别展示基频及高阶谐波对应的主导空间模态。基频模态控制尾迹中最强的大尺度反对称摆动；更高频模态则把下游剪切层和小尺度振荡补充进重构。

![HODMD mode 01：基频尾迹结构](assets/projects/cylinder-hodmd/mode_01_d50.png "基频模态给出圆柱后方最强的大尺度反对称尾迹结构，是后续重构和外推的主导空间成分。")

![HODMD mode 03：二阶谐波结构](assets/projects/cylinder-hodmd/mode_03_d50.png "二阶谐波模态补充剪切层和下游涡列的高频结构，使单一基频之外的周期细节能够进入重构。")

![HODMD mode 05：三阶谐波结构](assets/projects/cylinder-hodmd/mode_05_d50.png "三阶谐波模态集中在下游尾迹振荡区，用于修正高频相位和局部振幅。")

:::result 模态解释
这些模态共同描述“圆柱后方剪切层脱落 -> 下游涡列传播 -> 谐波修正细节”的结构链条。HODMD 的价值不只是压缩数据，而是把频率、增长率和空间结构放在同一个可解释框架内。
:::

## 训练窗口重构

训练窗口为 source snapshots `1:301`。报告中最终 physical RRMSE 为 `3.51e-3`；snapshot `301` 的局部全局相对 L2 误差为 `3.55e-3`，其中 `u` 分量为 `1.56e-3`，`v` 分量为 `1.48e-2`。

![训练窗口内 HODMD 重构对照](assets/projects/cylinder-hodmd/reconstruction_t0151_src0151_d50.webp "训练窗口内的 HODMD 重构对照显示 u/v 分量和误差分布，snapshot 301 的全局相对 L2 误差为 3.55e-3。")

Fig 5 说明 `d=50` 的模态集已经能恢复训练窗口内的主要速度结构。误差集中在剪切层和下游涡列相位敏感区域；这与圆柱尾迹的物理结构一致。

## 验证窗口外推

HODMD 外推使用同一组模态、增长率和频率继续推进：

$$
v(t)\approx \sum_{m=1}^{M} a_m u_m
\exp\left((\delta_m+i\omega_m)t\right).
$$

验证报告显示，source snapshot `351` 的全局相对 L2 误差为 `3.48e-3`，source snapshot `401` 的全局相对 L2 误差为 `3.46e-3`。

![验证窗口内 HODMD 外推对照](assets/projects/cylinder-hodmd/compare_t0351_src0351_d50.webp "训练窗口外 source snapshot 351 的 HODMD 预测对照，全局相对 L2 误差为 3.48e-3。")

:::result 当前结论
在这个 z=2 圆柱尾迹平面中，d=50 HODMD 不只是拟合训练窗口，也能在验证窗口维持稳定外推误差。这说明主导频率和空间模态确实捕捉了尾迹周期演化，而不是只记住了训练快照。
:::

## 仍需补充

- 系统比较不同 delay order `d` 和 SVD 截断阈值对频率、模态和验证误差的影响。
- 明确每个模态的归一化、相位约定和物理单位。
- 将二维 z=2 平面扩展到多个 spanwise plane 或三维体模态。

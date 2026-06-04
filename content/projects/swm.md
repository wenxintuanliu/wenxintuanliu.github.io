---
title: 冲击波多相混合算例
type: project
subtitle: MFC / Shock-Wave Mixer
category: Compressible Multiphase Flow
status: working
publishedAt: 2026-05-19
updatedAt: 2026-05-30
readingMinutes: 7
tags: [项目文章]
hero: assets/projects/swm/schlieren-evolution.gif
methods: [compressible-multiphase]
projects: [cyl4]
references: [mfc-code]
referenceItems:
  - mfc-code | MFC: an open-source high-order multi-component flow solver | https://github.com/MFlowCode/MFC
relatedProjects: [cyl4]
relatedArticles: [compressible-multiphase-workflow]
relatedMethods: [compressible-multiphase]
dataAvailability: 网页媒体资产保存在 assets/projects/swm/；原始 MFC 运行目录位于 /home/chunfengfusu/MFC_run/runs/swm，受本地环境限制不随站点发布。
summary: 二维 shock-wave mixer：右行冲击波穿过弱剪切层、轻气泡、重夹杂体与多处下游小尺度界面。
---

## 研究问题

强压缩波穿过密度不均匀的轻/重夹杂体时，界面变形、波系反射和混合区输运如何耦合发展？

## 图像生成

算例由 MFC 生成 HDF5/Silo 场文件。网页资产脚本读取 MPI 分块并重排为二维场；GIF 使用 [MFC 多相流工作流](pages/method.html?id=compressible-multiphase-workflow) 中的固定色标与固定画布生成，避免帧间布局跳动 [cite:mfc-code]。

![Schlieren evolution of shock-interface interaction](assets/projects/swm/schlieren-evolution.gif "固定画布 schlieren 动画展示冲击波穿过轻/重夹杂体和剪切层后的波系演化。")

![Pressure field at t = 0.625](assets/projects/swm/pressure-midrun.png "MFC pressure field, collection_25")

![Inclusion volume fraction at t = 1.25](assets/projects/swm/inclusion-volume-final.png "MFC alpha_2 field, collection_50")

![Spanwise vorticity at t = 1.25](assets/projects/swm/vorticity-final.png "MFC omega_3 field, collection_50")

:::result 当前观察
Schlieren 动画显示冲击波扫过多相界面后的反射、折射和剪切层扰动；压力场、体积分数和涡量图可以交叉定位局部压缩与夹杂体拉伸。
:::

## 仍需补充

- 混合率、能谱或界面长度等定量诊断。
- 与简化 Riemann 问题或文献算例的对照。

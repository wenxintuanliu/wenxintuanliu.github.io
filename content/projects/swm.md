---
title: 冲击波多相混合算例
type: project
subtitle: MFC / Shock-wave mixer with light and heavy inclusions
category: Compressible Multiphase Flow
status: working
publishedAt: 2026-05-19
updatedAt: 2026-07-04
readingMinutes: 8
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
dataAvailability: 图像与动画保存在 assets/projects/swm/；原始 MFC 运行目录位于 /home/chunfengfusu/MFC_run/runs/swm，包含 swm.py、pre_process.inp、simulation.inp、probe 数据和 Silo/HDF5 输出。
summary: 自写二维 MFC shock-wave mixer 算例：右行强压缩波穿过弱剪切层、波纹轻/重夹杂体和下游小气泡，记录压力、体积分数、涡量与探针响应。
---

## 问题

这个算例是我自己搭的一个二维 MFC 小工况，用来观察冲击波进入非均匀多物质区域之后会发生什么：压缩波在轻/重夹杂体界面上反射和折射，界面被压力梯度和密度梯度共同扭曲，剪切层继续卷吸并把材料界面拉长。

相比单个理想化气泡，我更想搭一个接近“混合器”的场景：左侧强驱动区产生右行冲击/压缩波，背景中叠加上下弱剪切层，流场中放置波纹重质团、波纹轻质泡、上游轻泡、下游重椭圆和两个小卫星泡。一个短算例里由此同时出现波系传播、界面变形、涡量生成和探针压力响应。

## 模型与数值设置

MFC 这里使用二维两流体可压多相模型 [cite:mfc-code]。计算域为

$$
x\in[-1.2,2.4],\qquad y\in[-0.9,0.9],
$$

网格参数为 $m=300,\ n=150$，因此

$$
\Delta x=\frac{3.6}{300}=0.012,\qquad
\Delta y=\frac{1.8}{150}=0.012.
$$

初始时间步长设为 $1.7\times10^{-4}$，并开启 CFL 自适应时间步，目标 CFL 为 0.23。实际运行中时间步会根据局部波速调整，最终从 $t=0$ 推进到 $t=1.25$，共约 2458 步。输出间隔为 $t_{\mathrm{save}}=0.025$，因此得到 collection 0 到 50 的场文件。

空间离散采用五阶 WENO，`mapped_weno` 开启，`weno_eps=10^{-12}`；时间推进使用三阶时间格式。Riemann solver 设为 2，波速估计方式为 1，平均状态方式为 2。四个边界均采用 MFC 的非反射/外推类边界设置 `-6`，用来减少有限计算域边界对内部冲击-界面相互作用的污染。

两种流体均使用 stiffened-gas 形式但 $\pi_\infty=0$。输入文件中 `fluid_pp(1)%gamma=2.5`、`fluid_pp(2)%gamma=3.125`，对应脚本里使用的 $\gamma_1=1.4$ 和 $\gamma_2=1.32$。初始背景压力为 $p_0=1$，背景密度为 $\rho_0=1$。

## 初始结构

算例由 10 个 patch 组成。第 1 个 patch 是全域背景空气；第 2 和第 3 个 patch 在上下半区加入弱反向剪切，速度量级约为 $0.1c_0$。第 4 个 patch 是左侧驱动 slab，中心位于 $x=-0.93$，压力为 $5.6p_0$，密度为 $3.25\rho_0$，速度为 $1.22c_0$，用于生成右行强压缩波。

材料夹杂体用第二相体积分数表示。主要结构包括：

- 波纹重质团：中心 $(0.10,0.20)$，半径 0.22，密度 $2.6\rho_0$；
- 波纹轻质泡：中心 $(0.55,-0.22)$，半径 0.18，密度 $0.16\rho_0$；
- 上游轻泡：中心 $(-0.26,-0.28)$，半径 0.13，密度 $0.13\rho_0$；
- 下游重椭圆：中心 $(0.96,0.18)$，半轴 0.21 和 0.11，密度 $3.4\rho_0$；
- 两个小气泡：中心 $(1.24,-0.10)$ 和 $(1.52,0.24)$，半径分别为 0.095 和 0.075。

波纹团和波纹泡使用 MFC 的 modal geometry，并叠加 Fourier 形变；所有夹杂体都做了平滑处理，避免初始体积分数界面过于尖锐。这个设置让冲击波先遇到上游轻泡，再穿过主重质团和轻质泡，随后继续撞击下游重椭圆和小气泡串。

## 输出与诊断

运行输出 `pres`、`rho`、`vel1`、`vel2`、`omega3`、`schlieren`、`alpha1/2` 和 `alpha_rho1/2`。后处理读取 MPI 分块 Silo/HDF5 输出，并用固定画布生成动画和静态图。

![Schlieren evolution of shock-interface interaction](assets/projects/swm/schlieren-evolution.gif "固定画布 schlieren 动画记录冲击波穿过轻/重夹杂体和剪切层后的波系演化。")

Schlieren 图最适合看波前、接触间断和细尺度界面。冲击波从左向右扫过后，在不同密度夹杂体周围产生反射、折射和局部聚焦；界面附近的 baroclinic torque 会持续生成涡量，使后期结构不再只是简单的波前平移。

![Pressure field at t = 0.625](assets/projects/swm/pressure-midrun.png "MFC pressure field, collection_25")

中期压力场显示强压缩波已经穿过主夹杂体区域，压力高值和低值在轻/重界面周围重新分布。这个图和 schlieren 动画互补：schlieren 强调梯度，压力图直接显示压缩区和膨胀区的位置。

![Inclusion volume fraction at t = 1.25](assets/projects/swm/inclusion-volume-final.png "MFC alpha_2 field, collection_50")

最终的第二相体积分数图记录了材料区域被冲击和剪切共同拉伸后的形态。轻泡和重质团的变形方式不同，这也是这个 mixed setup 最有意思的部分。

![Spanwise vorticity at t = 1.25](assets/projects/swm/vorticity-final.png "MFC omega_3 field, collection_50")

涡量图把剪切层卷吸和界面附近的涡量生成显示得更直接。下游夹杂体附近也出现了局部旋转结构，主波前之后的二次相互作用仍然能在涡量场里留下痕迹。

## 探针与守恒检查

算例设置了 5 个压力探针，位置分别为 $(-0.35,0)$、$(0.18,0.22)$、$(0.62,-0.22)$、$(1.05,0.18)$ 和 $(1.45,-0.08)$。压力历史按这 5 个位置从保存场文件采样，用来把波前到达顺序转成时间信号。

![Pressure histories at five probes](assets/projects/swm/probe-pressure-history.png "五个探针位置的压力历史，用于定位强压缩波和后续反射波到达时间。")

不同探针的压力峰值差异很大：上游探针较早看到驱动波，靠近下游重椭圆的探针出现更高的局部压力峰，对应夹杂体附近的波系重构。

![Inclusion-phase diagnostics](assets/projects/swm/material-diagnostics.png "第二相材料的质心迁移和守恒诊断。")

材料诊断图显示第二相质心整体向右输运，y 方向位置变化较小；质量归一化曲线保持接近 1，而体积分数占据体积下降。也就是说，材料总量基本守住了，但界面形状和占据区域已经被冲击和剪切明显改写。

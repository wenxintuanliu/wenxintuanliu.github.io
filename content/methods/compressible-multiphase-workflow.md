---
title: 可压多相流：冲击波遇到材料界面
type: method
subtitle: Compressible Multiphase Flow
category: Method
status: working
publishedAt: 2026-05-30
updatedAt: 2026-07-04
readingMinutes: 10
tags: [数值方法]
projects: [swm]
methods: [compressible-multiphase]
references: [mfc-code, mfc-paper, allaire-five-equation, kapila-model, jiang-shu-weno, shu-weno-review]
referenceItems:
  - mfc-code | MFC: an open-source high-order multi-component flow solver | https://github.com/MFlowCode/MFC
  - mfc-paper | MFC: An open-source high-order multi-component, multi-phase, and multi-scale compressible flow solver | https://arxiv.org/abs/1907.10512
  - allaire-five-equation | A five-equation model for the simulation of interfaces between compressible fluids | https://doi.org/10.1006/jcph.2002.7143
  - kapila-model | Two-phase modeling of deflagration-to-detonation transition in granular materials | https://doi.org/10.1063/1.1398042
  - jiang-shu-weno | Efficient Implementation of Weighted ENO Schemes | https://doi.org/10.1006/jcph.1996.0130
  - shu-weno-review | High Order Weighted Essentially Nonoscillatory Schemes for Convection Dominated Problems | https://doi.org/10.1137/S0036144504449956
relatedProjects: [swm]
relatedArticles: [spectral-element-notes]
relatedMethods: [compressible-multiphase]
summary: 整理弥散界面变量、五方程模型、状态方程、WENO 捕捉和 baroclinic 涡量生成。
---

## 可压多相流的麻烦

单相不可压流动里，涡量、压力和速度已经足够复杂。可压多相流还要多处理两件事：一是压力波会被材料界面反射和折射，二是界面两侧密度和声速不同，导致涡量在界面附近生成。

MFC 是为多组分、多相和强间断可压流动设计的求解器 [cite:mfc-code] [cite:mfc-paper]。这类算例不能只看一张压力图；体积分数、密度梯度、涡量和探针时序都要一起读。

## 体积分数

两相模型中，体积分数满足

$$
\alpha_1+\alpha_2=1 .
$$

每个体积分数还应满足

$$
0 \le \alpha_k \le 1 .
$$

混合密度为

$$
\rho
=
\alpha_1\rho_1
+
\alpha_2\rho_2 .
$$

第二相质量可由积分得到：

$$
m_2(t)
=
\int_{\Omega}
\alpha_2\rho_2
\,d\Omega .
$$

第二相质心为

$$
\mathbf{x}_{c,2}(t)
=
\frac{1}{m_2(t)}
\int_{\Omega}
\mathbf{x}
\alpha_2\rho_2
\,d\Omega .
$$

这两个量比单独看界面形状更定量。体积分数图给出材料位置，质量和质心给出材料整体守恒与下游输运。

## 五方程模型

弥散界面方法不显式追踪一条几何界面，而是在若干网格单元内平滑表示材料过渡。Allaire 等人的五方程模型是这一方向的重要基础 [cite:allaire-five-equation]。对共享速度和压力的两相模型，可写出下面几条方程。

相质量守恒：

$$
\frac{\partial(\alpha_k\rho_k)}{\partial t}
+
\nabla\cdot
\left(
\alpha_k\rho_k\mathbf{u}
\right)
=0 .
$$

动量守恒：

$$
\frac{\partial(\rho\mathbf{u})}{\partial t}
+
\nabla\cdot
\left(
\rho\mathbf{u}\otimes\mathbf{u}
+pI
\right)
=0 .
$$

总能量守恒：

$$
\frac{\partial E}{\partial t}
+
\nabla\cdot
\left(
(E+p)\mathbf{u}
\right)
=0 .
$$

总能量为

$$
E
=
\rho e
+
\frac{1}{2}\rho
\left\|
\mathbf{u}
\right\|_2^2 .
$$

体积分数方程常含有非守恒项。可写成

$$
\frac{\partial\alpha_2}{\partial t}
+
\mathbf{u}\cdot\nabla\alpha_2
=
K\nabla\cdot\mathbf{u}.
$$

这里的系数 K 与两相可压缩性有关。Kapila 等人的模型从机械平衡和热力学关系出发讨论了这类项 [cite:kapila-model]。

## 状态方程

常用的 stiffened-gas 状态方程为

$$
p
=
\left(\gamma_k-1\right)
\rho_k e_k
-
\gamma_k\pi_{\infty,k}.
$$

若

$$
\pi_{\infty,k}=0 ,
$$

则退化为理想气体形式：

$$
p
=
\left(\gamma_k-1\right)
\rho_k e_k .
$$

不同相可以有不同的

$$
\gamma_k .
$$

因此即使共享压力和速度，材料声学性质也不一样。冲击波遇到界面后，反射波、透射波和局部聚焦都会受这些参数影响。

## 有限体积更新

强冲击问题通常使用守恒型有限体积更新。以一维守恒律为例：

$$
\frac{\partial U}{\partial t}
+
\frac{\partial F(U)}{\partial x}
=0 .
$$

单元平均量的更新为

$$
U_i^{n+1}
=
U_i^n
-
\frac{\Delta t}{\Delta x}
\left(
\widehat{F}_{i+1/2}
-
\widehat{F}_{i-1/2}
\right).
$$

二维时，还要加上另一个方向的通量差：

$$
U_{i,j}^{n+1}
=
U_{i,j}^{n}
-
\frac{\Delta t}{\Delta x}
\left(
\widehat{F}_{i+1/2,j}
-
\widehat{F}_{i-1/2,j}
\right)
-
\frac{\Delta t}{\Delta y}
\left(
\widehat{G}_{i,j+1/2}
-
\widehat{G}_{i,j-1/2}
\right).
$$

界面通量由左右重构状态和 Riemann solver 给出。强间断问题中，通量计算直接影响冲击捕捉的稳定性。

## WENO 重构

WENO 方法的核心是：在光滑区尽量使用高阶模板，在间断附近自动降低跨间断模板的权重 [cite:jiang-shu-weno] [cite:shu-weno-review]。

界面值可抽象写成

$$
\widehat{q}_{i+1/2}
=
\sum_{r}
\omega_r
\widehat{q}_{i+1/2}^{(r)} .
$$

非线性权重为

$$
\omega_r
=
\frac{\alpha_r}{\sum_s \alpha_s}.
$$

其中

$$
\alpha_r
=
\frac{d_r}{(\epsilon+\beta_r)^p}.
$$

这里

$$
d_r
$$

是理想权重，

$$
\beta_r
$$

是光滑性指标。若某个模板跨过冲击或材料界面，光滑性指标变大，对应权重降低。

## CFL 条件

可压流动的时间步受声速限制。二维情形可粗略写成

$$
\Delta t
\le
\mathrm{CFL}
\min
\left(
\frac{\Delta x}{|u|+c},
\frac{\Delta y}{|v|+c}
\right).
$$

其中声速为

$$
c .
$$

冲击波进入不同材料后，局部声速和速度都会变化。自适应时间步由此成为稳定计算的一部分。

## Schlieren 与涡量

数值 schlieren 常根据密度梯度构造。一个常见形式为

$$
S(\mathbf{x})
=
\exp
\left(
-
\kappa
\frac{
\left\|
\nabla\rho
\right\|
-
\left\|
\nabla\rho
\right\|_{\min}
}{
\left\|
\nabla\rho
\right\|_{\max}
-
\left\|
\nabla\rho
\right\|_{\min}
}
\right).
$$

它适合看冲击、接触间断和材料界面，但不能代替压力场。压力场直接给出压缩和膨胀结构：

$$
p=p(\mathbf{x},t).
$$

二维涡量为

$$
\omega_z
=
\frac{\partial v}{\partial x}
-
\frac{\partial u}{\partial y}.
$$

可压多密度流动中，涡量方程里有 baroclinic 项：

$$
\frac{D\omega}{Dt}
=
\left(
\omega\cdot\nabla
\right)
\mathbf{u}
-
\omega
\left(
\nabla\cdot\mathbf{u}
\right)
+
\frac{
\nabla\rho
\times
\nabla p
}{
\rho^2
}
+\cdots .
$$

当密度梯度和压力梯度不平行时，

$$
\nabla\rho
\times
\nabla p
\ne
0 .
$$

这就是冲击波穿过材料界面后涡量生成的重要来源。

## 诊断量

可压多相流的图不能只追求花。Schlieren 看波前和间断，压力看压缩区，体积分数看材料，涡量看界面附近的旋转结构，探针压力看波到达时间，积分量看材料守恒和整体输运。

这些量互相对应时，才能判断冲击、界面和涡量之间的关系。只有一张动态图，即使视觉效果很好，也很难判断具体的物理过程。

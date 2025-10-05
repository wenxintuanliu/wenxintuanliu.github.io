import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
# 设置支持中文的字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用于正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用于正常显示负号

def lid_driven_cavity_basic(Re=100, nx=41, ny=41, max_iter=6900, dt=0.001, tol=1e-5):
    # 域和网格参数
    Lx, Ly = 1.0, 1.0
    dx, dy = Lx / (nx - 1), Ly / (ny - 1)

    # 初始化变量（使用交错网格）
    u = np.zeros((ny, nx))  # x方向速度 (i, j) -> (x, y)
    v = np.zeros((ny, nx))  # y方向速度
    p = np.zeros((ny, nx))  # 压力

    # 设置顶盖速度
    u[-1, :] = 1.0  # 顶盖 (y=1)

    # 时间迭代
    for n in range(max_iter):
        un = u.copy()
        vn = v.copy()

        # 1. 预测步：计算中间速度 (忽略压力项)
        u_star = un.copy()
        v_star = vn.copy()

        # 内部点计算 (u-速度)
        # Plan Step 1 & 2 & 3: Correct loop structure for u_star and fix syntax.
        for j in range(1, ny - 1): # Iterate over y
            for i in range(1, nx - 1): # Iterate over x
                # 对流项 (中心差分)
                conv_u = (un[j, i] * (un[j, i + 1] - un[j, i - 1]) / (2 * dx) +
                          vn[j, i] * (un[j + 1, i] - un[j - 1, i]) / (2 * dy)) # Added closing parenthesis

                # 扩散项 (二阶中心差分)
                diff_u = (1 / Re) * (
                        (un[j, i + 1] - 2 * un[j, i] + un[j, i - 1]) / dx ** 2 +
                        (un[j + 1, i] - 2 * un[j, i] + un[j - 1, i]) / dy ** 2
                )
                # 更新中间速度
                u_star[j, i] = un[j, i] + dt * (-conv_u + diff_u)

        # 内部点计算 (v-速度)
        # Plan Step 1 & 2 & 3: Correct loop structure for v_star and fix syntax.
        for j in range(1, ny - 1): # Iterate over y
            for i in range(1, nx - 1): # Iterate over x
                # 对流项
                conv_v = (un[j, i] * (vn[j, i + 1] - vn[j, i - 1]) / (2 * dx) +
                          vn[j, i] * (vn[j + 1, i] - vn[j - 1, i]) / (2 * dy)) # Added closing parenthesis

                # 扩散项
                diff_v = (1 / Re) * (
                        (vn[j, i + 1] - 2 * vn[j, i] + vn[j, i - 1]) / dx ** 2 +
                        (vn[j + 1, i] - 2 * vn[j, i] + vn[j - 1, i]) / dy ** 2
                )
                v_star[j, i] = vn[j, i] + dt * (-conv_v + diff_v)

        # 2. 求解压力泊松方程 (Jacobi迭代)
        # Plan Step 1: Correct indentation for pressure calculation part.
        b = np.zeros((ny, nx)) # Source term for PPE

        # 计算源项 (连续性方程残差！)
        # Plan Step 1: Correct loop structure for source term b.
        for j in range(1, ny - 1): # Iterate over y
            for i in range(1, nx - 1): # Iterate over x
                b[j, i] = (1 / dt) * (
                        (u_star[j, i + 1] - u_star[j, i - 1]) / (2 * dx) +
                        (v_star[j + 1, i] - v_star[j - 1, i]) / (2 * dy)
                )

        # 迭代求解压力
        # Plan Step 1 & 4: Correct pressure Jacobi iteration loop and apply BCs inside.
        for _ in range(100):  # 压力求解子迭代
            p_old_iter = p.copy()
            for j in range(1, ny - 1): # Iterate over y
                for i in range(1, nx - 1): # Iterate over x
                    p[j, i] = (
                            dy ** 2 * (p_old_iter[j, i + 1] + p_old_iter[j, i - 1]) +
                            dx ** 2 * (p_old_iter[j + 1, i] + p_old_iter[j - 1, i]) -
                            dx ** 2 * dy ** 2 * b[j, i]
                    ) / (2 * (dx ** 2 + dy ** 2))

            # 压力边界条件 (dp/dn=0)
            p[:, 0] = p[:, 1]    # 左边界 dp/dx = 0
            p[:, -1] = p[:, -2]  # 右边界 dp/dx = 0
            p[0, :] = p[1, :]    # 下边界 dp/dy = 0
            p[-1, :] = p[-2, :]  # 上边界 (顶盖) dp/dy = 0

        # 3. 修正步：用压力梯度更新速度
        # Plan Step 1 & 5: Correct velocity correction loop.
        for j in range(1, ny - 1): # Iterate over y
            for i in range(1, nx - 1): # Iterate over x
                u[j, i] = u_star[j, i] - dt * (p[j, i + 1] - p[j, i - 1]) / (2 * dx)
                v[j, i] = v_star[j, i] - dt * (p[j + 1, i] - p[j - 1, i]) / (2 * dy)

        # 应用速度边界条件
        # Plan Step 6: Ensure velocity BCs are applied correctly at the end of the time step.
        u[:, 0] = 0.0   # 左壁 (x=0)
        u[:, -1] = 0.0  # 右壁 (x=Lx)
        u[0, :] = 0.0   # 下壁 (y=0)
        u[-1, :] = 1.0  # 顶盖 (y=Ly) - 驱动速度

        v[:, 0] = 0.0   # 左壁
        v[:, -1] = 0.0  # 右壁
        v[0, :] = 0.0   # 下壁
        v[-1, :] = 0.0  # 顶盖 (顶盖y方向速度为0)


        # 检查收敛
        # Plan Step 7: Correct convergence check logic and break statement.
        if n % 100 == 0:
            du = np.linalg.norm(u - un) / np.linalg.norm(un + 1e-12) # Relative error
            dv = np.linalg.norm(v - vn) / np.linalg.norm(vn + 1e-12) # Relative error
            if du < tol and dv < tol:
                print(f"在迭代 {n} 步后收敛")
                break
    else: # Executed if the loop completes without a break
        print(f"达到最大迭代次数 {max_iter}，可能未收敛。du={du:.2e}, dv={dv:.2e}")


    return u, v, p


# 运行模拟
u, v, p = lid_driven_cavity_basic(Re=100, nx=41, ny=41)

# 可视化结果
plt.figure(figsize=(12, 9))
plt.subplot(221)
plt.contourf(p, cmap='viridis')
plt.title('压力场')
plt.colorbar()

plt.subplot(222)
plt.contourf(u, cmap='coolwarm')
plt.title('x方向速度')
plt.colorbar()

plt.subplot(223)
plt.contourf(v, cmap='coolwarm')
plt.title('y方向速度')
plt.colorbar()

# 流线图
x = np.linspace(0, 1, 41)
y = np.linspace(0, 1, 41)
X, Y = np.meshgrid(x, y)

plt.subplot(224)
plt.streamplot(X, Y, u, v, density=2, color='k', linewidth=1)
plt.title('流线图')
plt.xlim(0, 1)
plt.ylim(0, 1)

plt.tight_layout()
plt.savefig('cavity_flow_basic.png', dpi=600)
plt.show()
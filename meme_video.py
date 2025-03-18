import numpy as np
import matplotlib.pyplot as plt

# 定义初始参数
x0 = 1e9  # Token数量
y0 = 10    # SOL数量
n = 32     # 曲线参数
k = (x0 ** n) * y0  # 计算常数k

# 生成x轴数据（使用对数空间避免数值溢出）
x_values = np.logspace(np.log10(x0/100),  # 比当前值小两个数量级
                       np.log10(x0*100),  # 比当前值大两个数量级
                       500)  # 生成500个数据点

# 计算对应的y值
y_values = k / (x_values ** n)

# 创建画布
plt.figure(figsize=(10, 6))

# 绘制曲线（对数坐标系）
plt.plot(x_values, y_values, linewidth=2)
plt.xscale('log')
plt.yscale('log')

# 标记当前市场状态
plt.scatter(x0, y0, color='red', zorder=5, label=f'Current State (x={x0:.1e}, y={y0})')
plt.axvline(x0, color='grey', linestyle='--', alpha=0.5)
plt.axhline(y0, color='grey', linestyle='--', alpha=0.5)

# 添加标签和标题
plt.title(f'Pricing Curve: $x^{{{n}}} \cdot y = k$\n(k = {k:.2e})', fontsize=14)
plt.xlabel('Token Supply (x) - log scale', fontsize=12)
plt.ylabel('SOL Reserve (y) - log scale', fontsize=12)
plt.grid(True, which='both', linestyle='--', alpha=0.7)
plt.legend()

# 显示图表
plt.show()
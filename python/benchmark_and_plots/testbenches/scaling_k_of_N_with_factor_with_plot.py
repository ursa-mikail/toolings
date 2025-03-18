import time
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Simulate the system behavior (replace with actual logic)
def system_under_test(k, N):
    time.sleep(0.005 * (k + N) / 10)  # Simulate time scaling
    return random.random() < (k / N)  # Simulate success rate

# Run the benchmark
def benchmark(k_ratios, max_scale, steps):
    x, y, z = [], [], []
    for scale in range(1, max_scale + 1):
        for ratio in k_ratios:
            k = int(ratio * scale)  # Increase k with scale
            N = scale  # Increase N with scale
            start_time = time.time()
            system_under_test(k, N)  # Test the system
            elapsed_time = time.time() - start_time

            # Collect data points for 3D plot
            x.append(ratio)
            y.append(scale)
            z.append(elapsed_time)

            print(f"Test (k/N={ratio:.2f}, Scale={scale}x): Time={elapsed_time:.4f}s")
    return x, y, z

# Parameters
k_ratios = np.linspace(0.1, 0.9, 9)  # k/N ratios from 0.1 to 0.9
max_scale = 50  # Up to 50x scale

# Run benchmark
x, y, z = benchmark(k_ratios, max_scale, steps=50)

# 3D Plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x, y, z, c=z, cmap='viridis', marker='o')

# Labels and Title
ax.set_xlabel('k/N Ratio')
ax.set_ylabel('Mx (Scale Factor)')
ax.set_zlabel('Time Taken (s)')
ax.set_title('System Performance (k/N vs. Scale vs. Time)')

plt.show()

"""
Test (k/N=0.10, Scale=1x): Time=0.0065s
Test (k/N=0.20, Scale=1x): Time=0.0014s
Test (k/N=0.30, Scale=1x): Time=0.0039s
Test (k/N=0.40, Scale=1x): Time=0.0006s
Test (k/N=0.50, Scale=1x): Time=0.0006s
Test (k/N=0.60, Scale=1x): Time=0.0006s
Test (k/N=0.70, Scale=1x): Time=0.0006s
Test (k/N=0.80, Scale=1x): Time=0.0006s
:
Test (k/N=0.60, Scale=50x): Time=0.0406s
Test (k/N=0.70, Scale=50x): Time=0.0454s
Test (k/N=0.80, Scale=50x): Time=0.0459s
Test (k/N=0.90, Scale=50x): Time=0.0476s
"""
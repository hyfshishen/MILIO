import matplotlib.pyplot as plt
import numpy as np

# Data
ratios = [4.0, 6.0, 8.0]
throughput_1gpu = [294.00, 305.44, 310.05]
throughput_2gpu = [503.49, 531.49, 558.23]
throughput_4gpu = [839.40, 791.96, 1004.39]

plt.figure(figsize=(10, 6))

plt.plot(ratios, throughput_1gpu, marker='^', linestyle=':', linewidth=2, label='1 GPU')
plt.plot(ratios, throughput_2gpu, marker='o', linestyle='-', linewidth=2, label='2 GPUs')
plt.plot(ratios, throughput_4gpu, marker='s', linestyle='--', linewidth=2, label='4 GPUs')

plt.title('Aggregate Compression Throughput vs. Target Ratio (HACC Dataset)', fontsize=14)
plt.xlabel('Target Compression Ratio', fontsize=12)
plt.ylabel('Aggregate Throughput (GB/s)', fontsize=12)
plt.grid(True, linestyle=':', alpha=0.7)
plt.legend(fontsize=12)
plt.xticks(ratios)

# Save
plt.savefig('/u/bzhang28/.gemini/antigravity/brain/650dd055-455b-4c1a-a67b-8a05ffc7f862/performance_chart.png')
print("Chart saved.")

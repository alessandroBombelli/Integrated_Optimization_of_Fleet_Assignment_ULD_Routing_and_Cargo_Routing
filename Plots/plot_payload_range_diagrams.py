import matplotlib.pyplot as plt

plt.close("all")

# B747-400ERF
x1 = [0, 9200, 11900, 16100]  # Range values
y1 = [112,112,85,0]        # Payload values

# B747-400BCF
x2 = [0,7500,11800,14900]  # Range values
y2 = [107,107,63,0]          # Payload values

plt.figure(figsize=(8, 5))  # Set figure size

# Plot first set of points
plt.plot(x1, y1, marker='o', markersize=10, linestyle='-', label="B747-400ERF")

# Plot second set of points
plt.plot(x2, y2, marker='s', markersize=10, linestyle='--', label="B747-400BCF")

# Add text labels near the data points
for x, y in zip(x1, y1):
    plt.text(x+100, y+3, f"({x}, {y})", fontsize=10, ha="center")

for x, y in zip(x2, y2):
    plt.text(x+100, y-3, f"({x}, {y})", fontsize=10, ha="center")

# Labels and title
plt.xlabel("Range [km]")
plt.ylabel("Payload [tonnes]")

# Legend and grid
plt.legend(loc="best")
plt.grid(True)

# Save the figure
plt.savefig("payload_range_diagram.png", dpi=600, bbox_inches="tight")

# Show the plot
plt.show()

import gurobipy
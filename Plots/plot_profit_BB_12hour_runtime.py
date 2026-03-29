import matplotlib.pyplot as plt
import numpy as np
from brokenaxes import brokenaxes
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# Define colors
INFORMS_orange     = "#e88900"
INFORMS_darkorange = "#e64300"
INFORMS_dark       = "#6b0a1f"

# Define the orange palette
orange_palette = [
    (1.0, 0.85, 0.7),  # Light Peach
    (1.0, 0.7, 0.4),   # Soft Apricot
    (1.0, 0.55, 0.1),  # Golden Orange
    (0.91, 0.4, 0.1),  # Deep Orange
    (0.8, 0.3, 0.0),   # Burnt Orange
    (0.6, 0.2, 0.0)    # Dark Rust
]

plt.close("all")

# Data
instances     = [rf"$\mathbb{{H}}$50", rf"$\mathbb{{M}}$50", rf"$\mathbb{{L}}$50"]
approaches    = ["Hybrid arc-path-based", "Full arc-based"]
profit_values = np.array([[3.499, 2.921], [3.347,2.912], [3.285,2.683]])  # Profit per instance-approach
best_bounds   = np.array([[3.543,3.646], [3.375,3.482], [3.327,3.427]])  # Best bounds per instance-approach

# Plot settings
bar_width = 0.35        # Reduced bar width to create spacing
gap_between_bars = 0.1  # Small gap between bars in the same instance
group_spacing = 1.2     # Larger gap between different instances

# Compute x positions
instance_positions = np.arange(len(instances)) * (2 * bar_width + gap_between_bars + group_spacing)  # Position groups

x_positions = []
for pos in instance_positions:
    x_positions.append(pos - (bar_width / 2 + gap_between_bars / 2))
    x_positions.append(pos + (bar_width / 2 + gap_between_bars / 2))



# Flatten data for plotting
profit_flat = profit_values.flatten()
best_bounds_flat = best_bounds.flatten()



fig, ax = plt.subplots(figsize=(10, 5))

#bax = brokenaxes(ylims=((0, 0.2), (2.5, 3.8)), hspace=0.10)  # Define y-axis break

# Plot bars
ax.bar(x_positions, profit_flat, width=bar_width, color=INFORMS_orange, label="Profit")
ax.bar(x_positions, best_bounds_flat - profit_flat, width=bar_width, bottom=profit_flat, color=orange_palette[0], label="BB")

# X-ticks and labels
x_labels = [f"{inst} - {approach}" for inst in instances for approach in approaches]
ax.set_xticks(x_positions)
ax.set_xticklabels(x_labels, rotation=30, ha="right")

error = [np.round(100*(best_bounds[i][1]-profit_values[i][0])/(best_bounds[i][1]),1) for i in range(len(instances))]
# Adding arrows and annotations
for i in range(len(instances)):
    x_start = x_positions[2*i+1]
    y_start = best_bounds[i][1]
    
    x_end = x_positions[2*i+1]
    y_end = profit_values[i][0]
    
    # Draw arrow
    ax.annotate("", xy=(x_end, y_end), xytext=(x_start, y_start),
                arrowprops=dict(arrowstyle="->", color="black", lw=1.5))
    
    # Add text near the arrow
    ax.text((x_start + x_end) / 2 + 0.2, (y_start + y_end) / 2, f"{error[i]:.2f}%", 
            ha="center", va="bottom", fontsize=10, color="black")


# Labels and formatting
plt.ylim(2, max(best_bounds_flat)+0.1) 
ax.set_ylabel("Profit [M€]")
ax.legend(loc="best")
ax.grid("True")

# Save the figure
plt.savefig(os.path.join(script_dir,"comp+integrated_fullarc_12h.png"), dpi=600, bbox_inches="tight")

plt.show()




import matplotlib.pyplot as plt
import numpy as np

import awesomefigures as af

# Five luminance levels, five independently selectable hues.
grid = af.contrast_grid(
    levels=5,
    hues=[55, 20, 145, 210, 290],
    ratio=1.4,
    start_luminance=0.95,
)

# Pick any one hue from each row. Adjacent CR remains 1.4.
palette = grid.select([0, 1, 2, 3, 4])

x = np.linspace(0, 2 * np.pi, 400)
fig, ax = plt.subplots()
for k, rgba in enumerate(palette.mpl_colors(alpha=0.8, background="white")):
    ax.plot(x, np.sin(x + 0.35 * k), color=rgba, linewidth=3)

ax.set_title("Constant-contrast palette")
plt.show()

Accessibility and print safety
==============================

Scientific plots should not rely on color alone.

The Heri Matplotlib style automatically cycles distinct colors, markers,
and linestyles for successive plain line plots. Repeated scatter calls get
different group markers. Explicit choices always take precedence.
For reproducible scatter groups, use awesomefigures.scatter_scheme.

The accessibility panel has six views:

* Original color figure
* Grayscale preserving linear-sRGB luminance
* Print stress: grayscale with deliberately reduced tonal contrast and levels
* Deuteranopia
* Protanopia
* Tritanopia

The color-vision simulations use the Machado et al. (2009) matrices from
Colorspacious. They approximate, rather than guarantee, how someone with
a particular color-vision deficiency might see a figure. Print stress is
not a calibrated printer or ICC profile. This is a design diagnostic,
not proof of accessibility.

Example
-------

.. code-block:: python

   import awesomefigures as af
   import matplotlib.pyplot as plt
   import numpy as np

   af.set_style("heri", font="DejaVu Sans")
   x = np.linspace(0, 8, 150)
   fig, ax = plt.subplots()
   for i in range(4):
       ax.plot(x, np.sin(x+i*0.3)+i*0.4, label=f"Series {i+1}")
   ax.legend()
   fig.tight_layout()

   af.show_accessibility_panel(fig)
   af.save_accessibility_panel(fig, "fig_accessibility.png")

The original figure is not recolored. The preview includes legends, text,
axes, and heatmaps. For large plots, use max_width=650 to limit size.
The ncols and severity options configure layout and CVD severity.

.. code-block:: python

   image = af.simulate_figure(fig, "tritanopia")
   variants = af.figure_variants(fig, modes=("original", "grayscale"))

Grouped scatter plots
---------------------

For categories, vary color and marker by group, not by observation.

.. code-block:: python

   schemes = af.scatter_scheme(
       [55, 20, 145, 210, 290], ratio=1.2, start_luminance=0.72
   )
   for (xs, ys), style in zip(groups, schemes):
       ax.scatter(xs, ys, **style)

Notebook plots
--------------

The Sphinx notebook cookbook puts a six-view panel immediately after each
figure. Use tools/setup_and_run.ps1 to regenerate and save the panels.

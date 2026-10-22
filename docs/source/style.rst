Styles
======

``awesomefigures`` includes three style states: ``heri`` (publication
colours, fonts, and redundant line identifiers), ``elegante`` (those
publication defaults plus rigorously aligned endpoint ticks and inset
markers), and Matplotlib ``default``. Use ``available_styles()`` to
inspect the installed presets.

Heri
----

The default ``heri`` style uses print-aware categorical colors: the
first few plotted series are assigned widely separated luminances, as
well as different markers and dash patterns. Earlier publication figures
can be reproduced using ``palette="legacy"``, which retains the original
WTI categorical colors.

.. raw:: html

   <div class="cc-style-summary">
     <div><strong>Background</strong>white + light gray grid</div>
     <div><strong>Typography</strong>compact 8--9 pt paper scale</div>
     <div><strong>Lines</strong>1.6 pt, top/right spines hidden</div>
     <div><strong>Export</strong>600 dpi hybrid PDF defaults</div>
   </div>

.. plot::
   :include-source:

   import numpy as np
   import matplotlib.pyplot as plt
   import awesomefigures as af

   af.set_style("heri", font="DejaVu Sans")

   x = np.linspace(0, 9, 260)
   fig, ax = plt.subplots(figsize=(8.0, 4.1))

   for i in range(4):
       ax.plot(
           x,
           np.sin(x * 0.72 + i * 0.55) + i * 0.34,
           label=f"Series {i + 1}",
       )

   ax.set(
       title="Heri publication style",
       xlabel="Time",
       ylabel="Response",
   )
   ax.legend(ncol=2)
   fig.tight_layout()

Use it with:

.. code-block:: python

   af.set_style("heri", font="Arial")

Choose another font without changing the rest of the style:

.. code-block:: python

   af.set_style("heri", font="Helvetica")
   af.set_style("heri", font="STIX")
   af.set_style("heri", font="DejaVu Sans")
   af.set_style("heri", font="utopia")

The default categorical cycle is the print-safe variant. The original
colors remain in ``af.HERI_PALETTE`` and can be activated with:

.. code-block:: python

   af.set_style("heri", palette="legacy")

The continuous heatmap colormap is ``af.HERI_CMAP``.

Select published palettes without changing their original colours
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``heri`` and ``elegante`` also support built-in palettes as colour
cycles. For example:

.. code-block:: python

   af.set_style("elegante", palette="okabe-ito",
                font="DejaVu Sans", use_tex=False)
   af.set_style("heri", palette="tol-bright",
                font="DejaVu Sans", use_tex=False)

See the visual :doc:`named_palettes` catalogue. Sequential palettes
such as ``cividis`` are not used as categorical cycles; obtain their
native Matplotlib map with ``af.named_colormap("cividis")``.

Elegante — balanced ticks and inset markers
---------------------------------------------

The ``elegante`` preset improves a specific editorial detail: the left
and right spines coincide with the **first and last x-axis ticks**, while
the bottom and top limits coincide with the **first and last y-axis ticks**.
Tick spacing is chosen from readable decimal families, rather than using
an arbitrary padded interval. Every division is uniformly spaced, and
the step size is selected jointly with the axis boundaries.

It also separates **curves** from **visible markers**: spline/line data
remain unchanged and can touch the axes, but circles, squares, triangles
and other Line2D markers inside the plot have room around them.
A marker that would overlap a spine is suppressed *only visually*;
no interpolation knot is deleted. Dense lines use up to nine spaced
markers by default, keeping their original continuous curve.

.. plot::
   :include-source:

   import numpy as np
   import matplotlib.pyplot as plt
   import awesomefigures as af

   af.set_style("elegante", font="DejaVu Sans", use_tex=False, rasterize=False)
   x = np.linspace(0, 100, 501)
   fig, ax = plt.subplots(figsize=(8, 3.7))

   ax.plot(x, .86*np.sin(2*np.pi*x/100) + .2,
           label="A", marker="o", markersize=6)
   ax.plot(x, .60*np.cos(2*np.pi*x/100) - .25,
           label="B", marker="s", markersize=6)
   ax.set(xlabel="Time", ylabel="Response", title="Elegant endpoint alignment")
   ax.legend()
   fig.canvas.draw()

Observe that ``x = 0`` and ``x = 100`` are both labelled ticks and
lie on the vertical boundaries. When a curve is defined at an endpoint,
the stroke reaches the boundary, but its marker is not clipped. The
library does **not** extrapolate a spline whose data stop short of the
chosen nice view limits.

How the tick algorithm works
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For observed extrema ``a`` and ``b``, let ``h = m*10**k`` be a
candidate step, with ``m`` chosen from ``(1, 2, 2.5, 5, 10)``.
Each candidate produces tick-aligned limits

.. math::

   L = h\left\lfloor\frac{a}{h}\right\rfloor,\quad
   U = h\left\lceil\frac{b}{h}\right\rceil,\quad
   t_j=L+jh.

The selected candidate trades off relative unused axis space against the
difference between its tick count and a requested target. The endpoint
condition is exact up to floating-point precision:

.. math::

   x_{\min}=t_0,\qquad x_{\max}=t_{N-1}.

The same reasoning applies independently to ``y``.

**Configure** the result after plotting, before rendering:

.. code-block:: python

   af.set_style("elegante", font="Arial", use_tex=False)
   fig, ax = plt.subplots()
   ax.plot(x, y, marker="^")

   af.apply_elegant_axes(
       ax,
       target_xticks=6,
       target_yticks=5,
       marker_inset_pt=4.0,
       marker_count=9,
       force_zero=False,
       padding=0.0,
   )
   fig.savefig("elegant.pdf")

``apply_elegant_axes()`` can also be called with the ``heri`` or
Matplotlib default style. It returns the same Axes for chaining. Under
``elegante``, the calculation also runs automatically when the figure
is drawn, displayed, or saved. Use ``nice_tick_bounds(a,b,target_ticks=6)``
for tick generation without creating a plot.

.. code-block:: python

   low, high, ticks = af.nice_tick_bounds(7, 94, target_ticks=6)
   # 0.0, 100.0, array([0., 20., 40., 60., 80., 100.])

**Limits and reproducibility:** user-set ``set_xlim()`` and
``set_ylim()`` are respected. The alignment helper intentionally skips
logarithmic, date, categorical, shared, inverted, and non-Cartesian axes;
no misleading linear tick arithmetic is applied. Manually specified
marker intervals based on point indices are preserved except near the
frame. Floating-point/arc-length ``markevery`` patterns keep Matplotlib
behaviour unchanged. Scatter observations are never deleted; scatter-only
figures receive a small outward extension to protect boundary symbols.

This finishing pass controls geometry, not data smoothing. It does not
create spline samples, infer the scientific domain, or change interpolation
knots. Its PDF/PGF geometry remains vectorial.

Default
-------

``default`` restores Matplotlib rcParams and disables the automatic dense
rasterization switch installed by the Heri preset.

.. plot::
   :include-source:

   import numpy as np
   import matplotlib.pyplot as plt
   import awesomefigures as af

   af.set_style("default")

   x = np.linspace(0, 9, 260)
   fig, ax = plt.subplots(figsize=(8.0, 4.1))

   for i in range(4):
       ax.plot(
           x,
           np.sin(x * 0.72 + i * 0.55) + i * 0.34,
           label=f"Series {i + 1}",
       )

   ax.set(
       title="Matplotlib default",
       xlabel="Time",
       ylabel="Response",
   )
   ax.legend(ncol=2)
   fig.tight_layout()

Restore it with:

.. code-block:: python

   af.set_style("default")

Heri with a custom palette
--------------------------

The plotting style does not force you to use the built-in Heri categorical
colors. Generate a palette and pass its colors to the artists.

.. plot::
   :include-source:

   import numpy as np
   import matplotlib.pyplot as plt
   import awesomefigures as af

   af.set_style("heri", font="DejaVu Sans")

   colors = af.color_palette(
       hues=[55, 20, 145, 210, 290],
       ratio=1.20,
       start_luminance=0.72,
   )

   x = np.linspace(0, 8, 250)
   fig, ax = plt.subplots(figsize=(8.0, 4.1))

   for i, color in enumerate(colors):
       ax.plot(
           x,
           np.cos(0.72 * x + i * 0.45) + 0.28 * i,
           color=color,
           label=f"Series {i + 1}",
       )

   ax.set(
       title="Heri layout + generated contrast palette",
       xlabel="x",
       ylabel="Value",
   )
   ax.legend(ncol=3)
   fig.tight_layout()

Publication details
-------------------

Hybrid PDF rasterization
~~~~~~~~~~~~~~~~~~~~~~~~

With ``rasterize=True``, common dense artists such as scatter, hexbin,
``imshow``, ``pcolormesh``, filled contours and 3D surfaces are rasterized.
Ordinary plot lines, error bars, axes, text, ticks and legends stay vector.

.. code-block:: python

   af.set_style("heri", font="Arial", rasterize=True)
   af.save_figure(fig, "result.pdf", dpi=600)

Panel labels
~~~~~~~~~~~~

.. code-block:: python

   af.panel_label(ax, "A")

Temporary styling
~~~~~~~~~~~~~~~~~

.. code-block:: python

   with af.style_context("heri", font="Arial"):
       fig, ax = plt.subplots()
       ax.plot(x, y)

The previous Matplotlib state is restored after the block.

See :doc:`customization` for hue order, additional colors, markers,
linestyles, alpha and export options.

Built-in scientific palettes
============================

Choose familiar published colour schemes without copying HEX codes. These
presets are installed with ``awesomefigures`` and available to all plotting
helpers, publication styles and the interactive Palette & Plot Studio.

There are **two different contracts**:

* **Named reference palettes** retain their original sRGB coordinates.
  Selecting ``"okabe-ito"`` never silently remaps its colours to a new
  luminance ladder; its adjacent WCAG contrast ratios are *measured*, not
  imposed.
* **Generated contrast palettes** use :doc:`palettes` and solve for OKLCH
  hue, chroma and a prescribed WCAG relative-luminance ladder. These are
  new palettes and should not be attributed to the original named scheme.

Neither approach certifies that every pair will be distinguishable for every
viewer. Use distinct marker shapes and line styles, and inspect :doc:`accessibility`
as well as real printouts.

Categorical palettes — for independent groups
----------------------------------------------

These are exact historical HEX specifications; their source links are listed
below. The first four are widely used as colour-vision-aware starting points.
The other three are established general-purpose qualitative sets, **not**
automatically universal colour-blind guarantees.

.. plot::

   import matplotlib.pyplot as plt
   import awesomefigures as af

   names = af.available_named_palettes("categorical")
   fig, axes = plt.subplots(len(names), 1, figsize=(9.6, 7.3))
   for ax, name in zip(axes, names):
       colours = af.named_palette(name, as_hex=True)
       for k, code in enumerate(colours):
           ax.barh(0, 1, left=k, height=.8, color=code, edgecolor="white",
                   linewidth=.8)
           ax.text(k+.5, -.65, code, ha="center", va="top", fontsize=7,
                   rotation=0, family="monospace")
       ax.set_xlim(0, len(colours))
       ax.set_ylim(-.95, .62)
       ax.text(0, .53, name + "  (" + str(len(colours)) + ")",
               fontsize=10, weight="bold", va="bottom")
       ax.axis("off")
   fig.subplots_adjust(hspace=.36)

Access the precise colours immediately:

.. code-block:: python

   import awesomefigures as af

   af.available_named_palettes("categorical")
   af.named_palette("okabe-ito", as_hex=True)
   af.color_palette("tol-bright", n=4)
   af.plot_scheme("tol-high-contrast")
   af.scatter_scheme("brewer-set2", n=5)

Use the schemes with the publication styles:

.. code-block:: python

   import matplotlib.pyplot as plt
   import awesomefigures as af

   af.set_style("elegante", palette="okabe-ito",
                font="DejaVu Sans", use_tex=False)
   fig, ax = plt.subplots()
   for values in series:
       ax.plot(x, values)
   fig.savefig("figure.pdf")

For more than the available categorical colours, the library raises an
error instead of repeating colours invisibly. Define additional encodings,
split a crowded plot into panels, or construct a new contrast palette.

Sequential and diverging — for ordered values
----------------------------------------------

Continuous maps are supplied directly by Matplotlib. A continuous map should
normally be passed to ``imshow``, ``pcolormesh``, ``contourf`` or a
scalar colour mapping, **not** cycled across nominal category labels.

.. plot::

   import numpy as np
   import matplotlib.pyplot as plt
   import awesomefigures as af

   names = [*af.available_named_palettes("sequential"),
            *af.available_named_palettes("diverging")]
   fig, axes = plt.subplots(len(names), 1, figsize=(8.8, 4.8))
   ramp = np.linspace(0, 1, 384)[None, :]
   for ax, name in zip(axes, names):
       ax.imshow(ramp, cmap=af.named_colormap(name), aspect="auto",
                 interpolation="nearest", extent=[0, 1, 0, 1])
       ax.set_ylabel(name, rotation=0, ha="right", va="center", fontsize=10)
       ax.set_yticks([])
       ax.set_xticks([0, .5, 1])
       ax.tick_params(axis="x", labelsize=8, length=2)
   fig.subplots_adjust(left=.18, right=.96, top=.97, bottom=.12, hspace=.65)

Example:

.. code-block:: python

   image = ax.imshow(values, cmap=af.named_colormap("cividis"))
   fig.colorbar(image, ax=ax)

   # If a finite list of sequential colours is needed:
   sampled = af.named_palette("viridis", n=7, as_hex=True)

Continuous palettes in this catalogue: ``viridis``, ``cividis``,
``plasma``, ``magma``, ``inferno`` and diverging ``rdbu``
(Matplotlib's canonical ``RdBu``).

Metadata and transparency
-------------------------

.. code-block:: python

   p = af.get_named_palette("okabe-ito")
   print(p.kind, p.source, p.colors)
   print(af.available_named_palettes())

   # The original palette is never replaced by adjusted HEX values.
   original_hex = af.named_palette("okabe-ito", as_hex=True)
   translucent = af.named_palette(
       "okabe-ito", alpha=0.65, background="#FFFFFF",
       preserve_apparent=True
   )

Only the plotted RGBA source values may be compensated for transparency.
When exact apparent-colour recovery is not physically possible, compensation
is approximate, and overlapping transparent marks change appearance.
``as_hex=True`` always returns the opaque reference colours.

``contrast_palette("okabe-ito")`` deliberately raises: a WCAG-constructed
palette and a historically specified palette must not be silently conflated.
To design new hues with guaranteed adjacent *opaque* luminance ratios, supply
hue angles to ``af.contrast_palette([...], ratio=...)``.

Attribution and source references
---------------------------------

* Masataka Okabe and Kei Ito,
  `Color Universal Design <https://jfly.uni-koeln.de/color/>`_.
* Paul Tol, `Colour schemes and templates
  <https://sronpersonalpages.nl/~pault/>`_; specifically Bright,
  High-contrast and Muted qualitative schemes.
* Tableau, `How we designed the new color palettes in Tableau 10
  <https://www.tableau.com/blog/colors-upgrade-tableau-10-56782>`_.
* Cynthia Brewer / ColorBrewer, `ColorBrewer 2
  <https://colorbrewer2.org/>`_: Set2, Dark2 and RdBu.
* Matplotlib, `Choosing Colormaps in Matplotlib
  <https://matplotlib.org/stable/users/explain/colors/colormaps.html>`_:
  viridis, cividis, plasma, magma and inferno.

The colour numbers are shared for reproducible attribution; this project
does not claim authorship of any source palette. Original HEX order is
preserved where documented, and the map itself is Matplotlib-owned for
continuous schemes.

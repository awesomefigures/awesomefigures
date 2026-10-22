Alpha and apparent color
========================

Why alpha changes the color
---------------------------

When an sRGB foreground S is drawn over a background B at opacity alpha, the
displayed color is

.. math::

   D=\alpha S+(1-\alpha)B.

Using the original opaque RGB value as S therefore changes the visible color
unless alpha equals one.

Direct composition
------------------

.. code-block:: python

   import awesomefigures as af

   displayed = af.composite(
       foreground="#0083F9",
       background="white",
       alpha=0.70,
   )

Compensating the source color
-----------------------------

If the desired displayed target is T, the analytical inverse is

.. math::

   S=\frac{T-(1-\alpha)B}{\alpha}.

Use compensate_alpha:

.. code-block:: python

   result = af.compensate_alpha(
       "#0083F9",
       alpha=0.70,
       background="white",
   )

The returned AlphaCompensation object contains:

.. code-block:: python

   result.target_rgb
   result.source_rgb
   result.displayed_rgb
   result.background_rgb
   result.alpha
   result.feasible
   result.strategy

   result.target_hex
   result.source_hex
   result.displayed_hex
   result.max_channel_error
   result.delta_e_ok

Exact and inexact recovery
--------------------------

If the analytical source lies inside the sRGB cube, feasible is True and the
target can be reproduced exactly.

If the source would lie outside the sRGB cube, exact recovery is impossible at
that alpha/background combination. Two strategies are available.

Perceptual strategy
~~~~~~~~~~~~~~~~~~~

This is the default.

.. code-block:: python

   result = af.compensate_alpha(
       target="#0083F9",
       alpha=0.55,
       background="white",
       strategy="perceptual",
   )

The library searches the sRGB cube for a source whose displayed result minimizes
Euclidean OKLab distance to the target.

Clip strategy
~~~~~~~~~~~~~

.. code-block:: python

   result = af.compensate_alpha(
       target="#0083F9",
       alpha=0.55,
       background="white",
       strategy="clip",
   )

This clips the analytical source channel by channel. It is faster and useful as
a baseline, but is not generally perceptually optimal.

Minimum exact alpha
-------------------

Use minimum_alpha to find the smallest opacity for which exact recovery is
possible on a known background:

.. code-block:: python

   alpha_min = af.minimum_alpha(
       "#0083F9",
       background="white",
   )

For a complete Palette:

.. code-block:: python

   alpha_min = palette.minimum_alpha(background="white")

Rendering an entire palette
---------------------------

.. code-block:: python

   rendered = palette.render(
       alpha=0.75,
       background="white",
       preserve_apparent=True,
       alpha_strategy="perceptual",
   )

Matplotlib-ready RGBA tuples are available directly:

.. code-block:: python

   colors = palette.mpl_colors(
       alpha=0.75,
       background="white",
       preserve_apparent=True,
   )

Or through the high-level constructor:

.. code-block:: python

   colors = af.color_palette(
       hues=[55, 20, 145, 210, 290],
       ratio=1.4,
       alpha=0.75,
       background="white",
       preserve_apparent=True,
       alpha_strategy="perceptual",
   )

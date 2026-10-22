Color spaces
============

awesomefigures uses several color representations because no single space is
best for every operation.

sRGB
----

Hex colors and Matplotlib colors are interpreted as encoded sRGB. Examples:

.. code-block:: python

   af.to_rgb("#0083F9")
   af.to_rgb("tab:blue")
   af.to_hex([0.0, 0.5, 1.0])

sRGB channels are not linear in emitted light. WCAG relative luminance therefore
first decodes sRGB through its transfer function.

Linear sRGB
-----------

The low-level helpers are available from awesomefigures.color_spaces:

.. code-block:: python

   from awesomefigures.color_spaces import srgb_to_linear, linear_to_srgb

   linear = srgb_to_linear("#0083F9")
   encoded = linear_to_srgb(linear)

WCAG relative luminance
-----------------------

After sRGB decoding, relative luminance is

.. math::

   Y = 0.2126R_{lin}+0.7152G_{lin}+0.0722B_{lin}.

Use:

.. code-block:: python

   y = af.relative_luminance("#0083F9")

The constant-contrast ladder is defined in this Y coordinate, not in OKLCH
lightness.

WCAG contrast ratio
-------------------

For two colors with relative luminances Y1 and Y2,

.. math::

   CR = \frac{\max(Y_1,Y_2)+0.05}
              {\min(Y_1,Y_2)+0.05}.

Use either colors:

.. code-block:: python

   af.contrast_ratio("#FFFFFF", "#000000")

or already-computed luminances:

.. code-block:: python

   af.luminance_contrast(0.8, 0.4)

OKLCH
-----

The palette generator uses hue and chroma in OKLCH because they provide a more
useful perceptual control surface than raw RGB.

Conceptually a requested color is described by

.. math::

   (L, C, h),

where h is the user-selected hue angle and C is the requested chroma. The
library numerically solves L so that the resulting sRGB color reaches the
desired WCAG relative luminance Y.

The important distinction is:

.. math::

   L_{OKLCH} \neq Y_{WCAG}.

Equal steps in OKLCH lightness do not guarantee equal WCAG contrast ratios.
This library therefore controls the contrast ladder in Y and uses OKLCH for hue
and chroma.

sRGB gamut
----------

Some combinations of luminance, hue, and chroma cannot be represented in sRGB.
The library reduces chroma until the color fits the gamut.

Inspect this with a ColorCell:

.. code-block:: python

   cell = af.color_for_luminance(0.7, hue=55, chroma=0.20)

   print(cell.requested_chroma)
   print(cell.actual_chroma)

For custom algorithms:

.. code-block:: python

   from awesomefigures.color_spaces import (
       in_srgb_gamut,
       oklch_to_linear_srgb,
   )

OKLab and perceptual error
--------------------------

OKLab is used for perceptual error diagnostics and for gamut-limited alpha
compensation.

.. code-block:: python

   lab = af.srgb_to_oklab("#0083F9")
   error = af.delta_e_ok("#0083F9", "#007FEA")

delta_e_ok is Euclidean distance in OKLab. It is useful as a compact perceptual
objective, but it should not be interpreted as a universal visibility threshold.

"""Small plotting-related utility functions.

Almost all of this code is shamelessly copied verbatim from the excellent
`seaborn <https://github.com/mwaskom/seaborn>`_ plotting package.
"""
from __future__ import division
import colorsys
from itertools import cycle
import husl
import numpy as np
import matplotlib as mpl
import matplotlib.colors as mplcol
import matplotlib.pyplot as plt
from pkg_resources import resource_filename


def init_style():
    """Initialises the ssimpl plotutils plotting style."""

    # Reset the plotting parameters to internal defaults
    plt.rcdefaults()

    # Load the ssimpl params
    fname = resource_filename(__name__, 'matplotlibrc_ssimpl')
    plt.rcParams.update(mpl.rc_params_from_file(fname, fail_on_error=True))


def color_palette(name=None, n_colors=6, desat=None):
    """Return matplotlib color codes for a given palette.

    Availible seaborn palette names:
        deep, muted, bright, pastel, dark, colorblind

    Other options:
        hls, husl, any matplotlib palette

    *Params*:
        name: None, string, or list-ish
            name of palette or None to return current color list. if
            list-ish (i.e. arrays work too), input colors are used but
            possibly desaturated
        n_colors : int
            number of colors in the palette
        desat : float
            desaturation factor for each color

    *Returns*:
        palette : list of colors
            color palette
    """

    seaborn_palettes = dict(
        deep=["#4C72B0", "#55A868", "#C44E52",
              "#8172B2", "#CCB974", "#64B5CD"],
        muted=["#4878CF", "#6ACC65", "#D65F5F",
               "#B47CC7", "#C4AD66", "#77BEDB"],
        pastel=["#92C6FF", "#97F0AA", "#FF9F9A",
                "#D0BBFF", "#FFFEA3", "#B0E0E6"],
        bright=["#003FFF", "#03ED3A", "#E8000B",
                "#8A2BE2", "#FFC400", "#00D7FF"],
        dark=["#001C7F", "#017517", "#8C0900",
              "#7600A1", "#B8860B", "#006374"],
        colorblind=["#0072B2", "#009E73", "#D55E00",
                    "#CC79A7", "#F0E442", "#56B4E9"],
    )

    if name is None:
        palette = mpl.rcParams["axes.color_cycle"]
    elif hasattr(name, "__iter__"):
        palette = name
    elif name == "hls":
        palette = hls_palette(n_colors)
    elif name == "husl":
        palette = husl_palette(n_colors)
    elif name in seaborn_palettes:
        palette = seaborn_palettes[name]
    elif name in dir(mpl.cm):
        palette = mpl_palette(name, n_colors)
    else:
        raise ValueError("%s is not a valid palette name" % name)

    if desat is not None:
        palette = [desaturate(c, desat) for c in palette]

    # Always return as many colors as we asked for
    pal_cycle = cycle(palette)
    palette = [pal_cycle.next() for _ in range(n_colors)]

    # Always return in r, g, b tuple format
    palette = map(mpl.colors.colorConverter.to_rgb, palette)

    return palette


def hls_palette(n_colors=6, h=.01, l=.6, s=.65):
    """Get a set of evenly spaced colors in HLS hue space.

    h, l, and s should be between 0 and 1

    *Parameters*:
        n_colors : int
            number of colors in the palette
        h : float
            first hue
        l : float
            lightness
        s : float
            saturation

    *Returns*:
        palette : list of tuples
            color palette
    """

    hues = np.linspace(0, 1, n_colors + 1)[:-1]
    hues += h
    hues %= 1
    hues -= hues.astype(int)
    palette = [colorsys.hls_to_rgb(h_i, l, s) for h_i in hues]
    return palette


def husl_palette(n_colors=6, h=.01, s=.9, l=.65):
    """Get a set of evenly spaced colors in HUSL hue space.

    h, s, and l should be between 0 and 1

    *Parameters*:
        n_colors : int
            number of colors in the palette
        h : float
            first hue
        s : float
            saturation
        l : float
            lightness

    *Returns*:
        palette : list of tuples
            color palette
    """

    hues = np.linspace(0, 1, n_colors + 1)[:-1]
    hues += h
    hues %= 1
    hues *= 359
    s *= 99
    l *= 99
    palette = [husl.husl_to_rgb(h_i, s, l) for h_i in hues]
    return palette


def mpl_palette(name, n_colors=6):
    """Return discrete colors from a matplotlib palette.

    Note that this handles the qualitative colorbrewer palettes
    properly, although if you ask for more colors than a particular
    qualitative palette can provide you will fewer than you are
    expecting.

    *Parameters*:
        name : string
            name of the palette
        n_colors : int
            number of colors in the palette

    *Returns*:
        palette : list of tuples
            palette colors in r, g, b format
    """

    brewer_qual_pals = {"Accent": 8, "Dark2": 8, "Paired": 12,
                        "Pastel1": 9, "Pastel2": 8,
                        "Set1": 9, "Set2": 8, "Set3": 12}

    cmap = getattr(mpl.cm, name)
    if name in brewer_qual_pals:
        bins = np.linspace(0, 1, brewer_qual_pals[name])[:n_colors]
    else:
        bins = np.linspace(0, 1, n_colors + 2)[1:-1]
    palette = map(tuple, cmap(bins)[:, :3])

    return palette


def dark_palette(color, n_colors=6, reverse=False, as_cmap=False):
    """Make a palette that blends from a deep gray to `color`.

    *Parameters*:
        color : matplotlib color
            hex, rgb-tuple, or html color name
        n_colors : int, optional
            number of colors in the palette
        reverse : bool, optional
            if True, reverse the direction of the blend
        as_cmap : bool, optional
            if True, return as a matplotlib colormap instead of list

    *Returns*:
        palette : list or colormap
    """

    gray = "#222222"
    colors = [color, gray] if reverse else [gray, color]
    return blend_palette(colors, n_colors, as_cmap)


def blend_palette(colors, n_colors=6, as_cmap=False):
    """Make a palette that blends between a list of colors.

    *Parameters*:
        colors : sequence of matplotlib colors
            hex, rgb-tuple, or html color name
        n_colors : int, optional
            number of colors in the palette
        as_cmap : bool, optional
            if True, return as a matplotlib colormap instead of list

    *Returns*:
        palette : list or colormap
    """

    name = "-".join(map(str, colors))
    pal = mpl.colors.LinearSegmentedColormap.from_list(name, colors)
    if not as_cmap:
        pal = pal(np.linspace(0, 1, n_colors))
    return pal


def desaturate(color, prop):
    """Decrease the saturation channel of a color by some percent.

    *Parameters*:
        color : matplotlib color
            hex, rgb-tuple, or html color name
        prop : float
            saturation channel of color will be multiplied by this value

    *Returns*:
        new_color : rgb tuple
            desaturated color code in RGB tuple representation
    """

    # Check inputs
    if not 0 <= prop <= 1:
        raise ValueError("prop must be between 0 and 1")

    # Get rgb tuple rep
    rgb = mplcol.colorConverter.to_rgb(color)

    # Convert to hls
    h, l, s = colorsys.rgb_to_hls(*rgb)

    # Desaturate the saturation channel
    s *= prop

    # Convert back to rgb
    new_color = colorsys.hls_to_rgb(h, l, s)

    return new_color


def saturate(color):
    """Return a fully saturated color with the same hue.

    *Parameters*:
        color :  matplotlib color
            hex, rgb-tuple, or html color name

    *Returns*:
        new_color : rgb tuple
            saturated color code in RGB tuple representation
    """

    return set_hls_values(color, s=1)


def set_hls_values(color, h=None, l=None, s=None):
    """Independently manipulate the h, l, or s channels of a color.

    *Parameters*:
        color : matplotlib color
            hex, rgb-tuple, or html color name
        h, l, s : floats between 0 and 1, or None
            new values for each channel in hls space

    *Returns*:
        new_color : rgb tuple
            new color code in RGB tuple representation
    """

    # Get rgb tuple representation
    rgb = mplcol.colorConverter.to_rgb(color)
    vals = list(colorsys.rgb_to_hls(*rgb))
    for i, val in enumerate([h, l, s]):
        if val is not None:
            vals[i] = val

    rgb = colorsys.hls_to_rgb(*vals)
    return rgb


def axlabel(xlabel, ylabel, **kwargs):
    """Grab current axis and label it."""
    ax = plt.gca()
    ax.set_xlabel(xlabel, **kwargs)
    ax.set_ylabel(ylabel, **kwargs)


def despine(fig=None, ax=None, top=True, right=True,
            left=False, bottom=False):
    """Remove the top and right spines from plot(s).

    fig : matplotlib figure
        figure to despine all axes of, default uses current figure
    ax : matplotlib axes
        specific axes object to despine
    top, right, left, bottom : boolean
        if True, remove that spine

    """
    if fig is None and ax is None:
        axes = plt.gcf().axes
    elif fig is not None:
        axes = fig.axes
    elif ax is not None:
        axes = [ax]

    for ax_i in axes:
        for side in ["top", "right", "left", "bottom"]:
            ax_i.spines[side].set_visible(not locals()[side])

#!/usr/bin/env python3
"""Reproduce the paper's visual-comparison figure (Fig. 15): a reconstructed
CESM CLDHGH (z=0 slice) shown for the original and for cuZFP / MILIO-o at two
compression ratios, using the magma colormap with a zoom inset per panel.

Inputs (raw float32, shape H x W = 1800 x 3600, row-major), in DATA_DIR:
  CLDHGH_1_1800_3600.dat   original
  cuzfp_cr8.dat            cuZFP  reconstruction, CR ~ 8
  milio_cr8.dat            MILIO-o reconstruction, CR ~ 8
  cuzfp_cr16.dat           cuZFP  reconstruction, CR ~ 16
  milio_cr16.dat           MILIO-o reconstruction, CR ~ 16

Output: benchmark_charts/chart_visual_comparison.pdf
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, ConnectionPatch

# ---------------------------------------------------------------- configuration
H, W = 1800, 3600
DATA_DIR = os.environ.get("FIG15_DATA", ".")
OUT = os.environ.get("FIG15_OUT", "benchmark_charts/chart_visual_comparison.pdf")

# Zoom region on the full field (row0:row1, col0:col1). Chosen to sit over a
# structured cloud area so the quality difference is visible when magnified.
ZR0, ZR1, ZC0, ZC1 = 250, 520, 520, 950

# Panels: (label, dat file, method text, CR text). CR is measured at run time and
# passed via env (see FIG15_CR_* below) so the labels track the actual run.
PANELS = [
    ("a", "CLDHGH_1_1800_3600.dat", "Original", None),
    ("b", "cuzfp_cr8.dat",  "cuZFP",   os.environ.get("FIG15_CR_CUZFP8",  "8.00")),
    ("c", "milio_cr8.dat",  "MILIO-o", os.environ.get("FIG15_CR_MILIO8",  "8.03")),
    ("d", "cuzfp_cr16.dat", "cuZFP",   os.environ.get("FIG15_CR_CUZFP16", "16.0")),
    ("e", "milio_cr16.dat", "MILIO-o", os.environ.get("FIG15_CR_MILIO16", "15.99")),
]

plt.rcParams["font.family"] = "serif"


# ------------------------------------------------------------------ SSIM / PSNR
def _gaussian(sigma=1.5, radius=5):
    x = np.arange(-radius, radius + 1)
    g = np.exp(-(x ** 2) / (2.0 * sigma ** 2))
    return g / g.sum()


def _blur(img, g):
    """Separable Gaussian blur with reflect padding (float64)."""
    r = len(g) // 2
    p = np.pad(img, ((0, 0), (r, r)), mode="reflect")
    o1 = np.zeros_like(img, dtype=np.float64)
    for k, gk in enumerate(g):
        o1 += gk * p[:, k:k + img.shape[1]]
    p2 = np.pad(o1, ((r, r), (0, 0)), mode="reflect")
    o2 = np.zeros_like(img, dtype=np.float64)
    for k, gk in enumerate(g):
        o2 += gk * p2[k:k + img.shape[0], :]
    return o2


def ssim(a, b, L):
    """Standard Wang et al. SSIM (11-tap Gaussian, sigma 1.5, K1/K2 default)."""
    a = a.astype(np.float64)
    b = b.astype(np.float64)
    g = _gaussian(1.5, 5)
    C1 = (0.01 * L) ** 2
    C2 = (0.03 * L) ** 2
    mu_a, mu_b = _blur(a, g), _blur(b, g)
    mu_a2, mu_b2, mu_ab = mu_a * mu_a, mu_b * mu_b, mu_a * mu_b
    sa = _blur(a * a, g) - mu_a2
    sb = _blur(b * b, g) - mu_b2
    sab = _blur(a * b, g) - mu_ab
    smap = ((2 * mu_ab + C1) * (2 * sab + C2)) / \
           ((mu_a2 + mu_b2 + C1) * (sa + sb + C2))
    return float(smap.mean())


def psnr(a, b, L):
    mse = float(np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2))
    if mse == 0:
        return float("inf")
    return 20.0 * np.log10(L) - 10.0 * np.log10(mse)


# ------------------------------------------------------------------------- load
def load(name):
    return np.fromfile(os.path.join(DATA_DIR, name), dtype=np.float32).reshape(H, W)


def main():
    os.makedirs("benchmark_charts", exist_ok=True)
    orig = load(PANELS[0][1])
    vmin, vmax = float(orig.min()), float(orig.max())
    L = vmax - vmin

    fig, axes = plt.subplots(1, 5, figsize=(23, 5.2))

    for ax, (lab, fname, method, cr) in zip(axes, PANELS):
        img = orig if lab == "a" else load(fname)
        ax.imshow(img, cmap="magma", vmin=vmin, vmax=vmax,
                  origin="upper", aspect="auto", interpolation="nearest")
        ax.set_xticks([])
        ax.set_yticks([])

        # --- zoom inset in the top-right corner ---
        axins = ax.inset_axes([0.60, 0.60, 0.40, 0.40])
        axins.imshow(img, cmap="magma", vmin=vmin, vmax=vmax,
                     origin="upper", aspect="auto", interpolation="nearest")
        axins.set_xlim(ZC0, ZC1)
        axins.set_ylim(ZR1, ZR0)   # inverted y for origin='upper'
        axins.set_xticks([])
        axins.set_yticks([])
        for s in axins.spines.values():
            s.set_edgecolor("white")
            s.set_linewidth(1.5)

        # dashed source box on the main image
        rect = Rectangle((ZC0, ZR0), ZC1 - ZC0, ZR1 - ZR0, fill=False,
                         edgecolor="white", linewidth=1.3, linestyle=(0, (4, 3)))
        ax.add_patch(rect)
        # two connectors: box right corners -> inset left corners (a clean funnel)
        for (bx, by), (ix, iy) in [((ZC1, ZR0), (0, 1)), ((ZC1, ZR1), (0, 0))]:
            cp = ConnectionPatch(xyA=(bx, by), coordsA=ax.transData,
                                 xyB=(ix, iy), coordsB=axins.transAxes,
                                 color="white", linewidth=1.0)
            cp.set_zorder(5)
            ax.add_patch(cp)

        # --- caption ---
        if lab == "a":
            cap = "(a) Original (CESM\nCLDHGH, $z$=0 slice)"
        else:
            p = psnr(orig, img, L)
            s = ssim(orig, img, L)
            cap = (f"({lab}) {method}\n(CR={cr},\n"
                   f"PSNR={p:.2f} dB,\nSSIM={s:.3f})")
        ax.set_xlabel(cap, fontsize=15, labelpad=8)

    fig.subplots_adjust(left=0.005, right=0.995, top=0.99, bottom=0.02, wspace=0.03)
    fig.savefig(OUT, dpi=200, bbox_inches="tight")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

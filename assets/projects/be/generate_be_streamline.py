#!/usr/bin/env python3
"""Generate styled mean-flow previews for the 444 cube-array case."""

from __future__ import annotations

import argparse
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pymech.neksuite as nek
from matplotlib.colors import ListedColormap


PLOT_A_FIELDS = "/home/chunfengfusu/nekRS-26.0/nekRS_stats/nekRS_44stats_be0/plot_a_fields"
DEFAULT_A01 = "/home/chunfengfusu/nekRS-26.0/nekRS_stats/nekRS_44stats_be0/pstat_case/a01be.nek5000"
DEFAULT_OUT_Z = "/home/chunfengfusu/web/research-showcase/assets/projects/be/mean_streamline_z0p5_be0.png"
DEFAULT_OUT_Y = "/home/chunfengfusu/web/research-showcase/assets/projects/be/mean_streamline_y2p0_be0.png"

if PLOT_A_FIELDS not in sys.path:
    sys.path.append(PLOT_A_FIELDS)

from core.interpolation import (  # noqa: E402
    NekHighPrecisionInterpolator,
    collect_component,
    domain_bounds_from_nek_data,
    resolve_nek_field_path,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a01", default=DEFAULT_A01, help="Path to a01 .nek5000 header or field file")
    parser.add_argument("--out", default=DEFAULT_OUT_Z, help="Output PNG path for the z-plane")
    parser.add_argument("--out-y", default=DEFAULT_OUT_Y, help="Output PNG path for the y-plane")
    parser.add_argument("--z", type=float, default=0.5, help="Horizontal slice height")
    parser.add_argument("--y", type=float, default=2.0, help="Vertical slice y location")
    parser.add_argument("--resolution", type=int, default=260, help="Number of x/y samples")
    parser.add_argument("--tol-newton", type=float, default=5e-13, help="pySEMTools point-location tolerance")
    return parser.parse_args()


def interpolate_plane(path: str, axis: str, value: float, resolution: int, tol_newton: float) -> dict[str, np.ndarray]:
    field = nek.readnek(resolve_nek_field_path(path))
    x_min, x_max, y_min, y_max, z_min, z_max = domain_bounds_from_nek_data(field)
    axis = axis.lower().strip()

    if axis == "z":
        a = np.linspace(x_min, x_max, int(resolution))
        b = np.linspace(y_min, y_max, int(resolution))
        ag, bg = np.meshgrid(a, b)
        xg = ag
        yg = bg
        coord = float(np.clip(value, z_min, z_max))
        zg = np.full_like(xg, coord)
        component_a = "u"
        component_b = "v"
        xlabel = "x"
        ylabel = "y"
    elif axis == "y":
        a = np.linspace(x_min, x_max, int(resolution))
        b = np.linspace(z_min, z_max, int(resolution))
        ag, bg = np.meshgrid(a, b)
        xg = ag
        yg = np.full_like(xg, float(np.clip(value, y_min, y_max)))
        zg = bg
        coord = float(yg[0, 0])
        component_a = "u"
        component_b = "w"
        xlabel = "x"
        ylabel = "z"
    else:
        raise ValueError("axis must be 'z' or 'y'")

    interpolator = NekHighPrecisionInterpolator(field, tol_newton=tol_newton)
    cache = interpolator.locate_points(xg.ravel(), yg.ravel(), zg.ravel())

    u = interpolator.eval_scalar_field(collect_component(field, "vel", 0), cache).reshape(xg.shape)
    v = interpolator.eval_scalar_field(collect_component(field, "vel", 1), cache).reshape(xg.shape)
    w = interpolator.eval_scalar_field(collect_component(field, "vel", 2), cache).reshape(xg.shape)
    mask = (cache.rcode <= 1).reshape(xg.shape)

    return {
        "a": a,
        "b": b,
        "u": u,
        "v": v,
        "w": w,
        "mask": mask,
        "axis": axis,
        "coord": np.array(coord),
        "component_a": component_a,
        "component_b": component_b,
        "xlabel": xlabel,
        "ylabel": ylabel,
    }


def plot_plane(fields: dict[str, np.ndarray], out_path: str) -> None:
    a = fields["a"]
    b = fields["b"]
    va = fields[str(fields["component_a"])]
    vb = fields[str(fields["component_b"])]
    mask = fields["mask"].astype(bool)
    axis = str(fields["axis"])
    coord = float(fields["coord"])
    xlabel = str(fields["xlabel"])
    ylabel = str(fields["ylabel"])

    speed = np.sqrt(va * va + vb * vb)
    speed = np.where(mask, speed, np.nan)
    a_stream = np.ma.array(np.where(mask, va, np.nan), mask=~mask | ~np.isfinite(va))
    b_stream = np.ma.array(np.where(mask, vb, np.nan), mask=~mask | ~np.isfinite(vb))

    vmax = np.nanpercentile(speed, 99.5)
    if not np.isfinite(vmax) or vmax <= 0:
        vmax = 1.0
    speed_plot = np.where(np.isfinite(speed), np.minimum(speed, vmax), np.nan)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with plt.rc_context(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "STIXGeneral", "DejaVu Serif"],
            "mathtext.fontset": "stix",
            "axes.linewidth": 1.2,
            "xtick.direction": "in",
            "ytick.direction": "in",
        }
    ):
        fig, ax = plt.subplots(figsize=(7.4, 6.8), dpi=170)
        levels = np.linspace(0.0, vmax, 80)
        contour = ax.contourf(a, b, np.ma.masked_invalid(speed_plot), levels=levels, cmap="turbo", extend="neither")

        ax.streamplot(
            a,
            b,
            a_stream,
            b_stream,
            density=2.15,
            color=(0.02, 0.02, 0.02, 0.86),
            linewidth=0.62,
            arrowsize=0.88,
            minlength=0.08,
            maxlength=4.0,
            integration_direction="both",
            zorder=6,
        )

        solid_overlay = np.where(mask, np.nan, 1.0)
        ax.pcolormesh(
            a,
            b,
            solid_overlay,
            shading="auto",
            cmap=ListedColormap([(0.52, 0.52, 0.52, 0.92)]),
            edgecolors="none",
            zorder=8,
        )

        ax.set_xlim(0.0, 4.0)
        ax.set_ylim(0.0, 4.0)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel(rf"${xlabel}/H$", fontsize=18)
        ax.set_ylabel(rf"${ylabel}/H$", fontsize=18)
        ax.set_title(rf"Mean in-plane velocity at ${axis}/H={coord:.1f}$", fontsize=18, pad=8)
        ax.set_xticks(np.arange(0, 4.1, 1.0))
        ax.set_yticks(np.arange(0, 4.1, 1.0))
        ax.tick_params(labelsize=14, width=1.0, length=5)

        cbar = fig.colorbar(contour, ax=ax, pad=0.025, fraction=0.046)
        comp_a = str(fields["component_a"])
        comp_b = str(fields["component_b"])
        cbar.set_ticks(np.linspace(0.0, vmax, 7))
        cbar.set_label(rf"$\sqrt{{\langle {comp_a}\rangle^2+\langle {comp_b}\rangle^2}}$", fontsize=15)
        cbar.ax.tick_params(labelsize=12)

        fig.tight_layout(pad=0.3)
        fig.savefig(out_path, dpi=320, bbox_inches="tight")
        plt.close(fig)


def main() -> None:
    args = parse_args()
    fields = interpolate_plane(args.a01, "z", args.z, args.resolution, args.tol_newton)
    plot_plane(fields, args.out)
    print(f"wrote {args.out}")

    fields_y = interpolate_plane(args.a01, "y", args.y, args.resolution, args.tol_newton)
    plot_plane(fields_y, args.out_y)
    print(f"wrote {args.out_y}")


if __name__ == "__main__":
    main()

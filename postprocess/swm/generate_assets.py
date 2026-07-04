#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import h5py
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from PIL import Image


RUN_DIR = Path("/home/chunfengfusu/MFC_run/runs/swm")
SILO_DIR = RUN_DIR / "silo_hdf5"
OUT_DIR = Path("/home/chunfengfusu/web/research-showcase/assets/projects/swm")
PROJECT_ASSET_PREFIX = "assets/projects/swm"

DOMAIN = (-1.2, 2.4, -0.9, 0.9)
SAVE_DT = 0.025
RANKS = 4

VAR_DATASETS = {
    "alpha_rho2": "#000004",
    "alpha2": "#000013",
    "omega3": "#000014",
    "pres": "#000011",
    "rho": "#000005",
    "schlieren": "#000015",
    "vel1": "#000008",
    "vel2": "#000009",
}

ALPHA_CMAP = LinearSegmentedColormap.from_list(
    "swm_alpha",
    ["#f8fafc", "#dbeafe", "#60a5fa", "#1d4ed8", "#172554"],
)
SCHLIEREN_CMAP = LinearSegmentedColormap.from_list(
    "swm_schlieren",
    ["#f8fafc", "#d9f99d", "#5eead4", "#0f766e", "#062a2a"],
)

FIELD_STYLE = {
    "schlieren": {
        "title": "numerical schlieren",
        "cmap": SCHLIEREN_CMAP,
        "label": "schlieren",
        "robust": (1.0, 99.75),
    },
    "pres": {
        "title": "pressure",
        "cmap": "viridis",
        "label": "p",
        "robust": (1, 99.4),
        "contour_alpha": True,
    },
    "alpha2": {
        "title": "inclusion volume fraction",
        "cmap": ALPHA_CMAP,
        "label": r"$\alpha_2$",
        "vmin": 0,
        "vmax": 1,
        "xlim": (0.80, 2.30),
        "ylim": (-0.55, 0.62),
    },
    "omega3": {
        "title": "spanwise vorticity",
        "cmap": "RdBu_r",
        "label": r"$\omega_3$",
        "robust": (1, 99.2),
        "symmetric": True,
        "contour_alpha": True,
        "xlim": (0.78, 2.40),
        "ylim": (-0.68, 0.78),
    },
}

PLOT_RC = {
    "font.family": "DejaVu Sans",
    "axes.titlesize": 11.5,
    "axes.labelsize": 10.5,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 8.5,
    "figure.titlesize": 13,
}


def read_blocks(step: int, variable: str):
    dataset = VAR_DATASETS[variable]
    blocks = []
    for rank in range(RANKS):
        path = SILO_DIR / f"p{rank}" / f"{step}.silo"
        with h5py.File(path, "r") as handle:
            x = handle[".silo/#000001"][:]
            y = handle[".silo/#000002"][:]
            raw = handle[f".silo/{dataset}"][:]
            values = raw.ravel(order="C").reshape((len(y) - 1, len(x) - 1))
        blocks.append((x, y, values))
    return blocks


def field_limits(blocks, variable: str) -> tuple[float, float]:
    style = FIELD_STYLE[variable]
    all_values = np.concatenate([block[2].ravel() for block in blocks])
    if "vmin" in style:
        return float(style["vmin"]), float(style["vmax"])
    if style.get("symmetric"):
        limit = float(np.nanpercentile(np.abs(all_values), style["robust"][1]))
        return -limit, limit
    lo, hi = np.nanpercentile(all_values, style["robust"])
    return float(lo), float(hi)


def draw_alpha_contours(ax, step: int, *, color: str, linewidth: float, alpha: float) -> None:
    for x, y, values in read_blocks(step, "alpha2"):
        if np.nanmin(values) > 0.5 or np.nanmax(values) < 0.5:
            continue
        xc = 0.5 * (x[:-1] + x[1:])
        yc = 0.5 * (y[:-1] + y[1:])
        ax.contour(xc, yc, values, levels=[0.5], colors=color, linewidths=linewidth, alpha=alpha)


def style_field_axes(ax, style: dict) -> None:
    xmin, xmax = style.get("xlim", DOMAIN[:2])
    ymin, ymax = style.get("ylim", DOMAIN[2:])
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x / L")
    ax.set_ylabel("y / L")
    ax.xaxis.set_major_locator(mticker.MultipleLocator(0.6))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.3))
    ax.tick_params(length=3.5, width=0.8)
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)


def plot_field(step: int, variable: str, filename: str) -> Path:
    style = FIELD_STYLE[variable]
    blocks = read_blocks(step, variable)
    vmin, vmax = field_limits(blocks, variable)

    if "xlim" in style:
        fig = plt.figure(figsize=(7.7, 5.25), dpi=180)
        ax = fig.add_axes([0.105, 0.145, 0.685, 0.745])
        cax = fig.add_axes([0.845, 0.245, 0.035, 0.540])
    else:
        fig = plt.figure(figsize=(11.6, 5.35), dpi=180)
        ax = fig.add_axes([0.070, 0.140, 0.805, 0.745])
        cax = fig.add_axes([0.900, 0.205, 0.020, 0.615])

    mesh = None
    for x, y, values in blocks:
        mesh = ax.pcolormesh(
            x,
            y,
            np.clip(values, vmin, vmax),
            shading="auto",
            cmap=style["cmap"],
            vmin=vmin,
            vmax=vmax,
            rasterized=True,
        )

    if style.get("contour_alpha"):
        contour_color = "white" if variable == "omega3" else "#111827"
        draw_alpha_contours(ax, step, color=contour_color, linewidth=0.75, alpha=0.72)

    style_field_axes(ax, style)
    ax.set_title(f"{style['title']} at t = {step * SAVE_DT:.3f}", loc="left", fontweight="bold")

    colorbar = fig.colorbar(mesh, cax=cax)
    colorbar.set_label(style["label"])
    colorbar.outline.set_linewidth(0.6)
    colorbar.ax.tick_params(length=3, width=0.7)

    output = OUT_DIR / filename
    fig.savefig(output, facecolor="white", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    return output


def make_schlieren_gif() -> tuple[Path, list[str]]:
    frame_steps = list(range(8, 51, 4))
    all_values = np.concatenate(
        [block[2].ravel() for step in frame_steps for block in read_blocks(step, "schlieren")]
    )
    vmin, vmax = np.nanpercentile(all_values, FIELD_STYLE["schlieren"]["robust"])
    frame_paths = [
        plot_gif_frame(step, "schlieren", f"schlieren-frame-{step:05d}.png", float(vmin), float(vmax))
        for step in frame_steps
    ]

    adaptive = Image.Palette.ADAPTIVE if hasattr(Image, "Palette") else Image.ADAPTIVE
    frames = [Image.open(path).convert("P", palette=adaptive) for path in frame_paths]
    output = OUT_DIR / "schlieren-evolution.gif"
    frames[0].save(output, save_all=True, append_images=frames[1:], duration=170, loop=0, optimize=False)
    for frame in frames:
        frame.close()
    return output, [path.name for path in frame_paths]


def plot_gif_frame(step: int, variable: str, filename: str, vmin: float, vmax: float) -> Path:
    style = FIELD_STYLE[variable]
    fig = plt.figure(figsize=(12, 6), dpi=130)
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    for x, y, values in read_blocks(step, variable):
        ax.pcolormesh(
            x,
            y,
            np.clip(values, vmin, vmax),
            shading="auto",
            cmap=style["cmap"],
            vmin=vmin,
            vmax=vmax,
            rasterized=True,
        )
    xmin, xmax, ymin, ymax = DOMAIN
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    ax.text(
        0.025,
        0.935,
        f"t = {step * SAVE_DT:.3f}",
        transform=ax.transAxes,
        color="#111827",
        fontsize=13,
        ha="left",
        va="top",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.72, "pad": 3.5},
    )

    output = OUT_DIR / filename
    fig.savefig(output, dpi=130, facecolor="white", pad_inches=0)
    plt.close(fig)
    return output


def read_probe(path: Path) -> np.ndarray:
    data = np.loadtxt(path)
    return data[np.isfinite(data).all(axis=1)]


def block_centers(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return 0.5 * (x[:-1] + x[1:]), 0.5 * (y[:-1] + y[1:])


def sample_field(step: int, variable: str, px: float, py: float) -> float:
    fallback = None
    fallback_dist = np.inf
    for x, y, values in read_blocks(step, variable):
        if x[0] <= px <= x[-1] and y[0] <= py <= y[-1]:
            xc, yc = block_centers(x, y)
            ix = int(np.argmin(np.abs(xc - px)))
            iy = int(np.argmin(np.abs(yc - py)))
            return float(values[iy, ix])
        xc, yc = block_centers(x, y)
        cx = float(np.clip(px, xc.min(), xc.max()))
        cy = float(np.clip(py, yc.min(), yc.max()))
        dist = (cx - px) ** 2 + (cy - py) ** 2
        if dist < fallback_dist:
            ix = int(np.argmin(np.abs(xc - cx)))
            iy = int(np.argmin(np.abs(yc - cy)))
            fallback = float(values[iy, ix])
            fallback_dist = dist
    if fallback is None:
        raise RuntimeError(f"Could not sample {variable} at ({px}, {py})")
    return fallback


def plot_probe_history(filename: str) -> Path:
    colors = ["#2563eb", "#f97316", "#16a34a", "#dc2626", "#7c3aed"]
    labels = ["Probe 1", "Probe 2", "Probe 3", "Probe 4", "Probe 5"]
    probes = [(-0.35, 0.00), (0.18, 0.22), (0.62, -0.22), (1.05, 0.18), (1.45, -0.08)]
    steps = np.arange(0, 51)
    times = steps * SAVE_DT

    fig, axes = plt.subplots(5, 1, figsize=(10.6, 7.8), dpi=180, sharex=True)
    for i, ax in enumerate(axes, start=1):
        px, py = probes[i - 1]
        pressure = np.array([sample_field(int(step), "pres", px, py) for step in steps])
        ax.plot(times, pressure, color=colors[i - 1], linewidth=1.7, marker="o", markersize=2.4)
        ax.text(
            0.012,
            0.82,
            labels[i - 1],
            transform=ax.transAxes,
            ha="left",
            va="top",
            color=colors[i - 1],
            fontsize=10.5,
            fontweight="bold",
        )
        ax.grid(True, color="#dbe5f0", linewidth=0.7, alpha=0.80)
        ax.set_xlim(0, 1.25)
        ymax = max(1.2, float(np.nanmax(pressure)) * 1.08)
        ymin = max(0.0, float(np.nanmin(pressure)) * 0.88)
        ax.set_ylim(ymin, ymax)
        ax.yaxis.set_major_locator(mticker.MaxNLocator(3))
        ax.tick_params(length=3, width=0.75)
        for spine in ax.spines.values():
            spine.set_linewidth(0.75)

    axes[0].set_title("Pressure histories at five probes", loc="left", fontweight="bold")
    axes[2].set_ylabel("pressure")
    axes[-1].set_xlabel("non-dimensional time")
    fig.subplots_adjust(left=0.080, right=0.985, top=0.940, bottom=0.085, hspace=0.13)

    output = OUT_DIR / filename
    fig.savefig(output, facecolor="white", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    return output


def material_moments(step: int) -> tuple[float, float, float, float]:
    mass = 0.0
    area = 0.0
    mx = 0.0
    my = 0.0
    alpha_blocks = read_blocks(step, "alpha2")
    arho_blocks = read_blocks(step, "alpha_rho2")
    for (x, y, alpha), (_, _, arho) in zip(alpha_blocks, arho_blocks):
        xc, yc = block_centers(x, y)
        dx = np.diff(x)
        dy = np.diff(y)
        cell_area = dy[:, None] * dx[None, :]
        alpha_pos = np.clip(alpha, 0.0, 1.0)
        arho_pos = np.clip(arho, 0.0, None)
        local_area = alpha_pos * cell_area
        local_mass = arho_pos * cell_area
        xx, yy = np.meshgrid(xc, yc)
        area += float(np.sum(local_area))
        mass += float(np.sum(local_mass))
        mx += float(np.sum(xx * local_mass))
        my += float(np.sum(yy * local_mass))
    if mass <= 0:
        return np.nan, np.nan, mass, area
    return mx / mass, my / mass, mass, area


def plot_material_diagnostics(filename: str) -> Path:
    steps = np.arange(0, 51)
    t = steps * SAVE_DT
    moments = np.array([material_moments(int(step)) for step in steps])
    xloc = moments[:, 0]
    yloc = moments[:, 1]
    mass = moments[:, 2]
    area = moments[:, 3]
    mass_norm = mass / mass[0]
    area_norm = area / area[0]

    fig, (ax_pos, ax_norm) = plt.subplots(1, 2, figsize=(11.6, 4.4), dpi=180)

    ax_pos.plot(t, xloc, color="#0f766e", linewidth=2.2, label="x center")
    ax_pos.plot(t, yloc, color="#eab308", linewidth=2.0, label="y center")
    ax_pos.set_title("Inclusion-phase center of mass", loc="left", fontweight="bold")
    ax_pos.set_xlabel("non-dimensional time")
    ax_pos.set_ylabel("location / L")
    ax_pos.set_xlim(0, 1.25)
    ax_pos.grid(True, color="#dbe5f0", linewidth=0.75, alpha=0.85)
    ax_pos.legend(frameon=False, loc="upper left")

    ax_norm.plot(t, mass_norm, color="#0f766e", linewidth=2.2, label="mass / initial")
    ax_norm.plot(t, area_norm, color="#2563eb", linewidth=2.0, label="occupied area / initial")
    ax_norm.set_title("Inclusion-phase diagnostics", loc="left", fontweight="bold")
    ax_norm.set_xlabel("non-dimensional time")
    ax_norm.set_ylabel("normalized value")
    ax_norm.set_xlim(0, 1.25)
    ax_norm.set_ylim(0.32, 1.06)
    ax_norm.grid(True, color="#dbe5f0", linewidth=0.75, alpha=0.85)
    ax_norm.legend(frameon=False, loc="lower left")

    for ax in (ax_pos, ax_norm):
        ax.tick_params(length=3.5, width=0.75)
        for spine in ax.spines.values():
            spine.set_linewidth(0.75)

    fig.tight_layout(w_pad=2.2)
    output = OUT_DIR / filename
    fig.savefig(output, facecolor="white", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    return output


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(PLOT_RC)

    gif, gif_frames = make_schlieren_gif()
    pressure = plot_field(25, "pres", "pressure-midrun.png")
    alpha = plot_field(50, "alpha2", "inclusion-volume-final.png")
    vorticity = plot_field(50, "omega3", "vorticity-final.png")
    probes = plot_probe_history("probe-pressure-history.png")
    material = plot_material_diagnostics("material-diagnostics.png")

    manifest = {
        "generatedFrom": str(RUN_DIR),
        "items": [
            {"role": "hero", "src": f"{PROJECT_ASSET_PREFIX}/{gif.name}", "frames": gif_frames},
            {"role": "pressure", "src": f"{PROJECT_ASSET_PREFIX}/{pressure.name}", "step": 25},
            {"role": "alpha2", "src": f"{PROJECT_ASSET_PREFIX}/{alpha.name}", "step": 50},
            {"role": "vorticity", "src": f"{PROJECT_ASSET_PREFIX}/{vorticity.name}", "step": 50},
            {"role": "probes", "src": f"{PROJECT_ASSET_PREFIX}/{probes.name}"},
            {"role": "material-diagnostics", "src": f"{PROJECT_ASSET_PREFIX}/{material.name}"},
        ],
    }
    (OUT_DIR / "assets-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote SWM assets to {OUT_DIR}")


if __name__ == "__main__":
    main()

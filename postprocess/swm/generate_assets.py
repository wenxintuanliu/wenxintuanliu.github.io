#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


RUN_DIR = Path("/home/chunfengfusu/MFC_run/runs/swm")
SILO_DIR = RUN_DIR / "silo_hdf5"
OUT_DIR = Path("/home/chunfengfusu/web/research-showcase/assets/projects/swm")
PROJECT_ASSET_PREFIX = "assets/projects/swm"

VAR_DATASETS = {
    "alpha2": "#000013",
    "omega3": "#000014",
    "pres": "#000011",
    "rho": "#000005",
    "schlieren": "#000015",
    "vel1": "#000008",
    "vel2": "#000009",
}

FIELD_STYLE = {
    "schlieren": {
        "title": "Schlieren field",
        "cmap": "magma",
        "label": "numerical schlieren",
        "robust": (1, 99.6),
    },
    "pres": {
        "title": "Pressure field",
        "cmap": "viridis",
        "label": "pressure",
        "robust": (1, 99),
    },
    "alpha2": {
        "title": "Inclusion volume fraction",
        "cmap": "cividis",
        "label": "alpha_2",
        "vmin": 0,
        "vmax": 1,
    },
    "omega3": {
        "title": "Spanwise vorticity",
        "cmap": "RdBu_r",
        "label": "omega_3",
        "robust": (1, 99),
        "symmetric": True,
    },
}


def read_blocks(step: int, variable: str):
    dataset = VAR_DATASETS[variable]
    blocks = []
    for rank in range(4):
        path = SILO_DIR / f"p{rank}" / f"{step}.silo"
        with h5py.File(path, "r") as f:
            x = f[".silo/#000001"][:]
            y = f[".silo/#000002"][:]
            raw = f[f".silo/{dataset}"][:]
            values = raw.ravel(order="C").reshape((len(y) - 1, len(x) - 1))
        blocks.append((x, y, values))
    return blocks


def plot_field(step: int, variable: str, filename: str, *, title_suffix: str = "") -> Path:
    style = FIELD_STYLE[variable]
    blocks = read_blocks(step, variable)
    all_values = np.concatenate([block[2].ravel() for block in blocks])
    if "vmin" in style:
        vmin = style["vmin"]
        vmax = style["vmax"]
    elif style.get("symmetric"):
        limit = float(np.nanpercentile(np.abs(all_values), style["robust"][1]))
        vmin, vmax = -limit, limit
    else:
        lo, hi = np.nanpercentile(all_values, style["robust"])
        vmin, vmax = float(lo), float(hi)

    fig, ax = plt.subplots(figsize=(11.5, 5.5), dpi=160)
    mesh = None
    for x, y, values in blocks:
        mesh = ax.pcolormesh(
            x,
            y,
            values,
            shading="auto",
            cmap=style["cmap"],
            vmin=vmin,
            vmax=vmax,
        )

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-1.2, 2.4)
    ax.set_ylim(-0.9, 0.9)
    ax.set_xlabel("x / L")
    ax.set_ylabel("y / L")
    ax.set_title(f"{style['title']} at t = {step * 0.025:.3f}{title_suffix}")
    ax.grid(False)
    colorbar = fig.colorbar(mesh, ax=ax, fraction=0.028, pad=0.02)
    colorbar.set_label(style["label"])
    fig.tight_layout(pad=0.6)

    output = OUT_DIR / filename
    fig.savefig(output)
    plt.close(fig)
    return output


def make_schlieren_gif() -> tuple[Path, list[str]]:
    frame_steps = list(range(0, 51, 5))
    all_values = np.concatenate(
        [block[2].ravel() for step in frame_steps for block in read_blocks(step, "schlieren")]
    )
    vmin, vmax = np.nanpercentile(all_values, FIELD_STYLE["schlieren"]["robust"])
    frame_paths = []
    for step in frame_steps:
        frame_paths.append(plot_gif_frame(step, "schlieren", f"schlieren-frame-{step:05d}.png", vmin, vmax))

    frames = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in frame_paths]
    output = OUT_DIR / "schlieren-evolution.gif"
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=170,
        loop=0,
        optimize=False,
    )
    for frame in frames:
        frame.close()
    return output, [path.name for path in frame_paths]


def plot_gif_frame(step: int, variable: str, filename: str, vmin: float, vmax: float) -> Path:
    style = FIELD_STYLE[variable]
    fig = plt.figure(figsize=(12, 6), dpi=120)
    ax = fig.add_axes((0, 0, 1, 1))
    for x, y, values in read_blocks(step, variable):
        ax.pcolormesh(
            x,
            y,
            values,
            shading="auto",
            cmap=style["cmap"],
            vmin=vmin,
            vmax=vmax,
        )
    ax.set_xlim(-1.2, 2.4)
    ax.set_ylim(-0.9, 0.9)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    output = OUT_DIR / filename
    fig.savefig(output, dpi=120, facecolor="black")
    plt.close(fig)
    return output


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gif, gif_frames = make_schlieren_gif()
    pressure = plot_field(25, "pres", "pressure-midrun.png")
    alpha = plot_field(50, "alpha2", "inclusion-volume-final.png")
    vorticity = plot_field(50, "omega3", "vorticity-final.png")

    manifest = {
        "generatedFrom": str(RUN_DIR),
        "items": [
            {"role": "hero", "src": f"{PROJECT_ASSET_PREFIX}/{gif.name}", "frames": gif_frames},
            {"role": "pressure", "src": f"{PROJECT_ASSET_PREFIX}/{pressure.name}", "step": 25},
            {"role": "alpha2", "src": f"{PROJECT_ASSET_PREFIX}/{alpha.name}", "step": 50},
            {"role": "vorticity", "src": f"{PROJECT_ASSET_PREFIX}/{vorticity.name}", "step": 50},
        ],
    }
    (OUT_DIR / "assets-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

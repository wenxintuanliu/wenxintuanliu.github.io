#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.tri as mtri
import numpy as np
from PIL import Image
import pymech.neksuite as nek

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "assets/projects/square"
RUN_DIR = Path("/home/chunfengfusu/Nek5000/run/square")
GIF_FRAME_COUNT = 24
FONT = {
    "axes.titlesize": 22,
    "axes.labelsize": 20,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "legend.fontsize": 15,
    "figure.titlesize": 23,
}

def speed(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    return np.sqrt(u**2 + v**2)

def set_plane_axes(ax, xlim, ylim) -> None:
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x / D")
    ax.set_ylabel("y / D")
    ax.grid(False)

def round_up_tenth(value: float) -> float:
    return max(0.1, float(np.ceil(value * 10.0) / 10.0))

def add_colorbar(fig, ax, contour, vmax: float, label: str, fmt: str = "%.1f", shrink: float = 0.88) -> None:
    ticks = np.linspace(0, vmax, 6)
    cbar = fig.colorbar(contour, ax=ax, fraction=0.027, pad=0.014, ticks=ticks, shrink=shrink)
    cbar.ax.yaxis.set_major_formatter(mticker.FormatStrFormatter(fmt))
    cbar.set_label(label)
    cbar.ax.tick_params(labelsize=15)

def contour_field(ax, tri: mtri.Triangulation, values: np.ndarray, title: str, cmap: str, vmin: float, vmax: float, xlim, ylim):
    levels = np.linspace(vmin, vmax, 96)
    plot_values = np.clip(values, vmin, vmax)
    contour = ax.tricontourf(tri, plot_values, levels=levels, cmap=cmap, vmin=vmin, vmax=vmax, extend="both")
    set_plane_axes(ax, xlim, ylim)
    
    # Add a square patch at the origin representing the square cylinder
    # Adjust position/size if necessary. Assuming centered at 0, size 1x1 
    # (-0.5 to 0.5) like typical D=1 setup.
    rect = plt.Rectangle((-0.5, -0.5), 1.0, 1.0, facecolor="white", edgecolor="#1f2937", linewidth=1.25, zorder=5)
    ax.add_patch(rect)
    
    if title:
        ax.set_title(title, loc="left", fontweight="bold")
    return contour

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(FONT)

    # get list of snapshot files
    files = sorted(RUN_DIR.glob("square0.f00*"))
    if not files:
        print("No snapshot files found!")
        return

    # sub-sample for GIF
    indices = np.linspace(0, len(files) - 1, GIF_FRAME_COUNT, dtype=int)
    selected_files = [files[i] for i in indices]

    # read first file to setup mesh
    field0 = nek.readnek(str(selected_files[0]))
    x = np.array([e.pos[0] for e in field0.elem]).flatten()
    y = np.array([e.pos[1] for e in field0.elem]).flatten()
    tri = mtri.Triangulation(x, y)
    
    # remove triangles inside the cylinder
    # calculate triangle centroids
    pts = np.vstack([x, y]).T
    triangles = tri.triangles
    centroids = pts[triangles].mean(axis=1)
    mask = (np.abs(centroids[:, 0]) < 0.48) & (np.abs(centroids[:, 1]) < 0.48)
    tri.set_mask(mask)

    xlim = (float(x.min()), float(x.max()))
    ylim = (float(y.min()), float(y.max()))

    vmax = 1.5  # Fixed scale based on prior check

    frame_paths = []
    
    for i, file in enumerate(selected_files):
        try:
            field = nek.readnek(str(file))
        except Exception as e:
            print(f"Failed to read {file}: {e}")
            continue
            
        u = np.array([e.vel[0] for e in field.elem]).flatten()
        v = np.array([e.vel[1] for e in field.elem]).flatten()
        
        values = speed(u, v)
        time_val = field.time

        fig, ax = plt.subplots(figsize=(10.8, 5.8), dpi=120)
        # DIFFERENT COLORMAP than cyl (using plasma)
        contour = contour_field(ax, tri, values, f"Time: {time_val:.2f}", "plasma", vmin=0, vmax=vmax, xlim=xlim, ylim=ylim)
        add_colorbar(fig, ax, contour, vmax, "|u|", shrink=0.72)
        fig.subplots_adjust(left=0.085, right=0.92, bottom=0.14, top=0.90)
        
        frame_path = OUT_DIR / f"frame_{i:04d}.png"
        fig.savefig(frame_path, facecolor="white", pad_inches=0)
        plt.close(fig)
        frame_paths.append(frame_path)
        print(f"Processed frame {i+1}/{len(selected_files)}")

    if not frame_paths:
        return

    # combine into GIF
    gif_path = OUT_DIR / "square_flow.gif"
    frames = [Image.open(fp).convert("P", palette=Image.Palette.ADAPTIVE) for fp in frame_paths]
    if frames:
        frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=150, loop=0, optimize=True)
        for img in frames:
            img.close()

    for fp in frame_paths:
        fp.unlink(missing_ok=True)

    manifest = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceData": str(RUN_DIR),
        "items": [
            {
                "type": "animation",
                "role": "hero",
                "title": "Square Cylinder Flow Speed Field",
                "src": "assets/projects/square/square_flow.gif",
                "frameCount": len(frame_paths),
                "method": "Rendered from Nek5000 square0.f* output files",
            }
        ]
    }
    
    (OUT_DIR / "assets-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote assets to {OUT_DIR}")

if __name__ == "__main__":
    main()

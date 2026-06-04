#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from pymech.neksuite import readnek


logging.getLogger("pysemtools").setLevel(logging.WARNING)

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "assets/projects/lid-obstacle"
FIELD_DIR = Path("/mnt/e/BAE_data/new/new_Reob5000xi_2")
FIELD_TEMPLATE = "insldc0.f{index:05d}"
Z_LEVEL = 0.1
NX = 512
NY = 512
GIF_FRAME_DURATION_MS = 300
FRAME_INDICES = np.linspace(1, 1001, 12, dtype=int).tolist()
OBSTACLE_MIN = 0.4
OBSTACLE_MAX = 0.6
OBSTACLE_DRAW_PAD = 0.006

INTERPOLATION_CORE = Path("/home/chunfengfusu/nek5000_44stats_Re5000_ob/plot_a_fields")
if str(INTERPOLATION_CORE) not in sys.path:
    sys.path.insert(0, str(INTERPOLATION_CORE))

from core.interpolation import NekHighPrecisionInterpolator, collect_component  # noqa: E402


STREAMLINE_SOURCES = [
    (
        "re1000-base",
        "Re = 1000, no obstacle",
        Path("/home/chunfengfusu/nek5000_44stats_Re1000/plot_a_fields/workflows/stream_vort/output/plane_y05_streamline_velocity.png"),
    ),
    (
        "re1000-obstacle",
        "Re = 1000, with obstacle",
        Path("/home/chunfengfusu/nek5000_44stats_Re1000_ob/plot_a_fields/workflows/stream_vort/output/plane_y05_streamline_velocity.png"),
    ),
    (
        "re3200-base",
        "Re = 3200, no obstacle",
        Path("/home/chunfengfusu/nek5000_44stats_Re3200/plot_a_fields/workflows/stream_vort/output/plane_y05_streamline_velocity.png"),
    ),
    (
        "re3200-obstacle",
        "Re = 3200, with obstacle",
        Path("/home/chunfengfusu/nek5000_44stats_Re3200_ob/plot_a_fields/workflows/stream_vort/output/plane_y05_streamline_velocity.png"),
    ),
    (
        "re5000-base",
        "Re = 5000, no obstacle",
        Path("/home/chunfengfusu/nek5000_44stats_Re5000/plot_a_fields/workflows/stream_vort/output/plane_y05_streamline_velocity.png"),
    ),
    (
        "re5000-obstacle",
        "Re = 5000, with obstacle",
        Path("/home/chunfengfusu/nek5000_44stats_Re5000_ob/plot_a_fields/workflows/stream_vort/output/plane_y05_streamline_velocity.png"),
    ),
]


def copy_streamline_assets() -> list[dict]:
    items = []
    for key, title, src in STREAMLINE_SOURCES:
        if not src.exists():
            raise FileNotFoundError(src)
        out_name = f"mean-streamline-{key}.png"
        shutil.copy2(src, OUT_DIR / out_name)
        items.append(
            {
                "type": "image",
                "role": "mean-streamline",
                "title": title,
                "src": f"assets/projects/lid-obstacle/{out_name}",
                "sourceFile": str(src),
                "method": "existing averaged streamline velocity plot on y = 0.5",
            }
        )
    return items


def build_grid() -> dict:
    x = np.linspace(0.0, 1.0, NX)
    y = np.linspace(0.0, 1.0, NY)
    xx, yy = np.meshgrid(x, y)
    zz = np.full_like(xx, Z_LEVEL)
    points = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])
    return {"x": x, "y": y, "xx": xx, "yy": yy, "points": points}


def interpolate_velocity(interpolator, cache, field_data, shape: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    u = interpolator.eval_scalar_field(collect_component(field_data, "vel", 0), cache).reshape(shape)
    v = interpolator.eval_scalar_field(collect_component(field_data, "vel", 1), cache).reshape(shape)
    mask = cache.rcode.reshape(shape) <= 1
    u = np.where(mask, u, np.nan)
    v = np.where(mask, v, np.nan)
    return u, v


def compute_vorticity_z(u: np.ndarray, v: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    valid = np.isfinite(u) & np.isfinite(v)
    omega = np.full(u.shape, np.nan, dtype=float)
    stencil = valid.copy()
    stencil[0, :] = False
    stencil[-1, :] = False
    stencil[:, 0] = False
    stencil[:, -1] = False
    stencil[1:, :] &= valid[:-1, :]
    stencil[:-1, :] &= valid[1:, :]
    stencil[:, 1:] &= valid[:, :-1]
    stencil[:, :-1] &= valid[:, 1:]
    ii, jj = np.where(stencil)
    omega[ii, jj] = (
        (v[ii, jj + 1] - v[ii, jj - 1]) / (x[jj + 1] - x[jj - 1])
        - (u[ii + 1, jj] - u[ii - 1, jj]) / (y[ii + 1] - y[ii - 1])
    )
    return omega


def apply_obstacle_mask(field: np.ndarray, grid: dict) -> np.ndarray:
    obstacle = (
        (grid["xx"] >= OBSTACLE_MIN)
        & (grid["xx"] <= OBSTACLE_MAX)
        & (grid["yy"] >= OBSTACLE_MIN)
        & (grid["yy"] <= OBSTACLE_MAX)
    )
    return np.where(obstacle, np.nan, field)


def plot_vorticity(omega: np.ndarray, grid: dict, out_path: Path, title: str, vmax: float) -> None:
    fig, ax = plt.subplots(figsize=(6.8, 6.2), dpi=150)
    cmap = plt.get_cmap("RdBu_r").copy()
    cmap.set_bad("#f7f8f4")
    image = ax.imshow(
        omega,
        extent=[0.0, 1.0, 0.0, 1.0],
        origin="lower",
        cmap=cmap,
        vmin=-vmax,
        vmax=vmax,
        # Display resampling only. The field values were obtained by pysemtools
        # Probes spectral interpolation before vorticity was computed.
        interpolation="nearest",
        aspect="equal",
    )
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(title, loc="left", fontweight="bold")
    ax.add_patch(
        plt.Rectangle(
            (OBSTACLE_MIN - OBSTACLE_DRAW_PAD, OBSTACLE_MIN - OBSTACLE_DRAW_PAD),
            OBSTACLE_MAX - OBSTACLE_MIN + 2 * OBSTACLE_DRAW_PAD,
            OBSTACLE_MAX - OBSTACLE_MIN + 2 * OBSTACLE_DRAW_PAD,
            facecolor="#f7f8f4",
            edgecolor="#f7f8f4",
            linewidth=0.0,
            antialiased=False,
            zorder=20,
        )
    )
    cbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(r"$\omega_z$")
    fig.tight_layout()
    fig.savefig(out_path, facecolor="#f7f8f4")
    plt.close(fig)


def make_gif(frame_paths: list[Path], out_path: Path) -> None:
    frames = [Image.open(path).convert("P", palette=Image.ADAPTIVE) for path in frame_paths]
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=GIF_FRAME_DURATION_MS, loop=0, optimize=True)


def generate_vorticity_gif() -> list[dict]:
    grid = build_grid()
    first_path = FIELD_DIR / FIELD_TEMPLATE.format(index=FRAME_INDICES[0])
    first_data = readnek(str(first_path))
    interpolator = NekHighPrecisionInterpolator(first_data, max_pts=512)
    cache = interpolator.locate_points(grid["points"][:, 0], grid["points"][:, 1], grid["points"][:, 2])

    vorticity_frames = []
    frame_data = []
    for index in FRAME_INDICES:
        path = FIELD_DIR / FIELD_TEMPLATE.format(index=index)
        field_data = first_data if path == first_path else readnek(str(path))
        u, v = interpolate_velocity(interpolator, cache, field_data, grid["xx"].shape)
        omega = compute_vorticity_z(u, v, grid["x"], grid["y"])
        omega = apply_obstacle_mask(omega, grid)
        vorticity_frames.append(omega)
        frame_data.append((index, float(getattr(field_data, "time", index)), path))

    finite_values = np.concatenate([np.abs(frame[np.isfinite(frame)]).ravel() for frame in vorticity_frames])
    vmax = max(1.0e-6, float(np.nanpercentile(finite_values, 98.0)))

    frame_paths = []
    for omega, (index, time_value, path) in zip(vorticity_frames, frame_data):
        out_name = f"vorticity-z010-frame-{index:05d}.png"
        out_path = OUT_DIR / out_name
        plot_vorticity(omega, grid, out_path, f"z = {Z_LEVEL:.1f} vorticity  |  t = {time_value:.2f}", vmax)
        frame_paths.append(out_path)

    make_gif(frame_paths, OUT_DIR / "vorticity-z010-spectral512.gif")
    return [
        {
            "type": "animation",
            "role": "feature",
            "title": f"Vorticity evolution on z = {Z_LEVEL:.1f}",
            "src": "assets/projects/lid-obstacle/vorticity-z010-spectral512.gif",
            "sourceDirectory": str(FIELD_DIR),
            "frameCount": len(frame_paths),
            "durationMs": GIF_FRAME_DURATION_MS,
            "method": "pysemtools spectral interpolation on a z = 0.1 probe plane",
        }
    ]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    items.extend(generate_vorticity_gif())
    items.extend(copy_streamline_assets())

    manifest = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceFieldDirectory": str(FIELD_DIR),
        "streamlineSources": [str(item[2]) for item in STREAMLINE_SOURCES],
        "slice": {"plane": "z", "level": Z_LEVEL, "nx": NX, "ny": NY},
        "method": "pysemtools Probes spectral interpolation with multiple_point_legendre_numpy for instantaneous vorticity GIF; existing y = 0.5 averaged streamline figures copied from local Nek5000 postprocessing.",
        "items": items,
    }
    (OUT_DIR / "assets-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote assets to {OUT_DIR}")
    print(f"items={len(items)}")


if __name__ == "__main__":
    main()

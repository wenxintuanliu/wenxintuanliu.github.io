#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import h5py
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.tri as mtri
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "assets/projects/cyl4"
DATA_DIR = Path("/home/chunfengfusu/NekRS_run/cyl2/z2_plane/data")
AE_DIR = Path("/home/chunfengfusu/NekRS_run/cyl2/z2_plane/sindy/GNN_SINDY/outputs/rom_stage1_gcn_ae_z4")
H5_FILE = DATA_DIR / "cyl_z2_sindy.h5"
METADATA_FILE = DATA_DIR / "metadata.json"
AE_FILE = AE_DIR / "ae_latent.npz"
SUMMARY_FILE = AE_DIR / "summary.json"
HISTORY_IMAGE = AE_DIR / "training_history.png"
SNAPSHOT_INDEX = 450
GIF_FRAME_COUNT = 28
FONT = {
    "axes.titlesize": 22,
    "axes.labelsize": 20,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "legend.fontsize": 15,
    "figure.titlesize": 23,
}


def load_flow() -> dict[str, np.ndarray]:
    with h5py.File(H5_FILE, "r") as handle:
        return {
            "fields": handle["fields"][:],
            "times": handle["time"][:],
            "pos": handle["graph/pos"][:],
            "edge_index": handle["graph/edge_index"][:],
        }


def speed(field: np.ndarray) -> np.ndarray:
    return np.sqrt(np.sum(field[:, :2] ** 2, axis=1))


def field_limits(pos: np.ndarray) -> tuple[tuple[float, float], tuple[float, float]]:
    return (float(pos[:, 0].min()), float(pos[:, 0].max())), (float(pos[:, 1].min()), float(pos[:, 1].max()))


def set_plane_axes(ax, pos: np.ndarray) -> None:
    xlim, ylim = field_limits(pos)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x / D")
    ax.set_ylabel("y / D")
    ax.grid(False)


def add_cylinder(ax) -> None:
    cyl = plt.Circle((0, 0), 0.5, facecolor="white", edgecolor="#1f2937", linewidth=1.25, zorder=5)
    ax.add_patch(cyl)


def build_triangulation(pos: np.ndarray) -> mtri.Triangulation:
    tri = mtri.Triangulation(pos[:, 0], pos[:, 1])
    pts = pos[:, :2]
    triangles = tri.triangles
    edge_lengths = np.stack(
        [
            np.linalg.norm(pts[triangles[:, 0]] - pts[triangles[:, 1]], axis=1),
            np.linalg.norm(pts[triangles[:, 1]] - pts[triangles[:, 2]], axis=1),
            np.linalg.norm(pts[triangles[:, 2]] - pts[triangles[:, 0]], axis=1),
        ],
        axis=1,
    )
    centroids = pts[triangles].mean(axis=1)
    mask = (edge_lengths.max(axis=1) > 0.35) | (np.linalg.norm(centroids, axis=1) < 0.52)
    tri.set_mask(mask)
    return tri


def round_up_tenth(value: float) -> float:
    return max(0.1, float(np.ceil(value * 10.0) / 10.0))


def add_colorbar(fig, ax, contour, vmax: float, label: str, fmt: str = "%.1f", shrink: float = 0.88) -> None:
    ticks = np.linspace(0, vmax, 6)
    cbar = fig.colorbar(contour, ax=ax, fraction=0.027, pad=0.014, ticks=ticks, shrink=shrink)
    cbar.ax.yaxis.set_major_formatter(mticker.FormatStrFormatter(fmt))
    cbar.set_label(label)
    cbar.ax.tick_params(labelsize=15)


def contour_field(ax, tri: mtri.Triangulation, pos: np.ndarray, values: np.ndarray, title: str, cmap: str, vmin: float, vmax: float):
    levels = np.linspace(vmin, vmax, 96)
    plot_values = np.clip(values, vmin, vmax)
    contour = ax.tricontourf(tri, plot_values, levels=levels, cmap=cmap, vmin=vmin, vmax=vmax)
    set_plane_axes(ax, pos)
    add_cylinder(ax)
    if title:
        ax.set_title(title, loc="left", fontweight="bold")
    return contour


def plot_flow_frame(flow: dict[str, np.ndarray], tri: mtri.Triangulation, index: int, out: Path, vmax: float) -> None:
    pos = flow["pos"]
    t = float(flow["times"][index])
    values = speed(flow["fields"][index])
    fig, ax = plt.subplots(figsize=(13.6, 7.2), dpi=150)
    contour = contour_field(ax, tri, pos, values, "", "viridis", vmin=0, vmax=vmax)
    add_colorbar(fig, ax, contour, vmax, "|u|", shrink=0.72)
    fig.subplots_adjust(left=0.085, right=0.92, bottom=0.14, top=0.90)
    fig.savefig(out, facecolor="white", pad_inches=0)
    plt.close(fig)


def make_flow_gif(flow: dict[str, np.ndarray], out: Path) -> dict:
    indices = np.linspace(0, flow["fields"].shape[0] - 1, GIF_FRAME_COUNT, dtype=int)
    tri = build_triangulation(flow["pos"])
    vmax = round_up_tenth(float(np.max(speed(flow["fields"][indices].reshape(-1, 2)))))
    frame_paths = []
    for index in indices:
        frame = OUT_DIR / f"flow-frame-{int(index):04d}.png"
        plot_flow_frame(flow, tri, int(index), frame, vmax)
        frame_paths.append(frame)

    frames = [Image.open(path).convert("P", palette=Image.Palette.ADAPTIVE) for path in frame_paths]
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=130, loop=0, optimize=False)
    for image in frames:
        image.close()
    for path in frame_paths:
        path.unlink(missing_ok=True)

    return {
        "firstSnapshot": int(indices[0]),
        "lastSnapshot": int(indices[-1]),
        "frameCount": int(len(indices)),
        "firstTime": float(flow["times"][indices[0]]),
        "lastTime": float(flow["times"][indices[-1]]),
    }


def plot_snapshot_compare(flow: dict[str, np.ndarray], ae: dict[str, np.ndarray], out: Path) -> dict:
    pos = flow["pos"]
    tri = build_triangulation(pos)
    t = float(flow["times"][SNAPSHOT_INDEX])
    truth = flow["fields"][SNAPSHOT_INDEX]
    recon = ae["reconstruction"][SNAPSHOT_INDEX]
    truth_speed = speed(truth)
    recon_speed = speed(recon)
    abs_err = np.abs(truth_speed - recon_speed)
    vmax = round_up_tenth(float(max(np.max(truth_speed), np.max(recon_speed))))
    err_vmax = round_up_tenth(float(np.percentile(abs_err, 99.6)))

    fig, axes = plt.subplots(3, 1, figsize=(13.8, 13.2), dpi=180, constrained_layout=True)
    panels = [
        (truth_speed, "", "viridis", 0, vmax, "|u|", "%.1f"),
        (recon_speed, "", "viridis", 0, vmax, "|u|", "%.1f"),
        (abs_err, "", "magma", 0, err_vmax, "error", "%.2f"),
    ]
    for ax, panel in zip(axes, panels):
        values, title, cmap, vmin, vmax_panel, label, fmt = panel
        contour = contour_field(ax, tri, pos, values, title, cmap, vmin=vmin, vmax=vmax_panel)
        add_colorbar(fig, ax, contour, vmax_panel, label, fmt)
    fig.suptitle("")
    fig.savefig(out, facecolor="white", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    return {"snapshot": SNAPSHOT_INDEX, "time": t}


def plot_latent_components(ae: dict[str, np.ndarray], out: Path) -> None:
    times = ae["times"]
    z = ae["z"]
    fig, ax = plt.subplots(figsize=(12.5, 6.8), dpi=180)
    for i in range(min(4, z.shape[1])):
        ax.plot(times, z[:, i], linewidth=2.0, label=f"z{i + 1}")
    ax.axvline(times[400], color="#6b7280", linestyle="--", linewidth=1.4, label="train/validation split")
    ax.set_xlabel("time")
    ax.set_ylabel("latent coordinate")
    ax.set_title("GCN-AE latent trajectory", loc="left", fontweight="bold")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, ncol=5)
    fig.tight_layout()
    fig.savefig(out, facecolor="white", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def plot_latent_phase(ae: dict[str, np.ndarray], out: Path) -> None:
    z = ae["z"]
    times = ae["times"]
    fig, ax = plt.subplots(figsize=(8.4, 7.2), dpi=180)
    sc = ax.scatter(z[:, 0], z[:, 1], c=times, s=22, cmap="viridis", edgecolor="none")
    ax.set_xlabel("z1")
    ax.set_ylabel("z2")
    ax.set_title("Latent phase portrait", loc="left", fontweight="bold")
    ax.grid(True, alpha=0.22)
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("time")
    fig.tight_layout()
    fig.savefig(out, facecolor="white", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def plot_graph_preview(flow: dict[str, np.ndarray], out: Path) -> None:
    pos = flow["pos"]
    edge_index = flow["edge_index"]
    rng = np.random.default_rng(7)
    edge_ids = rng.choice(edge_index.shape[1], size=min(7000, edge_index.shape[1]), replace=False)
    fig, ax = plt.subplots(figsize=(11.5, 6.4), dpi=180)
    for a, b in edge_index[:, edge_ids].T:
        ax.plot(pos[[a, b], 0], pos[[a, b], 1], color="#94a3b8", linewidth=0.22, alpha=0.18)
    ax.scatter(pos[:, 0], pos[:, 1], s=1.4, color="#0d9488", alpha=0.75)
    set_plane_axes(ax, pos)
    add_cylinder(ax)
    ax.set_title("Static graph on NekRS z = 2 plane", loc="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out, facecolor="white", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(FONT)

    flow = load_flow()
    ae = dict(np.load(AE_FILE))
    metadata = read_json(METADATA_FILE)
    summary = read_json(SUMMARY_FILE)

    gif_info = make_flow_gif(flow, OUT_DIR / "flow-evolution.gif")
    snapshot_info = plot_snapshot_compare(flow, ae, OUT_DIR / "gcn-ae-reconstruction-t0450.png")
    plot_latent_components(ae, OUT_DIR / "gcn-ae-latent-components.png")
    plot_graph_preview(flow, OUT_DIR / "gcn-ae-graph-preview.png")
    shutil.copy2(HISTORY_IMAGE, OUT_DIR / "gcn-ae-training-history.png")

    manifest = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceData": str(H5_FILE),
        "aeRun": str(AE_DIR),
        "metadata": metadata,
        "summary": summary,
        "items": [
            {
                "type": "animation",
                "role": "hero",
                "title": "Transient NekRS z = 2 cylinder-wake speed field",
                "src": "assets/projects/cyl4/flow-evolution.gif",
                "timeRange": [gif_info["firstTime"], gif_info["lastTime"]],
                "frameCount": gif_info["frameCount"],
                "method": "Rendered directly from cyl_z2_sindy.h5 velocity snapshots",
            },
            {
                "type": "image",
                "role": "gcn-ae-reconstruction",
                "title": "GCN-AE reconstruction on the z = 2 cylinder-wake plane",
                "src": "assets/projects/cyl4/gcn-ae-reconstruction-t0450.png",
                "time": snapshot_info["time"],
                "method": "Existing GCN-AE output; no SINDy rollout used",
            },
            {
                "type": "image",
                "role": "graph-preview",
                "title": "Static graph built from the NekRS z = 2 plane",
                "src": "assets/projects/cyl4/gcn-ae-graph-preview.png",
                "method": "HDF5 graph/edge_index and graph/pos",
            },
            {
                "type": "image",
                "role": "latent-components",
                "title": "First four latent coordinates over time",
                "src": "assets/projects/cyl4/gcn-ae-latent-components.png",
                "method": "ae_latent.npz z(t)",
            },
            {
                "type": "image",
                "role": "training-history",
                "title": "GCN-AE training history",
                "src": "assets/projects/cyl4/gcn-ae-training-history.png",
                "method": "Copied from Stage 1 GCN-AE output",
            },
        ],
    }
    (OUT_DIR / "assets-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote GCN-AE assets to {OUT_DIR}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import json
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

CASE_DIR = Path("/home/chunfengfusu/NekRS_run/cyl")
DATA_DIR = CASE_DIR / "z2_plane_gnn/data"
AE_DIR = CASE_DIR / "z2_plane_gnn/sindy/GNN_SINDY/GNN/outputs/gnn_autoencoder_oscillator_z2"

H5_FILE = DATA_DIR / "cyl_z2_plane_gnn.h5"
METADATA_FILE = DATA_DIR / "metadata.json"
AE_FILE = AE_DIR / "gnn_latent_reconstruction.npz"
SUMMARY_FILE = AE_DIR / "summary.json"
HISTORY_FILE = AE_DIR / "history.json"
GRAPH_AUDIT_FILE = AE_DIR / "graph_audit.json"

SNAPSHOT_INDEX = 400
GIF_FRAME_COUNT = 28
TRAIN_COUNT = 301

FONT = {
    "font.family": "DejaVu Sans",
    "axes.titlesize": 15,
    "axes.labelsize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 16,
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def add_cylinder(ax, facecolor: str = "white") -> None:
    cyl = plt.Circle((0, 0), 0.5, facecolor=facecolor, edgecolor="#111827", linewidth=1.05, zorder=6)
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
    mask = (edge_lengths.max(axis=1) > 0.36) | (np.linalg.norm(centroids, axis=1) < 0.52)
    tri.set_mask(mask)
    return tri


def round_up_tenth(value: float) -> float:
    return max(0.1, float(np.ceil(value * 10.0) / 10.0))


def add_colorbar(fig, ax, artist, label: str, ticks: np.ndarray, fmt: str = "%.1f") -> None:
    cbar = fig.colorbar(artist, ax=ax, fraction=0.030, pad=0.016, ticks=ticks)
    cbar.ax.yaxis.set_major_formatter(mticker.FormatStrFormatter(fmt))
    cbar.set_label(label)
    cbar.outline.set_linewidth(0.6)


def contour_field(
    ax,
    tri: mtri.Triangulation,
    pos: np.ndarray,
    values: np.ndarray,
    *,
    cmap: str,
    vmin: float,
    vmax: float,
    title: str = "",
):
    levels = np.linspace(vmin, vmax, 80)
    artist = ax.tricontourf(tri, np.clip(values, vmin, vmax), levels=levels, cmap=cmap, vmin=vmin, vmax=vmax)
    set_plane_axes(ax, pos)
    add_cylinder(ax)
    if title:
        ax.set_title(title, loc="left", fontweight="bold")
    return artist


def plot_flow_frame(flow: dict[str, np.ndarray], tri: mtri.Triangulation, index: int, out: Path, vmax: float) -> None:
    fig = plt.figure(figsize=(10.8, 5.9), dpi=130)
    ax = fig.add_axes([0.070, 0.145, 0.790, 0.780])
    cax = fig.add_axes([0.900, 0.235, 0.022, 0.600])
    artist = contour_field(ax, tri, flow["pos"], speed(flow["fields"][index]), cmap="viridis", vmin=0.0, vmax=vmax)
    cbar = fig.colorbar(artist, cax=cax, ticks=np.linspace(0.0, vmax, 5))
    cbar.ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
    cbar.set_label("|u|")
    cbar.outline.set_linewidth(0.6)
    ax.text(
        0.02,
        0.96,
        f"t = {flow['times'][index]:.1f}",
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=12,
        color="#111827",
        bbox={"boxstyle": "round,pad=0.24", "facecolor": "white", "edgecolor": "none", "alpha": 0.82},
    )
    fig.savefig(out, facecolor="white", pad_inches=0.02)
    plt.close(fig)


def make_flow_gif(flow: dict[str, np.ndarray], out: Path) -> dict:
    indices = np.linspace(0, flow["fields"].shape[0] - 1, GIF_FRAME_COUNT, dtype=int)
    tri = build_triangulation(flow["pos"])
    sampled = flow["fields"][indices].reshape(-1, 2)
    vmax = round_up_tenth(float(np.percentile(np.sqrt(np.sum(sampled**2, axis=1)), 99.7)))
    frame_paths = []
    for index in indices:
        frame = OUT_DIR / f"flow-frame-{int(index):04d}.png"
        plot_flow_frame(flow, tri, int(index), frame, vmax)
        frame_paths.append(frame)

    palette_mode = getattr(Image, "Palette", None)
    adaptive = Image.Palette.ADAPTIVE if palette_mode else Image.ADAPTIVE
    frames = [Image.open(path).convert("P", palette=adaptive) for path in frame_paths]
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=135, loop=0, optimize=False)
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


def plot_graph_preview(flow: dict[str, np.ndarray], metadata: dict, graph_audit: dict, out: Path) -> None:
    pos = flow["pos"]
    edge_index = flow["edge_index"]
    rng = np.random.default_rng(7)
    edge_ids = rng.choice(edge_index.shape[1], size=min(7500, edge_index.shape[1]), replace=False)

    fig, ax = plt.subplots(figsize=(10.8, 5.9), dpi=180)
    for a, b in edge_index[:, edge_ids].T:
        ax.plot(pos[[a, b], 0], pos[[a, b], 1], color="#94a3b8", linewidth=0.18, alpha=0.16, zorder=1)
    ax.scatter(pos[:, 0], pos[:, 1], s=1.2, color="#0f766e", alpha=0.72, zorder=2)
    set_plane_axes(ax, pos)
    add_cylinder(ax)
    ax.set_title("Static graph on the NekRS z = 2 plane", loc="left", fontweight="bold")
    ax.text(
        0.985,
        0.035,
        f"{metadata['nodes']} nodes / {metadata['directed_edges']} directed edges\n"
        f"in-degree {graph_audit['in_degree_min_median_max'][0]}-{graph_audit['in_degree_min_median_max'][2]}",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=9.5,
        color="#334155",
        bbox={"boxstyle": "round,pad=0.28", "facecolor": "white", "edgecolor": "#cbd5e1", "alpha": 0.88},
    )
    fig.tight_layout()
    fig.savefig(out, facecolor="white", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def smooth(values: np.ndarray, window: int = 9) -> np.ndarray:
    if values.size < window:
        return values
    kernel = np.ones(window) / window
    padded = np.pad(values, (window // 2, window // 2), mode="edge")
    return np.convolve(padded, kernel, mode="valid")


def plot_training_summary(history: dict, summary: dict, out: Path) -> None:
    total = np.asarray(history["loss"], dtype=float)
    reconstruction = np.asarray(history["reconstruction"], dtype=float)
    epochs = np.arange(1, total.size + 1)

    fig, (ax_loss, ax_bar) = plt.subplots(1, 2, figsize=(12.4, 4.6), dpi=180, gridspec_kw={"width_ratios": [1.45, 1]})

    ax_loss.plot(epochs, total, color="#c2410c", linewidth=0.9, alpha=0.30, label="total loss")
    ax_loss.plot(epochs, smooth(total), color="#c2410c", linewidth=2.2)
    ax_loss.plot(epochs, reconstruction, color="#2563eb", linewidth=0.9, alpha=0.25, label="reconstruction")
    ax_loss.plot(epochs, smooth(reconstruction), color="#2563eb", linewidth=2.0)
    ax_loss.set_yscale("log")
    ax_loss.set_xlabel("epoch")
    ax_loss.set_ylabel("training loss")
    ax_loss.set_title("Training history", loc="left", fontweight="bold")
    ax_loss.grid(True, which="both", alpha=0.22)
    ax_loss.legend(frameon=False, loc="upper right")

    train = summary["train_reconstruction"]
    val = summary["validation_reconstruction"]
    labels = ["global", "u", "v"]
    train_vals = [train["global_rel_l2"], train["u_rel_l2"], train["v_rel_l2"]]
    val_vals = [val["global_rel_l2"], val["u_rel_l2"], val["v_rel_l2"]]
    x = np.arange(len(labels))
    width = 0.36
    ax_bar.bar(x - width / 2, train_vals, width=width, color="#0f766e", label="train")
    ax_bar.bar(x + width / 2, val_vals, width=width, color="#eab308", label="validation")
    ax_bar.set_xticks(x, labels)
    ax_bar.set_ylabel("relative L2")
    ax_bar.set_ylim(0, max(train_vals + val_vals) * 1.23)
    ax_bar.set_title("Final reconstruction error", loc="left", fontweight="bold")
    ax_bar.grid(True, axis="y", alpha=0.22)
    ax_bar.legend(frameon=False)
    for xpos, value in zip(np.r_[x - width / 2, x + width / 2], train_vals + val_vals):
        ax_bar.text(xpos, value + 0.003, f"{value:.3f}", ha="center", va="bottom", fontsize=8.5)

    fig.tight_layout()
    fig.savefig(out, facecolor="white", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def plot_latent_phase(ae: dict[str, np.ndarray], summary: dict, out: Path) -> None:
    z = ae["z"]
    times = ae["times"]
    split_idx = summary["train_count"] - 1

    fig, ax = plt.subplots(figsize=(7.2, 6.1), dpi=190)
    ax.plot(z[: summary["train_count"], 0], z[: summary["train_count"], 1], color="#334155", linewidth=1.0, alpha=0.40)
    ax.plot(z[split_idx:, 0], z[split_idx:, 1], color="#334155", linewidth=1.0, alpha=0.40)
    sc = ax.scatter(z[:, 0], z[:, 1], c=times, s=18, cmap="turbo", edgecolor="none", zorder=3)
    ax.scatter(z[0, 0], z[0, 1], s=44, color="#111827", marker="o", label="start", zorder=4)
    ax.scatter(z[split_idx, 0], z[split_idx, 1], s=54, color="white", edgecolor="#111827", linewidth=1.2, label="train/validation split", zorder=5)
    ax.set_xlabel("z1")
    ax.set_ylabel("z2")
    ax.set_title("Two-dimensional latent phase portrait", loc="left", fontweight="bold")
    ax.grid(True, alpha=0.22)
    ax.set_aspect("equal", adjustable="box")
    ax.legend(frameon=False, loc="upper right")
    cbar = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.035)
    cbar.set_label("simulation time")
    cbar.outline.set_linewidth(0.6)
    fig.tight_layout()
    fig.savefig(out, facecolor="white", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def plot_snapshot_compare(flow: dict[str, np.ndarray], ae: dict[str, np.ndarray], out: Path) -> dict:
    pos = flow["pos"]
    tri = build_triangulation(pos)
    t = float(flow["times"][SNAPSHOT_INDEX])
    truth = flow["fields"][SNAPSHOT_INDEX]
    recon = ae["reconstruction"][SNAPSHOT_INDEX]
    truth_speed = speed(truth)
    recon_speed = speed(recon)
    abs_err = np.abs(truth_speed - recon_speed)
    vmax = round_up_tenth(float(np.percentile(np.r_[truth_speed, recon_speed], 99.7)))
    err_vmax = round_up_tenth(float(np.percentile(abs_err, 99.6)))

    fig, axes = plt.subplots(3, 1, figsize=(10.8, 11.4), dpi=180)
    panels = [
        (truth_speed, "NekRS", "turbo", 0.0, vmax, "|u|", "%.1f", np.linspace(0.0, vmax, 5)),
        (recon_speed, "GCN-AE", "turbo", 0.0, vmax, "|u|", "%.1f", np.linspace(0.0, vmax, 5)),
        (abs_err, "absolute error", "magma", 0.0, err_vmax, "error", "%.2f", np.linspace(0.0, err_vmax, 5)),
    ]
    for ax, panel in zip(axes, panels):
        values, title, cmap, vmin, vmax_panel, label, fmt, ticks = panel
        artist = contour_field(ax, tri, pos, values, cmap=cmap, vmin=vmin, vmax=vmax_panel, title=title)
        add_colorbar(fig, ax, artist, label, ticks, fmt)
    fig.suptitle(f"Validation snapshot {SNAPSHOT_INDEX}, t = {t:.1f}", y=0.995, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out, facecolor="white", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    return {"snapshot": SNAPSHOT_INDEX, "time": t}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(FONT)

    flow = load_flow()
    ae = dict(np.load(AE_FILE))
    metadata = read_json(METADATA_FILE)
    summary = read_json(SUMMARY_FILE)
    history = read_json(HISTORY_FILE)
    graph_audit = read_json(GRAPH_AUDIT_FILE)

    gif_info = make_flow_gif(flow, OUT_DIR / "flow-evolution.gif")
    plot_graph_preview(flow, metadata, graph_audit, OUT_DIR / "gcn-ae-graph-preview.png")
    plot_training_summary(history, summary, OUT_DIR / "gcn-ae-training-history.png")
    plot_latent_phase(ae, summary, OUT_DIR / "gcn-ae-latent-phase.png")
    snapshot_info = plot_snapshot_compare(flow, ae, OUT_DIR / "gcn-ae-reconstruction-t0400.png")

    manifest = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceCase": str(CASE_DIR),
        "sourceData": str(H5_FILE),
        "aeRun": str(AE_DIR),
        "metadata": metadata,
        "graphAudit": graph_audit,
        "summary": summary,
        "items": [
            {
                "type": "animation",
                "role": "hero",
                "title": "NekRS z = 2 cylinder-wake speed field",
                "src": "assets/projects/cyl4/flow-evolution.gif",
                "timeRange": [gif_info["firstTime"], gif_info["lastTime"]],
                "frameCount": gif_info["frameCount"],
            },
            {
                "type": "image",
                "role": "graph-preview",
                "title": "Static graph built from the NekRS z = 2 plane",
                "src": "assets/projects/cyl4/gcn-ae-graph-preview.png",
            },
            {
                "type": "image",
                "role": "training-summary",
                "title": "GCN-AE training history and final reconstruction error",
                "src": "assets/projects/cyl4/gcn-ae-training-history.png",
            },
            {
                "type": "image",
                "role": "latent-phase",
                "title": "Two-dimensional GCN-AE latent phase portrait",
                "src": "assets/projects/cyl4/gcn-ae-latent-phase.png",
            },
            {
                "type": "image",
                "role": "gcn-ae-reconstruction",
                "title": "GCN-AE reconstruction on the z = 2 cylinder-wake plane",
                "src": "assets/projects/cyl4/gcn-ae-reconstruction-t0400.png",
                "snapshot": snapshot_info["snapshot"],
                "time": snapshot_info["time"],
            },
        ],
    }
    (OUT_DIR / "assets-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote GCN-AE assets to {OUT_DIR}")


if __name__ == "__main__":
    main()

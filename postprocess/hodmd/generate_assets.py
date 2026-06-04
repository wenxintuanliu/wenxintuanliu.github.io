#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "assets/projects/cylinder-hodmd"
HODMD_DIR = Path("/home/chunfengfusu/NekRS_run/cyl/z2_plane_gnn/hodmd")
PLOTS = HODMD_DIR / "output_z2/plots_d50"
PRED = HODMD_DIR / "output_z2/plots_d50_prediction"
REPORT = HODMD_DIR / "output_z2/z2_hodmd_report_z2_hodmd_node_uv.txt"
ERROR_REPORT = PLOTS / "error_report_t0301_src0301_d50.txt"
PRED_REPORT = PRED / "prediction_snapshot_report_d50.txt"

IMAGE_MAP = {
    "eigenvalues": PLOTS / "eigenvalues_plot.png",
    "mode-01": PLOTS / "mode_01_d50.png",
    "mode-03": PLOTS / "mode_03_d50.png",
    "mode-05": PLOTS / "mode_05_d50.png",
    "reconstruction": PLOTS / "reconstruction_t0151_src0151_d50.png",
    "prediction": PRED / "compare_t0351_src0351_d50.png",
}


def parse_key_value_report(path: Path) -> dict[str, str]:
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def parse_component_table(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    out = {}
    for line in lines:
        parts = line.split()
        if len(parts) == 4 and parts[0] in {"u", "v"}:
            out[parts[0]] = {"rmse": float(parts[1]), "mae": float(parts[2]), "rel_l2": float(parts[3])}
    global_match = re.search(r"global_rel_l2:\s*([0-9.eE+-]+)", path.read_text(encoding="utf-8"))
    if global_match:
        out["global_rel_l2"] = float(global_match.group(1))
    return out


def parse_prediction_report(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("local_step"):
            continue
        parts = line.split()
        if len(parts) == 6:
            rows.append(
                {
                    "local_step": int(parts[0]),
                    "source_snapshot": int(parts[1]),
                    "time": float(parts[2]),
                    "global_rel_l2": float(parts[3]),
                    "u_rel_l2": float(parts[4]),
                    "v_rel_l2": float(parts[5]),
                }
            )
    return rows


def parse_main_report(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    keys = {}
    for key in ["Tensor size", "dt", "source_train_indices", "source_val_indices", "train_snapshot_count", "validation_snapshot_count", "d_values", "varepsilon_svd", "varepsilon_mode"]:
        match = re.search(rf"{re.escape(key)}:\s*(.+)", text)
        if match:
            keys[key] = match.group(1).strip()
    for key in ["Final train zero-mean RRMSE", "Final train physical RRMSE", "Validation physical RRMSE"]:
        match = re.search(rf"{re.escape(key)}\s*=\s*([0-9.eE+-]+)", text)
        if match:
            keys[key] = float(match.group(1))
    return keys


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for role, src in IMAGE_MAP.items():
        dst = OUT_DIR / src.name
        shutil.copy2(src, dst)
        items.append(
            {
                "type": "image",
                "role": role,
                "title": role.replace("-", " ").title(),
                "src": f"assets/projects/cylinder-hodmd/{src.name}",
                "method": "HODMD d=50 postprocess output",
            }
        )

    metrics = {
        "mainReport": parse_main_report(REPORT),
        "reconstruction": parse_component_table(ERROR_REPORT),
        "prediction": parse_prediction_report(PRED_REPORT),
    }
    manifest = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceDirectory": str(HODMD_DIR),
        "items": items,
        "metrics": metrics,
    }
    (OUT_DIR / "assets-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote HODMD assets to {OUT_DIR}")


if __name__ == "__main__":
    main()

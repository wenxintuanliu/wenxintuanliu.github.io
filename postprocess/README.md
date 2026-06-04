# Postprocess Pipeline

This folder contains local postprocessing scripts that convert raw simulation output
into web-ready research assets.

Current projects:

- `cyl4/`: reads `/home/chunfengfusu/NekRS_run/cyl2/z2_plane/data/cyl_z2_sindy.h5`
  and existing GCN-AE output from `GNN_SINDY/outputs/rom_stage1_gcn_ae_z4`.
  It generates graph, latent, reconstruction, and training-history figures under
  `assets/projects/cyl4/`.
- `hodmd/`: copies HODMD d=50 plots and parses reconstruction/prediction reports
  from `/home/chunfengfusu/NekRS_run/cyl/z2_plane_gnn/hodmd`.

For SEM data, interpolation must be performed through `pysemtools` probes, not
through generic scattered-data interpolation. The plotting layer only displays the
regular probe grid returned by `pysemtools.interpolation.probes.Probes`.

Run:

```bash
python3 postprocess/cyl4/generate_assets.py
python3 postprocess/hodmd/generate_assets.py
```

Project JSON files are maintained manually so the narrative stays aligned with the
Markdown articles and generated assets.

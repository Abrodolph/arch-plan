# Research notes: real floor plan datasets

Goal: real, messy architectural plans with labels, lines and markers. Searched October 2026 from a
sandbox that could reach GitHub, GitLab, Bitbucket, S3/GCS and PyPI only.

## Used

| Dataset | Host | Why |
|---|---|---|
| BRIDGE (ICDAR 2019) | github.com/gesstalt/BRIDGE | About 5,100 real house-plan images committed in git, with symbol boxes and region captions |
| ROBIN / ROBIN++ (ICDAR 2017) | github.com/gesstalt/ROBIN | 510 schematic plans plus 510 hand-drawn versions, a useful contrast set |

## Good datasets that could not be downloaded from the sandbox

| Dataset | Content | Licence | Where |
|---|---|---|---|
| CubiCasa5K | 5,000 scanned Finnish real-estate plans, SVG polygons for 80+ classes (rooms, walls, doors, windows, fixtures) | CC BY-NC 4.0 | zenodo.org/records/2613548 (5.5 GB) |
| CVC-FP | 122 scanned plans, SVG ground truth for walls, doors, windows, rooms | research | dag.cvc.uab.es |
| R2V / Raster-to-Vector | 815 Lianjia (Chinese real-estate) plans; annotations in github.com/art-programmer/FloorplanTransformation, images external | research | see DeepFloorplan download links |
| FloorPlanCAD | 15,000+ real CAD drawings (SVG + PNG) with symbol labels | CC BY-NC 4.0 | Hugging Face mirrors (original site shut down) |
| MLSTRUCT-FP | 954 large multi-unit plans, wall polygons | form-gated | github.com/MLSTRUCT/MLSTRUCT-FP |
| Floor Plans 500 | 500 plans in YOLO format (doors, windows, walls) | CC BY 4.0 | Kaggle / Roboflow Universe |
| Roboflow Universe floor plan sets | thousands of labelled plan images | mostly CC BY 4.0 | universe.roboflow.com |
| Zillow ZInD | 2D floor plans plus panoramas of real homes | licence agreement | github.com/zillow/zind (data on request) |
| LIFULL HOME'S | millions of Japanese real-estate plans | application required | nii.ac.jp |

## Checked and rejected

- HouseExpo / houseExpo++ (github.com/VahidAz/Floorplan_dataset): 35k plans, but only binary outline masks.
- ResPlan (github.com/m-agour/ResPlan): 17k plans as vectors; no original images (used for the Vastu set instead).
- SESYD (inside BRIDGE): synthetic, so excluded.
- YOLO floor-plan GitHub projects (sanatladkat, sreeragvs, mageaustralia, OsamaM0): code and weights only, no data.

# Generate top-down terrain

Use the terrain workflow when the camera must look straight down. Do not start by adding more camera words to a free-form prompt. Choose the output you need first.

## Choose the output

`heightmap` creates a grayscale elevation candidate. Brightness means height. Use this for terrain displacement after review.

`texture` creates a color terrain reference. Color describes the surface. It is not elevation data.

## First run

Preview the full prompt without loading the model:

```bash
python3 scripts/generate_terrain.py \
  --prompt "a volcanic island with radial ridges and a central crater" \
  --mode heightmap \
  --dry-run
```

After `./setup.sh` succeeds, generate a fixed result:

```bash
./scripts/terrain.sh \
  --prompt "a volcanic island with radial ridges and a central crater" \
  --mode heightmap \
  --size 1024x1024 \
  --steps 8 \
  --seed 42 \
  --open
```

The command expands the short description into an orthographic GIS elevation contract. It then checks grayscale saturation, usable tonal range, and clipping.

## Review the result

The numeric check does not prove camera angle or physical elevation. Before using the image as a heightmap, confirm all of these points:

1. There is no visible horizon, sky, or side face.
2. The view is vertical rather than oblique or isometric.
3. Bright areas consistently mean high ground.
4. Dark areas consistently mean low ground.
5. Shading does not create false ridges or valleys.
6. Sea level and the outer map boundary are black, not white or transparent.
7. The terrain reaches the intended map boundary without a perspective frame.

Reject the image when any point fails. Try another seed before changing the contract. If several seeds fail in the same way, record the outputs and treat the behavior as a model limitation rather than a prompt-writing failure.

## Check an existing image

```bash
.venv/bin/python scripts/check_heightmap.py outputs/terrain/heightmap/example.png
```

Use `--json` for automation. A pass means only that the pixels have a usable grayscale range. It does not certify geometry.

## Current setup requirement

On Apple Silicon, local generation requires full Xcode and its Metal Toolchain. Command Line Tools alone are not enough for the pinned MLX build. Run `./setup.sh`; it reports the exact missing prerequisite before downloading the model.

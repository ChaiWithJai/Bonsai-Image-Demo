# Five prompts for top-down terrain in Bonsai

We tested five prompts with the same Bonsai model, seed, image size, and step count. Bonsai can produce a strict top-down terrain image, but it still adds lighting that can create false elevation values.

Prompt 4 came closest to a heightmap. Prompt 5 produced the best visual terrain reference.

## 1. Direct camera description

![Direct camera result](https://raw.githubusercontent.com/ChaiWithJai/Bonsai-Image-Demo/a48b67bc386644dd4bae692a1bcf8d0b9cd38c6a/docs/assets/terrain-prompt-study/01-direct-camera.png)

```text
Absolute top-down view of a volcanic island with radial ridges and a central crater, camera directly overhead at 90 degrees, orthographic projection, grayscale elevation map, black sea level, white mountain summit
```

The camera angle is correct, but directional lighting creates false valleys and peaks.

## 2. GIS digital elevation model

![GIS DEM result](https://raw.githubusercontent.com/ChaiWithJai/Bonsai-Image-Demo/a48b67bc386644dd4bae692a1bcf8d0b9cd38c6a/docs/assets/terrain-prompt-study/02-gis-dem.png)

```text
GIS digital elevation model raster of a volcanic island with radial ridges and a central crater, orthographic nadir map, smooth grayscale altitude values, black zero-elevation ocean, brighter pixels at higher elevations, square dataset
```

The framing is clean, but the surface still uses relief shading instead of elevation alone.

## 3. Game terrain heightmap

![Game heightmap result](https://raw.githubusercontent.com/ChaiWithJai/Bonsai-Image-Demo/a48b67bc386644dd4bae692a1bcf8d0b9cd38c6a/docs/assets/terrain-prompt-study/03-game-heightmap.png)

```text
Game-engine terrain heightmap for a volcanic island with radial ridges and a central crater, seamless square 16-bit-style grayscale displacement map, black lowest elevation, white highest elevation, directly overhead orthographic layout
```

The terrain structure is strong, but the highlights and shadows make the image unsafe for displacement.

## 4. Scalar elevation field

![Scalar field result](https://raw.githubusercontent.com/ChaiWithJai/Bonsai-Image-Demo/a48b67bc386644dd4bae692a1bcf8d0b9cd38c6a/docs/assets/terrain-prompt-study/04-scalar-field.png)

```text
A flat 2D scalar elevation field representing a volcanic island with radial ridges and a central crater, smooth concentric grayscale value gradients, dark low values around the boundary and bright high values toward ridges, scientific raster visualization
```

Prompt 4 produced the closest result to a heightmap because most of the image uses ordered grayscale values. The crater still contains relief artifacts, so the image needs review and cleanup before use.

## 5. Orthographic terrain reference

![Orthographic reference result](https://raw.githubusercontent.com/ChaiWithJai/Bonsai-Image-Demo/a48b67bc386644dd4bae692a1bcf8d0b9cd38c6a/docs/assets/terrain-prompt-study/05-orthophoto-reference.png)

```text
Orthographic satellite-style terrain map of a volcanic island with radial ridges and a central crater, true nadir view from directly overhead, full island footprint centered in a square map tile, no horizon, consistent scale
```

Prompt 5 produced the best top-down terrain reference, but its colors do not encode elevation.

## Recommendation

Start with Prompt 4 and generate several seeds. Reject any result where highlights or shadows create local brightness changes that do not match elevation.

If relief lighting remains, use Prompt 5 to create the visual terrain reference. Then create the production heightmap in a terrain tool that computes elevation values. Converting an image to 16-bit does not recover missing elevation data.

## Test settings

- Model: Bonsai ternary MLX
- Seed: 42
- Size: 512 by 512 pixels
- Steps: 4
- Test run: https://github.com/ChaiWithJai/Bonsai-Image-Demo/actions/runs/33799151821

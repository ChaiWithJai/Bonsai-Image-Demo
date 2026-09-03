"""Prompt contracts for orthographic terrain generation."""

from __future__ import annotations

from typing import Literal

TerrainMode = Literal["heightmap", "texture"]

HEIGHTMAP_CONTRACT = (
    "A single-channel grayscale digital elevation model (DEM) of {description}. "
    "Absolute orthographic nadir projection, viewed vertically from exactly 90 degrees above. "
    "The image is a flat square GIS elevation raster with the full terrain footprint visible. "
    "Pixel brightness encodes elevation only: pure black is the lowest ground and pure white is "
    "the highest ground, with smooth continuous gray elevation gradients between them. "
    "Uniform shadowless illumination, neutral grayscale surface, clean map edges, high relief "
    "separation, scientific terrain height field."
)

TEXTURE_CONTRACT = (
    "An orthographic terrain texture map of {description}. Absolute nadir projection, viewed "
    "vertically from exactly 90 degrees above. The full terrain footprint is visible as a flat "
    "square game-development map tile. Even diffuse lighting, readable land cover, consistent "
    "scale, clean map edges, detailed natural terrain surface."
)


def build_terrain_prompt(description: str, mode: TerrainMode = "heightmap") -> str:
    """Expand a landform description into one explicit terrain contract."""
    clean = " ".join(description.split()).strip(" .")
    if not clean:
        raise ValueError("terrain description cannot be empty")
    if mode == "heightmap":
        return HEIGHTMAP_CONTRACT.format(description=clean)
    if mode == "texture":
        return TEXTURE_CONTRACT.format(description=clean)
    raise ValueError(f"unsupported terrain mode: {mode}")

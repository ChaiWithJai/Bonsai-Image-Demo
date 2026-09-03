"""Check whether an image is numerically usable as a heightmap candidate."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class HeightmapReport:
    width: int
    height: int
    saturation_percent: float
    p05: int
    p95: int
    tonal_span: int
    clipped_low_percent: float
    clipped_high_percent: float
    bright_border_percent: float
    numeric_pass: bool
    visual_review_required: bool
    failures: tuple[str, ...]


def _percentile(histogram: list[int], fraction: float, total: int) -> int:
    target = total * fraction
    seen = 0
    for value, count in enumerate(histogram):
        seen += count
        if seen >= target:
            return value
    return 255


def inspect_heightmap(path: Path) -> HeightmapReport:
    try:
        from PIL import Image, ImageStat
    except ImportError as exc:
        raise RuntimeError("Pillow is required; run ./setup.sh first") from exc

    with Image.open(path) as source:
        rgb = source.convert("RGB")
        gray = rgb.convert("L")
        hsv = rgb.convert("HSV")
        width, height = rgb.size
        histogram = gray.histogram()
        pixels = width * height
        p05 = _percentile(histogram, 0.05, pixels)
        p95 = _percentile(histogram, 0.95, pixels)
        saturation_percent = ImageStat.Stat(hsv).mean[1] / 255 * 100
        clipped_low_percent = sum(histogram[:6]) / pixels * 100
        clipped_high_percent = sum(histogram[250:]) / pixels * 100
        border_width = max(1, min(width, height) // 64)
        border_regions = (
            gray.crop((0, 0, width, border_width)),
            gray.crop((0, height - border_width, width, height)),
            gray.crop((0, border_width, border_width, height - border_width)),
            gray.crop((width - border_width, border_width, width, height - border_width)),
        )
        border_pixels = sum(region.width * region.height for region in border_regions)
        bright_border_pixels = sum(sum(region.histogram()[250:]) for region in border_regions)
        bright_border_percent = bright_border_pixels / border_pixels * 100

    failures: list[str] = []
    if saturation_percent > 8:
        failures.append(
            f"color saturation is {saturation_percent:.1f}%; a heightmap should be grayscale"
        )
    if p95 - p05 < 80:
        failures.append(f"tonal span is {p95 - p05}; elevation separation is too narrow")
    if clipped_high_percent > 35:
        failures.append(f"{clipped_high_percent:.1f}% of pixels are clipped near white")
    if bright_border_percent > 35:
        failures.append(
            f"{bright_border_percent:.1f}% of the map border is near white; "
            "the lowest elevation should frame the terrain"
        )

    return HeightmapReport(
        width=width,
        height=height,
        saturation_percent=round(saturation_percent, 2),
        p05=p05,
        p95=p95,
        tonal_span=p95 - p05,
        clipped_low_percent=round(clipped_low_percent, 2),
        clipped_high_percent=round(clipped_high_percent, 2),
        bright_border_percent=round(bright_border_percent, 2),
        numeric_pass=not failures,
        visual_review_required=True,
        failures=tuple(failures),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check grayscale and elevation range in a heightmap candidate."
    )
    parser.add_argument("image", type=Path)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    if not args.image.is_file():
        parser.error(f"image not found: {args.image}")
    try:
        report = inspect_heightmap(args.image)
    except RuntimeError as exc:
        sys.exit(str(exc))

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(
            f"heightmap: {report.width}x{report.height}  "
            f"saturation={report.saturation_percent:.1f}%  "
            f"range=p05:{report.p05}-p95:{report.p95}  "
            f"clipping={report.clipped_low_percent:.1f}%/{report.clipped_high_percent:.1f}%  "
            f"bright-border={report.bright_border_percent:.1f}%"
        )
        for failure in report.failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        if report.numeric_pass:
            print("PASS: grayscale and elevation range are usable.")
        print("REVIEW: confirm a true top-down projection before using this as elevation data.")

    if not report.numeric_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()

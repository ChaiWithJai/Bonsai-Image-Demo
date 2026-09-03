from __future__ import annotations

import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_terrain import build_command, parse_size  # noqa: E402
from check_heightmap import inspect_heightmap  # noqa: E402
from terrain_prompt import build_terrain_prompt  # noqa: E402


class TerrainPromptTests(unittest.TestCase):
    def test_heightmap_contract_states_projection_and_elevation_encoding(self) -> None:
        prompt = build_terrain_prompt("a volcanic island with radial ridges")
        self.assertIn("orthographic nadir", prompt)
        self.assertIn("exactly 90 degrees above", prompt)
        self.assertIn("brightness encodes elevation only", prompt)
        self.assertIn("black is the lowest", prompt)
        self.assertIn("white is the highest", prompt)
        self.assertIn("volcanic island", prompt)

    def test_texture_mode_does_not_claim_to_be_a_heightmap(self) -> None:
        prompt = build_terrain_prompt("an alpine valley", "texture")
        self.assertIn("terrain texture map", prompt)
        self.assertNotIn("brightness encodes elevation", prompt)

    def test_empty_description_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            build_terrain_prompt("   ")

    def test_size_requires_square_multiple_of_32(self) -> None:
        self.assertEqual(parse_size("1024x1024"), "1024x1024")
        self.assertEqual(parse_size("512×512"), "512x512")
        with self.assertRaisesRegex(Exception, "square"):
            parse_size("1024x768")
        with self.assertRaisesRegex(Exception, "multiple of 32"):
            parse_size("1000x1000")

    def test_guided_request_is_forwarded_to_existing_generator(self) -> None:
        args = Namespace(
            size="1024x1024",
            steps=8,
            model="ternary-gemlite",
            open=True,
            force_gpu_run=True,
        )
        output = ROOT / "outputs" / "terrain" / "heightmap" / "candidate.png"
        prompt = build_terrain_prompt("a glacial valley")

        command = build_command(args, prompt, 42, output)

        self.assertEqual(command[1], str(ROOT / "scripts" / "generate.py"))
        self.assertEqual(command[command.index("--prompt") + 1], prompt)
        self.assertEqual(command[command.index("--size") + 1], "1024x1024")
        self.assertEqual(command[command.index("--steps") + 1], "8")
        self.assertEqual(command[command.index("--seed") + 1], "42")
        self.assertEqual(command[command.index("--output") + 1], str(output))
        self.assertEqual(command[command.index("--model") + 1], "ternary-gemlite")
        self.assertIn("--open", command)
        self.assertIn("--force-gpu-run", command)


class HeightmapCheckTests(unittest.TestCase):
    def save_image(self, image: Image.Image) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "candidate.png"
        image.save(path)
        return path

    def test_grayscale_gradient_passes(self) -> None:
        image = Image.new("L", (256, 256))
        image.putdata([x for _y in range(256) for x in range(256)])
        report = inspect_heightmap(self.save_image(image))
        self.assertTrue(report.numeric_pass)
        self.assertGreaterEqual(report.tonal_span, 200)
        self.assertEqual(report.saturation_percent, 0)

    def test_narrow_tonal_range_fails(self) -> None:
        report = inspect_heightmap(self.save_image(Image.new("L", (256, 256), 120)))
        self.assertFalse(report.numeric_pass)
        self.assertTrue(any("tonal span" in failure for failure in report.failures))

    def test_color_image_fails(self) -> None:
        report = inspect_heightmap(self.save_image(Image.new("RGB", (256, 256), (180, 40, 20))))
        self.assertFalse(report.numeric_pass)
        self.assertTrue(any("color saturation" in failure for failure in report.failures))

    def test_crushed_extremes_fail(self) -> None:
        image = Image.new("L", (256, 256))
        image.putdata([0 if index % 2 else 255 for index in range(256 * 256)])
        report = inspect_heightmap(self.save_image(image))
        self.assertFalse(report.numeric_pass)
        self.assertTrue(any("crushed" in failure for failure in report.failures))
        self.assertTrue(any("clipped" in failure for failure in report.failures))


if __name__ == "__main__":
    unittest.main()

"""Generate a guided top-down terrain image with the existing Bonsai CLI."""

from __future__ import annotations

import argparse
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from terrain_prompt import build_terrain_prompt

DEMO_DIR = Path(__file__).resolve().parent.parent


def parse_size(value: str) -> str:
    normalized = value.lower().replace("×", "x")
    try:
        width_text, height_text = normalized.split("x", 1)
        width, height = int(width_text), int(height_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("size must be WIDTHxHEIGHT") from exc
    if width != height:
        raise argparse.ArgumentTypeError("terrain outputs must be square")
    if not 256 <= width <= 2048 or width % 32:
        raise argparse.ArgumentTypeError("terrain size must be 256-2048 and a multiple of 32")
    return f"{width}x{height}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an orthographic terrain heightmap or texture with Bonsai."
    )
    parser.add_argument("-p", "--prompt", required=True, help="Describe the landform only.")
    parser.add_argument("--mode", choices=("heightmap", "texture"), default="heightmap")
    parser.add_argument("--size", type=parse_size, default="1024x1024")
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--model")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--open", action="store_true")
    parser.add_argument(
        "--force-gpu-run",
        action="store_true",
        help="Linux only: allow the existing generator to run in-process.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the expanded prompt only.")
    parser.add_argument(
        "--skip-check", action="store_true", help="Skip numeric checks for heightmap mode."
    )
    return parser.parse_args()


def build_command(
    args: argparse.Namespace, expanded_prompt: str, seed: int, output: Path
) -> list[str]:
    command = [
        sys.executable,
        str(DEMO_DIR / "scripts" / "generate.py"),
        "--prompt",
        expanded_prompt,
        "--size",
        args.size,
        "--steps",
        str(args.steps),
        "--seed",
        str(seed),
        "--output",
        str(output),
    ]
    if args.model:
        command.extend(("--model", args.model))
    if args.open:
        command.append("--open")
    if args.force_gpu_run:
        command.append("--force-gpu-run")
    return command


def main() -> None:
    args = parse_args()
    expanded_prompt = build_terrain_prompt(args.prompt, args.mode)
    if args.dry_run:
        print(expanded_prompt)
        return

    seed = args.seed if args.seed is not None else secrets.randbits(31)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output = (
        args.output.expanduser().resolve()
        if args.output
        else DEMO_DIR
        / "outputs"
        / "terrain"
        / args.mode
        / f"terrain_{timestamp}_seed{seed}.png"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    command = build_command(args, expanded_prompt, seed, output)

    print(f"Terrain mode: {args.mode}")
    print(f"Expanded prompt: {expanded_prompt}")
    subprocess.run(command, check=True)

    if args.mode == "heightmap" and not args.skip_check:
        subprocess.run(
            [sys.executable, str(DEMO_DIR / "scripts" / "check_heightmap.py"), str(output)],
            check=True,
        )


if __name__ == "__main__":
    main()

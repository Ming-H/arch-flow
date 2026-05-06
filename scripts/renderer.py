#!/usr/bin/env python3
"""Render scene configuration to GIF/MP4 using Manim.

Renders as MP4 first (efficient), then converts to GIF with palette optimization.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"

SCENE_MAP = {
    "basic_flow": ("basic_flow", "BasicFlow"),
    "dag_flow": ("dag_flow", "DagFlow"),
    "pipeline_flow": ("pipeline_flow", "PipelineFlow"),
    "hub_spoke": ("hub_spoke", "HubSpoke"),
}


def render(config: dict, output_path: str, quality: str = "low") -> str:
    template_name = config["template"]
    if template_name not in SCENE_MAP:
        raise ValueError(f"Unknown template: {template_name}")

    template_file, scene_class = SCENE_MAP[template_name]
    template_path = TEMPLATES_DIR / f"{template_file}.py"

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    is_gif = output_path.endswith(".gif")
    is_mp4 = output_path.endswith(".mp4")

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.json")
        with open(config_path, "w") as f:
            json.dump(config, f, ensure_ascii=False)

        quality_flags = {
            "low": "-ql",
            "medium": "-qm",
            "high": "-qh",
            "4k": "-qk",
        }
        qflag = quality_flags.get(quality, "-ql")

        env = os.environ.copy()
        env["ARCH_FLOW_CONFIG"] = config_path

        # Always render as MP4 first (much smaller, higher quality)
        cmd = [
            sys.executable, "-m", "manim", "render",
            qflag,
            "--format", "mp4",
            "--media_dir", tmpdir,
            str(template_path),
            scene_class,
        ]

        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)

        if result.returncode != 0:
            print(f"Manim stderr:\n{result.stderr}")
            raise RuntimeError(f"Manim rendering failed: {result.stderr}")

        mp4_path = _find_output(tmpdir, ".mp4")
        if not mp4_path:
            raise RuntimeError("No MP4 output found after rendering")

        if is_mp4 or not is_gif:
            # Keep as MP4
            shutil.copy2(mp4_path, output_path)
            size_mb = os.path.getsize(output_path) / 1024 / 1024
            print(f"MP4 saved to: {output_path} ({size_mb:.1f}MB)")
            return output_path

        # Convert MP4 → GIF with two-pass palette optimization
        _convert_mp4_to_gif(mp4_path, output_path)
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"GIF saved to: {output_path} ({size_mb:.1f}MB)")
        return output_path


def _find_output(directory: str, ext: str) -> str | None:
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(ext):
                return os.path.join(root, f)
    return None


def _convert_mp4_to_gif(mp4_path: str, output_path: str) -> str:
    palette = output_path + ".palette.png"

    # Pass 1: generate optimal palette
    subprocess.run([
        "ffmpeg", "-y",
        "-i", mp4_path,
        "-vf", "fps=15,scale=1920:-1:flags=lanczos,palettegen=max_colors=256:stats_mode=full",
        palette,
    ], check=True, capture_output=True)

    # Pass 2: convert using palette
    subprocess.run([
        "ffmpeg", "-y",
        "-i", mp4_path,
        "-i", palette,
        "-lavfi", "fps=15,scale=1920:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
        "-loop", "0",
        output_path,
    ], check=True, capture_output=True)

    if os.path.exists(palette):
        os.remove(palette)

    return output_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python renderer.py <config.json> <output.gif|output.mp4> [quality]")
        sys.exit(1)

    config_path = sys.argv[1]
    output_path = sys.argv[2]
    quality = sys.argv[3] if len(sys.argv) > 3 else "low"

    with open(config_path) as f:
        config = json.load(f)

    render(config, output_path, quality)


if __name__ == "__main__":
    main()

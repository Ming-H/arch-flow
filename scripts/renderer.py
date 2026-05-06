#!/usr/bin/env python3
"""Render scene configuration to GIF using Manim."""

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

        cmd = [
            sys.executable, "-m", "manim", "render",
            qflag,
            "--format", "gif",
            "--media_dir", tmpdir,
            str(template_path),
            scene_class,
        ]

        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)

        if result.returncode != 0:
            print(f"Manim stderr:\n{result.stderr}")
            raise RuntimeError(f"Manim rendering failed: {result.stderr}")

        gif_path = _find_output(tmpdir, ".gif")
        if not gif_path:
            mp4_path = _find_output(tmpdir, ".mp4")
            if mp4_path:
                gif_path = _convert_mp4_to_gif(mp4_path, output_path)
            else:
                raise RuntimeError("No output file found after rendering")

        shutil.copy2(gif_path, output_path)
        print(f"GIF saved to: {output_path}")
        return output_path


def _find_output(directory: str, ext: str) -> str | None:
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(ext):
                return os.path.join(root, f)
    return None


def _convert_mp4_to_gif(mp4_path: str, output_path: str) -> str:
    gif_path = output_path
    cmd = [
        "ffmpeg", "-y",
        "-i", mp4_path,
        "-vf", "fps=15,scale=800:-1:flags=lanczos",
        "-loop", "0",
        gif_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return gif_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python renderer.py <config.json> <output.gif> [quality]")
        sys.exit(1)

    config_path = sys.argv[1]
    output_path = sys.argv[2]
    quality = sys.argv[3] if len(sys.argv) > 3 else "low"

    with open(config_path) as f:
        config = json.load(f)

    render(config, output_path, quality)


if __name__ == "__main__":
    main()

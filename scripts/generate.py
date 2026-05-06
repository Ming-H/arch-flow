#!/usr/bin/env python3
"""Main entry point: orchestrates the full arch-flow pipeline.

Usage:
    python generate.py --input <input.json> --output <output.gif> [--quality low|medium|high|4k]
    python generate.py --json '{"nodes": [...], "edges": [...]}'
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from parser import parse
from renderer import render


def main():
    parser = argparse.ArgumentParser(description="arch-flow: Generate architecture animation GIFs")
    parser.add_argument("--input", "-i", help="Path to input JSON file")
    parser.add_argument("--output", "-o", help="Output GIF path (default: output/<title>.gif)")
    parser.add_argument("--quality", "-q", default="high", choices=["low", "medium", "high", "4k"])
    parser.add_argument("--json", dest="json_str", help="Inline JSON string")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    elif args.json_str:
        data = json.loads(args.json_str)
    else:
        parser.error("Either --input or --json is required")

    config = parse(data)

    if args.output:
        output_path = args.output
    else:
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        safe_title = config["title"].replace(" ", "_").lower()
        output_path = str(output_dir / f"{safe_title}.gif")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    render(config, output_path, args.quality)


if __name__ == "__main__":
    main()

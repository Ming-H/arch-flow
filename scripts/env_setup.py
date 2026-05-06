#!/usr/bin/env python3
"""Environment setup for arch-flow. Checks and installs dependencies."""

import shutil
import subprocess
import sys
import platform


def run(cmd, check=True):
    return subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)


def check_python():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"Python 3.10+ required, got {version.major}.{version.minor}")
        sys.exit(1)
    print(f"[OK] Python {version.major}.{version.minor}")


def check_ffmpeg():
    if shutil.which("ffmpeg"):
        result = run("ffmpeg -version")
        version = result.stdout.split("\n")[0]
        print(f"[OK] {version}")
    else:
        print("[MISSING] ffmpeg not found")
        if platform.system() == "Darwin":
            print("  Install: brew install ffmpeg")
        elif platform.system() == "Linux":
            print("  Install: sudo apt install ffmpeg")
        sys.exit(1)


def check_cairo():
    result = run("pkg-config --modversion cairo", check=False)
    if result.returncode == 0:
        print(f"[OK] cairo {result.stdout.strip()}")
    else:
        print("[MISSING] cairo not found")
        if platform.system() == "Darwin":
            print("  Installing via brew...")
            run("brew install cairo pkg-config")
            print("[OK] cairo installed")
        elif platform.system() == "Linux":
            print("  Install: sudo apt install libcairo2-dev pkg-config")
            sys.exit(1)


def install_python_deps():
    script_dir = Path(__file__).parent.parent
    req_file = script_dir / "requirements.txt"
    if req_file.exists():
        print(f"Installing from {req_file}...")
        run(f"{sys.executable} -m pip install -r {req_file}")
        print("[OK] Python dependencies installed")
    else:
        print(f"[WARN] {req_file} not found, installing manim directly...")
        run(f"{sys.executable} -m pip install manim Pillow")
        print("[OK] manim and Pillow installed")


def check_manim():
    result = run(f"{sys.executable} -c 'import manim; print(manim.__version__)'", check=False)
    if result.returncode == 0:
        print(f"[OK] manim {result.stdout.strip()}")
    else:
        print("[MISSING] manim not installed, installing...")
        install_python_deps()


if __name__ == "__main__":
    from pathlib import Path

    print("=== arch-flow Environment Setup ===\n")
    check_python()
    check_ffmpeg()
    check_cairo()
    check_manim()
    print("\n=== All dependencies ready ===")

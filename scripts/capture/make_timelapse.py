#!/usr/bin/env python3
"""Build per-feature timelapses from Docs/progress/<feature>/*.png with ffmpeg.
Usage: make_timelapse.py --all | --feature NAME | --master [--fps 6]
"""
import argparse, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path("Docs/progress")

def build(frames, out, fps):
    if not frames:
        return
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as t:
        for f in frames:
            t.write(f"file '{f.resolve()}'\nduration {1/fps}\n")
        lst = t.name
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                    "-r", "30", str(out)], check=True)
    print("wrote", out)

def feature_frames(d):
    return sorted(d.glob("*.png"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--feature")
    ap.add_argument("--master", action="store_true")
    ap.add_argument("--fps", type=float, default=6)
    a = ap.parse_args()
    if not ROOT.exists():
        sys.exit("no Docs/progress yet")
    dirs = [d for d in sorted(ROOT.iterdir()) if d.is_dir() and not d.name.startswith("_")]
    if a.feature:
        dirs = [ROOT / a.feature]
    if a.all or a.feature:
        for d in dirs:
            build(feature_frames(d), ROOT / "timelapses" / f"{d.name}.mp4", a.fps)
    if a.master:
        frames = sorted((f for d in dirs for f in d.glob("*.png")), key=lambda p: p.name.split("__")[0])
        build(frames, ROOT / "timelapses" / "_master.mp4", a.fps)

if __name__ == "__main__":
    main()

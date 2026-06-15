#!/usr/bin/env python3
"""Render captured UTF-8 text as a report-ready terminal screenshot."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/msyh.ttc"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--title", default="Real command output")
    args = parser.parse_args()

    raw = args.input.read_bytes()
    encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    text = raw.decode(encoding).rstrip()
    lines = [args.title, "", *text.splitlines()]
    font = load_font(22)
    line_height = 32
    padding = 36
    width = max(1200, max(len(line) for line in lines) * 14 + padding * 2)
    height = max(420, len(lines) * line_height + padding * 2)

    image = Image.new("RGB", (width, height), "#0c0c0c")
    draw = ImageDraw.Draw(image)
    y = padding
    for index, line in enumerate(lines):
        color = "#7ee787" if index == 0 else "#f0f0f0"
        draw.text((padding, y), line, font=font, fill=color)
        y += line_height

    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)


if __name__ == "__main__":
    main()

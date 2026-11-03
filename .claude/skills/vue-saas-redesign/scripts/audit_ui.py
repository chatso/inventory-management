#!/usr/bin/env python3
"""Audit a Vue 3 src directory before and after a UI redesign.

Usage: python audit_ui.py <src-dir>

Reports routes, hardcoded colors per file, layout values coupled to a top
header, z-index values, container max-widths, and emoji in templates.
"""
import re
import sys
from collections import Counter
from pathlib import Path

HEX = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
RGB = re.compile(r"\brgba?\(\s*\d")
STICKY_TOP = re.compile(r"top\s*:\s*(\d+(?:\.\d+)?(?:px|rem))")
HEADER_CALC = re.compile(r"calc\(\s*100d?vh\s*-\s*\d+(?:px|rem)\s*\)")
Z_INDEX = re.compile(r"z-index\s*:\s*(\d+)")
MAX_WIDTH = re.compile(r"max-width\s*:\s*(\d{3,4}px)")
ROUTE_PATH = re.compile(r"""path\s*:\s*['"]([^'"]+)['"]""")
# Emoji and pictographs (excludes plain arrows/bullets used in text).
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-⛿✀-➿]")


def style_blocks(text):
    return re.findall(r"<style[^>]*>(.*?)</style>", text, flags=re.S)


def template_block(text):
    match = re.search(r"<template>(.*)</template>", text, flags=re.S)
    return match.group(1) if match else ""


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1])
    if not root.is_dir():
        sys.exit(f"Not a directory: {root}")

    files = sorted(p for p in root.rglob("*") if p.suffix in {".vue", ".css", ".js"} and "node_modules" not in p.parts)

    print("== Routes ==")
    for path in files:
        if path.suffix == ".js":
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "createRouter" in text or "routes" in text:
                paths = ROUTE_PATH.findall(text)
                if paths:
                    print(f"{path.relative_to(root)}: {', '.join(paths)}")

    color_rows, coupling, zs, widths, emojis = [], [], [], [], []
    color_counter = Counter()

    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        rel = path.relative_to(root)
        css = "\n".join(style_blocks(text)) if path.suffix == ".vue" else (text if path.suffix == ".css" else "")

        if css:
            hexes = HEX.findall(css)
            rgbs = RGB.findall(css)
            if hexes or rgbs:
                color_rows.append((len(hexes) + len(rgbs), str(rel)))
                color_counter.update(h.lower() for h in hexes)
            for m in STICKY_TOP.finditer(css):
                block_start = css.rfind("{", 0, m.start())
                block = css[block_start:m.end() + 80]
                if "sticky" in block or "fixed" in block:
                    coupling.append(f"{rel}: sticky/fixed top: {m.group(1)}")
            for m in HEADER_CALC.finditer(css):
                coupling.append(f"{rel}: {m.group(0)}")
            for m in Z_INDEX.finditer(css):
                zs.append((int(m.group(1)), str(rel)))
            for m in MAX_WIDTH.finditer(css):
                widths.append(f"{rel}: max-width {m.group(1)}")

        if path.suffix == ".vue":
            tpl = template_block(text)
            for m in EMOJI.finditer(tpl):
                emojis.append(f"{rel}:{line_of(text, text.find(tpl) + m.start())} {m.group(0)}")

    print("\n== Hardcoded colors in styles (count, file) ==")
    for count, rel in sorted(color_rows, reverse=True):
        print(f"{count:4d}  {rel}")
    print("\n== Most common hex literals ==")
    print(", ".join(f"{h} x{n}" for h, n in color_counter.most_common(25)) or "none")

    print("\n== Offsets likely coupled to a top header ==")
    print("\n".join(coupling) or "none")

    print("\n== z-index values (value, file) ==")
    for value, rel in sorted(set(zs)):
        print(f"{value:5d}  {rel}")

    print("\n== Container max-widths ==")
    print("\n".join(widths) or "none")

    print("\n== Emoji in templates ==")
    print("\n".join(emojis) or "none")


if __name__ == "__main__":
    main()

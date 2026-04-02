"""Visual board renderer using Pillow — generates a top-down PNG of the board layout."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

from .board_designer import BoardDesign

# ---------------------------------------------------------------------------
# Colour palette for terrain categories
# ---------------------------------------------------------------------------

TERRAIN_COLOURS = {
    "mountain": (139, 137, 137),      # grey
    "hill": (144, 190, 109),           # light green
    "dry_riverbed": (194, 178, 128),   # sandy tan
    "river": (100, 149, 237),          # cornflower blue
    "forest": (34, 120, 58),           # dark green
    "ruins": (160, 160, 160),          # light grey
    "crater": (90, 70, 55),            # dark brown
    "rocky_outcrops": (169, 169, 169), # dark grey
    "desert_dunes": (237, 217, 160),   # pale sand
    "bridge": (139, 90, 43),           # wood brown
}

BASE_COLOURS = {
    "green": (89, 130, 72),
    "brown": (121, 85, 61),
    "sand": (210, 190, 140),
    "grey": (140, 140, 140),
    "black": (50, 50, 50),
}

PIXELS_PER_INCH = 12  # rendering resolution


def render_board_image(
    design: BoardDesign,
    output_path: str | Path = "board_layout.png",
    ppi: int = PIXELS_PER_INCH,
) -> Optional[Path]:
    """Render the board design to a PNG image. Returns the path, or None if PIL is unavailable."""
    if not HAS_PIL:
        return None

    w_px = design.width * ppi
    h_px = design.height * ppi
    output_path = Path(output_path)

    # Determine base colour
    bc = design.base_colour.lower()
    bg = BASE_COLOURS.get("brown")  # default
    for key, colour in BASE_COLOURS.items():
        if key in bc:
            bg = colour
            break

    img = Image.new("RGB", (w_px, h_px), bg)
    draw = ImageDraw.Draw(img)

    # Draw grid (every 6 inches = one-foot squares)
    grid_step = 6 * ppi
    grid_colour = tuple(max(0, c - 20) for c in bg)
    for x in range(0, w_px, grid_step):
        draw.line([(x, 0), (x, h_px)], fill=grid_colour, width=1)
    for y in range(0, h_px, grid_step):
        draw.line([(0, y), (w_px, y)], fill=grid_colour, width=1)

    # Draw terrain placements
    for idx, p in enumerate(design.placements):
        colour = TERRAIN_COLOURS.get(p.feature_key, (180, 180, 180))
        x1 = int(p.x * ppi)
        y1 = int(p.y * ppi)
        x2 = int((p.x + p.width) * ppi)
        y2 = int((p.y + p.height) * ppi)

        # Fill with slight transparency effect (darker border)
        draw.rectangle([x1, y1, x2, y2], fill=colour, outline=(0, 0, 0), width=2)

        # Label
        label = p.label or p.feature.name
        short = label[:18]
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", max(10, ppi))
        except (OSError, IOError):
            font = ImageFont.load_default()

        # Centre text in the rectangle
        bbox = draw.textbbox((0, 0), short, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = x1 + (x2 - x1 - tw) // 2
        ty = y1 + (y2 - y1 - th) // 2
        # Text shadow for readability
        draw.text((tx + 1, ty + 1), short, fill=(0, 0, 0), font=font)
        draw.text((tx, ty), short, fill=(255, 255, 255), font=font)

    # Board border
    draw.rectangle([0, 0, w_px - 1, h_px - 1], outline=(255, 255, 255), width=3)

    # Title bar
    draw.rectangle([0, 0, w_px, 20], fill=(30, 30, 30))
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except (OSError, IOError):
        title_font = ImageFont.load_default()
    draw.text((8, 3), f"{design.name}  ({design.width}×{design.height}″)", fill=(255, 255, 255), font=title_font)

    img.save(output_path)
    return output_path

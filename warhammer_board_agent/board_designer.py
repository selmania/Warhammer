"""Board designer — manages the 60×44″ board layout and terrain placement."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .terrain import (
    BOARD_THEMES,
    MATERIALS,
    TERRAIN_FEATURES,
    TerrainFeature,
    Material,
    get_all_feature_names,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BOARD_WIDTH = 60  # inches
BOARD_HEIGHT = 44  # inches
GRID_CELL = 1  # 1-inch grid resolution


# ---------------------------------------------------------------------------
# Placement model
# ---------------------------------------------------------------------------

@dataclass
class PlacedTerrain:
    """A terrain feature placed at a specific position on the board."""
    feature_key: str
    x: float  # left edge, inches from board left
    y: float  # top edge, inches from board top
    width: float  # footprint width in inches
    height: float  # footprint depth in inches
    label: str = ""
    rotation: float = 0.0  # degrees

    @property
    def feature(self) -> TerrainFeature:
        return TERRAIN_FEATURES[self.feature_key]

    @property
    def centre(self) -> tuple[float, float]:
        return (self.x + self.width / 2, self.y + self.height / 2)

    def overlaps(self, other: PlacedTerrain, margin: float = 0.5) -> bool:
        """Check if this placement overlaps another (with optional margin)."""
        return not (
            self.x + self.width + margin <= other.x
            or other.x + other.width + margin <= self.x
            or self.y + self.height + margin <= other.y
            or other.y + other.height + margin <= self.y
        )

    def in_bounds(self) -> bool:
        return (
            self.x >= 0
            and self.y >= 0
            and self.x + self.width <= BOARD_WIDTH
            and self.y + self.height <= BOARD_HEIGHT
        )

    def to_dict(self) -> dict:
        return {
            "feature_key": self.feature_key,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "label": self.label,
            "rotation": self.rotation,
        }

    @classmethod
    def from_dict(cls, d: dict) -> PlacedTerrain:
        return cls(**d)


# ---------------------------------------------------------------------------
# Board design
# ---------------------------------------------------------------------------

@dataclass
class BoardDesign:
    """Full board design state."""
    name: str = "My Warhammer Board"
    theme: str = "custom"
    base_colour: str = "Earth brown"
    width: int = BOARD_WIDTH
    height: int = BOARD_HEIGHT
    placements: list[PlacedTerrain] = field(default_factory=list)
    notes: str = ""

    # -- Placement helpers ------------------------------------------------

    def add_terrain(
        self,
        feature_key: str,
        x: float,
        y: float,
        width: Optional[float] = None,
        height: Optional[float] = None,
        label: str = "",
    ) -> PlacedTerrain:
        """Add a terrain feature to the board. Returns the placement or raises ValueError."""
        if feature_key not in TERRAIN_FEATURES:
            raise ValueError(f"Unknown terrain feature: {feature_key}")
        feat = TERRAIN_FEATURES[feature_key]
        w = width or feat.footprint_inches[0]
        h = height or feat.footprint_inches[1]
        placement = PlacedTerrain(
            feature_key=feature_key,
            x=x, y=y,
            width=w, height=h,
            label=label or feat.name,
        )
        if not placement.in_bounds():
            raise ValueError(
                f"Placement at ({x}, {y}) with size {w}×{h}″ "
                f"extends outside the {self.width}×{self.height}″ board."
            )
        conflicts = [p for p in self.placements if p.overlaps(placement)]
        if conflicts:
            names = ", ".join(p.label for p in conflicts)
            raise ValueError(f"Overlaps with existing terrain: {names}")
        self.placements.append(placement)
        return placement

    def remove_terrain(self, index: int) -> PlacedTerrain:
        """Remove a terrain placement by index."""
        if 0 <= index < len(self.placements):
            return self.placements.pop(index)
        raise IndexError(f"Invalid terrain index: {index}")

    def move_terrain(self, index: int, new_x: float, new_y: float) -> PlacedTerrain:
        """Move an existing placement to a new position."""
        if not (0 <= index < len(self.placements)):
            raise IndexError(f"Invalid terrain index: {index}")
        p = self.placements[index]
        old_x, old_y = p.x, p.y
        p.x, p.y = new_x, new_y
        if not p.in_bounds():
            p.x, p.y = old_x, old_y
            raise ValueError("New position is out of bounds.")
        for i, other in enumerate(self.placements):
            if i != index and p.overlaps(other):
                p.x, p.y = old_x, old_y
                raise ValueError(f"New position overlaps with: {other.label}")
        return p

    # -- Auto-layout -----------------------------------------------------

    def auto_layout(self, feature_keys: list[str]) -> list[PlacedTerrain]:
        """Automatically place a list of features on the board with sensible spacing.

        Uses a simple grid-packing strategy distributing features evenly.
        """
        n = len(feature_keys)
        if n == 0:
            return []

        cols = math.ceil(math.sqrt(n * (self.width / self.height)))
        rows = math.ceil(n / cols)
        cell_w = self.width / cols
        cell_h = self.height / rows

        placed: list[PlacedTerrain] = []
        for idx, key in enumerate(feature_keys):
            row, col = divmod(idx, cols)
            feat = TERRAIN_FEATURES.get(key)
            if not feat:
                continue
            fw, fh = feat.footprint_inches
            # Centre within the cell
            cx = col * cell_w + (cell_w - fw) / 2
            cy = row * cell_h + (cell_h - fh) / 2
            # Clamp
            cx = max(0, min(cx, self.width - fw))
            cy = max(0, min(cy, self.height - fh))
            try:
                p = self.add_terrain(key, round(cx, 1), round(cy, 1), label=f"{feat.name} #{idx+1}")
                placed.append(p)
            except ValueError:
                # Overlap — nudge slightly
                for offset in [2, 4, 6, 8]:
                    try:
                        p = self.add_terrain(
                            key,
                            round(cx + offset, 1),
                            round(cy + offset, 1),
                            label=f"{feat.name} #{idx+1}",
                        )
                        placed.append(p)
                        break
                    except ValueError:
                        continue
        return placed

    # -- Board coverage analysis -----------------------------------------

    def coverage_percent(self) -> float:
        """Approximate percentage of the board covered by terrain."""
        terrain_area = sum(p.width * p.height for p in self.placements)
        return (terrain_area / (self.width * self.height)) * 100

    def terrain_density_assessment(self) -> str:
        """Return a qualitative assessment of terrain density for balanced play."""
        pct = self.coverage_percent()
        if pct < 15:
            return "Sparse — shooting armies will dominate. Consider adding more terrain."
        elif pct < 25:
            return "Light — provides some cover but favours ranged play."
        elif pct < 35:
            return "Balanced — good mix of open lanes and cover."
        elif pct < 50:
            return "Dense — melee armies benefit. Strong line-of-sight blocking."
        else:
            return "Very dense — may limit movement. Check for playability."

    # -- Material aggregation --------------------------------------------

    def get_all_materials(self) -> dict[str, Material]:
        """Collect all unique materials needed for the current design."""
        mats: dict[str, Material] = {}
        for p in self.placements:
            for m in p.feature.recommended_materials:
                mats[m.name] = m
        return mats

    def get_material_summary(self) -> list[dict]:
        """Return a list of material dicts for the shopping list builder."""
        mats = self.get_all_materials()
        return [
            {"name": m.name, "search_keywords": m.search_keywords, "price_range": m.typical_price_range}
            for m in mats.values()
        ]

    # -- Serialization ---------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "theme": self.theme,
            "base_colour": self.base_colour,
            "width": self.width,
            "height": self.height,
            "placements": [p.to_dict() for p in self.placements],
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: dict) -> BoardDesign:
        placements = [PlacedTerrain.from_dict(p) for p in d.get("placements", [])]
        return cls(
            name=d.get("name", "Board"),
            theme=d.get("theme", "custom"),
            base_colour=d.get("base_colour", ""),
            width=d.get("width", BOARD_WIDTH),
            height=d.get("height", BOARD_HEIGHT),
            placements=placements,
            notes=d.get("notes", ""),
        )

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> BoardDesign:
        data = json.loads(Path(path).read_text())
        return cls.from_dict(data)

    # -- ASCII board map -------------------------------------------------

    def render_ascii(self, scale: float = 0.5) -> str:
        """Render a simple ASCII top-down view of the board.

        scale: characters per inch (0.5 = one char per 2 inches).
        """
        cols = int(self.width * scale)
        rows = int(self.height * scale)
        grid = [["·" for _ in range(cols)] for _ in range(rows)]

        symbols = {
            "mountain": "▲",
            "hill": "∩",
            "dry_riverbed": "~",
            "river": "≈",
            "forest": "♣",
            "ruins": "▦",
            "crater": "◎",
            "rocky_outcrops": "●",
            "desert_dunes": "∿",
            "bridge": "═",
        }

        for idx, p in enumerate(self.placements):
            sym = symbols.get(p.feature_key, "■")
            # Map to grid coordinates
            gx1 = int(p.x * scale)
            gy1 = int(p.y * scale)
            gx2 = min(int((p.x + p.width) * scale), cols)
            gy2 = min(int((p.y + p.height) * scale), rows)
            for gy in range(max(0, gy1), gy2):
                for gx in range(max(0, gx1), gx2):
                    grid[gy][gx] = sym

        # Draw border
        border_h = "─" * (cols + 2)
        lines = [f"  ┌{border_h}┐  {self.name} ({self.width}×{self.height}″)"]
        for r, row in enumerate(grid):
            y_label = f"{int(r / scale):>2}"
            lines.append(f"{y_label}│ {''.join(row)} │")
        lines.append(f"  └{border_h}┘")

        # Legend
        if self.placements:
            lines.append("")
            lines.append("  Legend:")
            seen = set()
            for p in self.placements:
                sym = symbols.get(p.feature_key, "■")
                if p.feature_key not in seen:
                    seen.add(p.feature_key)
                    lines.append(f"    {sym} = {p.feature.name}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Quick-start helpers
# ---------------------------------------------------------------------------

def create_themed_board(theme_key: str, board_name: str = "") -> BoardDesign:
    """Create a new board design from a preset theme with auto-layout."""
    theme = BOARD_THEMES.get(theme_key)
    if not theme:
        raise ValueError(f"Unknown theme: {theme_key}. Options: {', '.join(BOARD_THEMES.keys())}")

    design = BoardDesign(
        name=board_name or theme["name"],
        theme=theme_key,
        base_colour=theme["base_colour"],
    )

    if theme["suggested_features"]:
        design.auto_layout(theme["suggested_features"])

    return design

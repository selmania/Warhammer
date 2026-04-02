"""Terrain knowledge base — types, materials, and construction guidance."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TerrainCategory(str, Enum):
    ELEVATION = "elevation"
    WATER = "water"
    VEGETATION = "vegetation"
    STRUCTURE = "structure"
    SURFACE = "surface"
    SCATTER = "scatter"


@dataclass
class Material:
    name: str
    description: str
    typical_price_range: str  # e.g. "$5-$15"
    search_keywords: list[str] = field(default_factory=list)


@dataclass
class TerrainFeature:
    name: str
    category: TerrainCategory
    description: str
    construction_tips: list[str]
    recommended_materials: list[Material]
    footprint_inches: tuple[float, float]  # width, depth default suggestion
    min_height_inches: float = 0.0
    max_height_inches: float = 0.0
    rules_impact: str = ""  # how it affects gameplay


# ---------------------------------------------------------------------------
# Pre-built knowledge base
# ---------------------------------------------------------------------------

MATERIALS = {
    "xps_foam": Material(
        name="XPS Insulation Foam (2″ sheets)",
        description="Extruded polystyrene — the workhorse of terrain building. Easy to cut, shape, and texture.",
        typical_price_range="$15-$30 per 4×8′ sheet",
        search_keywords=["XPS foam board insulation 2 inch", "extruded polystyrene foam crafting"],
    ),
    "plaster_cloth": Material(
        name="Plaster Cloth / Mod-Roc",
        description="Plaster-impregnated gauze for creating hard shells over foam armatures.",
        typical_price_range="$8-$18 per roll",
        search_keywords=["plaster cloth terrain", "mod roc plaster bandage"],
    ),
    "sculptamold": Material(
        name="Sculptamold",
        description="Lightweight modeling compound — great for rock faces and organic shapes.",
        typical_price_range="$10-$20 per 3 lb bag",
        search_keywords=["Sculptamold modeling compound", "lightweight terrain sculpting material"],
    ),
    "pva_glue": Material(
        name="PVA / White Glue",
        description="Essential adhesive for terrain building — bonds foam, flock, sand, and more.",
        typical_price_range="$5-$12 per bottle",
        search_keywords=["PVA glue crafting", "white glue terrain building"],
    ),
    "static_grass": Material(
        name="Static Grass",
        description="Short synthetic fibres applied with a static applicator for realistic grass.",
        typical_price_range="$8-$20 per bag",
        search_keywords=["static grass warhammer", "model railway static grass 6mm"],
    ),
    "flock_turf": Material(
        name="Flock / Scatter Turf",
        description="Fine ground foam for representing grass, foliage, and ground cover.",
        typical_price_range="$5-$15 per bag",
        search_keywords=["scatter flock terrain", "Woodland Scenics turf"],
    ),
    "sand_gravel": Material(
        name="Hobby Sand & Fine Gravel",
        description="For basing, dry riverbeds, and desert textures.",
        typical_price_range="$4-$10 per bag",
        search_keywords=["hobby sand terrain basing", "fine ballast model scenery"],
    ),
    "texture_paint": Material(
        name="Texture Paints (e.g. Citadel, Vallejo)",
        description="Thick paints that add gritty texture — fast way to base terrain.",
        typical_price_range="$6-$12 per pot",
        search_keywords=["Citadel texture paint", "Vallejo earth texture", "terrain texture paint"],
    ),
    "acrylic_paint": Material(
        name="Craft Acrylic Paints",
        description="Cheap, large-volume acrylics for base-coating terrain.",
        typical_price_range="$2-$8 per bottle",
        search_keywords=["craft acrylic paint terrain", "Apple Barrel acrylic brown"],
    ),
    "hot_wire_cutter": Material(
        name="Hot Wire Foam Cutter",
        description="Heated wire tool for cleanly shaping XPS foam into cliffs and slopes.",
        typical_price_range="$20-$60",
        search_keywords=["hot wire foam cutter", "styrofoam cutter tool"],
    ),
    "cork_bark": Material(
        name="Cork Bark / Cork Sheet",
        description="Natural cork for realistic rock faces and cliff edges.",
        typical_price_range="$8-$20",
        search_keywords=["cork bark terrain", "cork sheet crafting rocks"],
    ),
    "mdf_board": Material(
        name="MDF Board (3 mm – 6 mm)",
        description="Medium-density fibreboard for the board base. Stable and paintable.",
        typical_price_range="$10-$30 per 4×2′ panel",
        search_keywords=["MDF board 3mm", "MDF sheet craft hobby"],
    ),
    "resin_water": Material(
        name="Resin Water Effects",
        description="Two-part resin or acrylic water effects for pools, rivers, and lakes.",
        typical_price_range="$10-$25",
        search_keywords=["Woodland Scenics water effects", "resin water terrain miniature"],
    ),
    "milliput": Material(
        name="Milliput / Green Stuff Epoxy",
        description="Two-part epoxy putty for sculpting fine details.",
        typical_price_range="$8-$15",
        search_keywords=["Milliput epoxy putty", "green stuff sculpting warhammer"],
    ),
    "tree_armatures": Material(
        name="Tree Armatures & Foliage",
        description="Plastic or wire armatures plus clump foliage for trees.",
        typical_price_range="$10-$25 per set",
        search_keywords=["model tree armatures wargaming", "Woodland Scenics trees"],
    ),
    "mdf_ruins": Material(
        name="MDF Laser-Cut Ruins",
        description="Pre-cut MDF building ruins — assemble and paint.",
        typical_price_range="$15-$45 per kit",
        search_keywords=["MDF terrain ruins warhammer", "laser cut 28mm ruins"],
    ),
}


TERRAIN_FEATURES: dict[str, TerrainFeature] = {
    "mountain": TerrainFeature(
        name="Mountain / Rocky Outcrop",
        category=TerrainCategory.ELEVATION,
        description="A tall, rugged elevation piece representing mountains or large rock formations. Blocks line of sight and creates dramatic board centrepieces.",
        construction_tips=[
            "Stack and carve XPS foam layers to build up height — stagger the layers for a natural look.",
            "Use a hot-wire cutter to shape cliff faces; score horizontal lines for sedimentary rock texture.",
            "Cover with Sculptamold or plaster cloth for a hard, paintable shell.",
            "Drybrush with successive lighter greys from a dark base for convincing stone.",
            "Add cork bark fragments for exposed rock faces.",
        ],
        recommended_materials=[
            MATERIALS["xps_foam"],
            MATERIALS["hot_wire_cutter"],
            MATERIALS["sculptamold"],
            MATERIALS["plaster_cloth"],
            MATERIALS["cork_bark"],
            MATERIALS["acrylic_paint"],
        ],
        footprint_inches=(10, 8),
        min_height_inches=4,
        max_height_inches=8,
        rules_impact="Blocks line of sight. Counts as impassable or difficult terrain depending on slope.",
    ),
    "hill": TerrainFeature(
        name="Gentle Hill",
        category=TerrainCategory.ELEVATION,
        description="A low, rounded hill that provides elevated positions without fully blocking sight lines.",
        construction_tips=[
            "Cut an oval from 1-2″ XPS foam; bevel the edges at ~45° with a craft knife.",
            "Sand or rasp the edges to create a smooth slope.",
            "Coat with PVA + sand for ground texture, then paint and flock.",
        ],
        recommended_materials=[
            MATERIALS["xps_foam"],
            MATERIALS["pva_glue"],
            MATERIALS["sand_gravel"],
            MATERIALS["static_grass"],
            MATERIALS["acrylic_paint"],
        ],
        footprint_inches=(8, 6),
        min_height_inches=1,
        max_height_inches=3,
        rules_impact="Provides elevation advantage (+1 to hit in some rulesets). Not impassable.",
    ),
    "dry_riverbed": TerrainFeature(
        name="Dry Riverbed / Wadi",
        category=TerrainCategory.WATER,
        description="A winding dried-up river channel cut into the board surface. Provides natural cover and channels movement.",
        construction_tips=[
            "Route a shallow channel (½-1″ deep) through XPS foam board tiles.",
            "Line the channel with fine sand and small pebbles glued with PVA.",
            "Paint a dark brown base, drybrush with light tan and bone colours.",
            "Add occasional larger rocks (cork or real pebbles) along the banks.",
            "Scatter dead grass tufts along the edges for a parched look.",
        ],
        recommended_materials=[
            MATERIALS["xps_foam"],
            MATERIALS["sand_gravel"],
            MATERIALS["pva_glue"],
            MATERIALS["acrylic_paint"],
            MATERIALS["flock_turf"],
        ],
        footprint_inches=(20, 4),
        min_height_inches=0,
        max_height_inches=0,
        rules_impact="Provides soft cover. Counts as difficult terrain for vehicles.",
    ),
    "river": TerrainFeature(
        name="Flowing River",
        category=TerrainCategory.WATER,
        description="A river section with simulated water — can be fordable or impassable.",
        construction_tips=[
            "Cut a channel in the board and seal with PVA.",
            "Paint the riverbed in dark blue-green graduating to lighter edges.",
            "Pour acrylic water effects or two-part resin in thin layers.",
            "Add ripple effects while resin is tacky using a toothpick.",
        ],
        recommended_materials=[
            MATERIALS["xps_foam"],
            MATERIALS["resin_water"],
            MATERIALS["acrylic_paint"],
            MATERIALS["pva_glue"],
        ],
        footprint_inches=(20, 4),
        min_height_inches=0,
        max_height_inches=0,
        rules_impact="Fordable: difficult terrain. Deep: impassable except at bridges/fords.",
    ),
    "forest": TerrainFeature(
        name="Forest / Woodland",
        category=TerrainCategory.VEGETATION,
        description="A cluster of trees on a defined base, providing cover and blocking sight.",
        construction_tips=[
            "Create a shaped MDF or foamcore base with textured edges.",
            "Use removable tree armatures so models can move through the footprint.",
            "Texture the base with sand, flock, and fallen-leaf scatter.",
            "3-6 trees per forest base is a good density for 28mm scale.",
        ],
        recommended_materials=[
            MATERIALS["tree_armatures"],
            MATERIALS["mdf_board"],
            MATERIALS["flock_turf"],
            MATERIALS["static_grass"],
            MATERIALS["pva_glue"],
        ],
        footprint_inches=(8, 8),
        min_height_inches=3,
        max_height_inches=6,
        rules_impact="Provides heavy cover. Blocks line of sight to/through. Infantry move at half speed.",
    ),
    "ruins": TerrainFeature(
        name="Ruined Building",
        category=TerrainCategory.STRUCTURE,
        description="The remains of a stone or Imperial structure — provides cover and elevated positions.",
        construction_tips=[
            "Use MDF laser-cut kits for fast assembly, or scratch-build from XPS foam.",
            "Score foam to simulate individual stone blocks.",
            "Add rubble from offcuts and small stones around the base.",
            "Paint grey stone, wash with brown/black, drybrush highlights.",
        ],
        recommended_materials=[
            MATERIALS["mdf_ruins"],
            MATERIALS["xps_foam"],
            MATERIALS["pva_glue"],
            MATERIALS["acrylic_paint"],
            MATERIALS["milliput"],
        ],
        footprint_inches=(6, 6),
        min_height_inches=2,
        max_height_inches=6,
        rules_impact="Provides hard cover. Upper floors give elevation. Can be garrisoned.",
    ),
    "crater": TerrainFeature(
        name="Impact Crater",
        category=TerrainCategory.SURFACE,
        description="A blast crater — quick to build and great scatter terrain.",
        construction_tips=[
            "Press a ball shape into XPS foam to create the depression.",
            "Build up a raised rim with Sculptamold or more foam.",
            "Texture with sand and paint dark centre fading to scorched earth at edges.",
        ],
        recommended_materials=[
            MATERIALS["xps_foam"],
            MATERIALS["sculptamold"],
            MATERIALS["sand_gravel"],
            MATERIALS["acrylic_paint"],
        ],
        footprint_inches=(5, 5),
        min_height_inches=0,
        max_height_inches=1,
        rules_impact="Provides soft cover to models within. No movement penalty.",
    ),
    "rocky_outcrops": TerrainFeature(
        name="Scattered Rock Outcrops",
        category=TerrainCategory.SCATTER,
        description="Clusters of rocks providing light cover and visual interest.",
        construction_tips=[
            "Break up cork bark or carve small XPS chunks.",
            "Glue clusters onto small bases.",
            "Paint and drybrush with grey tones; add lichen or moss flock.",
        ],
        recommended_materials=[
            MATERIALS["cork_bark"],
            MATERIALS["pva_glue"],
            MATERIALS["acrylic_paint"],
            MATERIALS["flock_turf"],
        ],
        footprint_inches=(4, 3),
        min_height_inches=1,
        max_height_inches=3,
        rules_impact="Provides light cover. Does not block line of sight.",
    ),
    "desert_dunes": TerrainFeature(
        name="Sand Dunes",
        category=TerrainCategory.SURFACE,
        description="Rolling dunes for desert-themed boards.",
        construction_tips=[
            "Shape smooth mounds from XPS foam; round all edges.",
            "Coat with PVA and fine sand.",
            "Paint with warm tans and yellows; drybrush with pale cream.",
        ],
        recommended_materials=[
            MATERIALS["xps_foam"],
            MATERIALS["pva_glue"],
            MATERIALS["sand_gravel"],
            MATERIALS["acrylic_paint"],
        ],
        footprint_inches=(8, 6),
        min_height_inches=1,
        max_height_inches=3,
        rules_impact="Difficult terrain for vehicles. No cover bonus.",
    ),
    "bridge": TerrainFeature(
        name="Bridge / Crossing",
        category=TerrainCategory.STRUCTURE,
        description="A bridge spanning a river or ravine — a key tactical chokepoint.",
        construction_tips=[
            "Build from foamcore or balsa wood; MDF kits also available.",
            "Ensure it spans your river/ravine terrain piece exactly.",
            "Texture with stonework scoring or plank lines for wood.",
        ],
        recommended_materials=[
            MATERIALS["mdf_board"],
            MATERIALS["xps_foam"],
            MATERIALS["acrylic_paint"],
            MATERIALS["pva_glue"],
        ],
        footprint_inches=(6, 3),
        min_height_inches=1,
        max_height_inches=2,
        rules_impact="Open ground — no movement penalty. Chokepoint for tactical play.",
    ),
}


# ---------------------------------------------------------------------------
# Board themes (pre-set combinations)
# ---------------------------------------------------------------------------

BOARD_THEMES = {
    "arid_wasteland": {
        "name": "Arid Wasteland",
        "description": "A sun-scorched desert with dry riverbeds, rocky outcrops, and scattered ruins.",
        "base_colour": "Khaki / sandy tan",
        "suggested_features": ["mountain", "dry_riverbed", "rocky_outcrops", "ruins", "crater", "desert_dunes"],
    },
    "verdant_highlands": {
        "name": "Verdant Highlands",
        "description": "Rolling green hills with forests, rivers, and the occasional ruin.",
        "base_colour": "Rich green / dark earth",
        "suggested_features": ["hill", "forest", "river", "bridge", "ruins", "rocky_outcrops"],
    },
    "war_torn_city": {
        "name": "War-Torn Cityscape",
        "description": "Shattered urban sprawl — craters, ruins, and rubble everywhere.",
        "base_colour": "Grey concrete / asphalt",
        "suggested_features": ["ruins", "ruins", "crater", "crater", "rocky_outcrops", "hill"],
    },
    "volcanic_hellscape": {
        "name": "Volcanic Hellscape",
        "description": "Black basalt, lava rivers, and jagged mountains under dark skies.",
        "base_colour": "Black / dark charcoal",
        "suggested_features": ["mountain", "mountain", "river", "crater", "rocky_outcrops", "desert_dunes"],
    },
    "custom": {
        "name": "Custom Board",
        "description": "Start from scratch — pick your own features, theme, and colours.",
        "base_colour": "Your choice",
        "suggested_features": [],
    },
}


def get_all_feature_names() -> list[str]:
    return list(TERRAIN_FEATURES.keys())


def get_all_material_names() -> list[str]:
    return list(MATERIALS.keys())


def describe_feature(key: str) -> str:
    f = TERRAIN_FEATURES.get(key)
    if not f:
        return f"Unknown terrain feature: {key}"
    mats = ", ".join(m.name for m in f.recommended_materials)
    return (
        f"▸ {f.name} ({f.category.value})\n"
        f"  {f.description}\n"
        f"  Footprint: ~{f.footprint_inches[0]}″×{f.footprint_inches[1]}″  "
        f"Height: {f.min_height_inches}–{f.max_height_inches}″\n"
        f"  Rules: {f.rules_impact}\n"
        f"  Materials: {mats}\n"
    )

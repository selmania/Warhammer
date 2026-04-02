"""DIY & household alternatives knowledge base for terrain building.

Maps commercial terrain materials to cheap/free alternatives that can be
found around the house, in recycling bins, or scavenged from everyday items.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DIYAlternative:
    """A household or scavenged substitute for a commercial material."""
    name: str
    replaces: str  # what commercial material it substitutes
    source: str  # where to find it
    cost: str  # e.g. "Free", "$1-2"
    description: str
    tips: list[str] = field(default_factory=list)
    difficulty: str = "Easy"  # Easy / Medium / Advanced


# ---------------------------------------------------------------------------
# The knowledge base — organised by what they replace
# ---------------------------------------------------------------------------

DIY_ALTERNATIVES: list[DIYAlternative] = [
    # ── XPS Foam replacements ──────────────────────────────────────────
    DIYAlternative(
        name="Packing Styrofoam (EPS)",
        replaces="XPS Insulation Foam",
        source="Appliance boxes, electronics packaging, skip bins",
        cost="Free",
        description="Expanded polystyrene from packaging. Rougher than XPS but free and plentiful. Great for bulky terrain cores.",
        tips=[
            "Seal with PVA or mod podge before painting — spray paint melts EPS.",
            "Use a sharp bread knife or dental floss to cut — don't use a hot wire on EPS (toxic fumes).",
            "Stack and glue layers with PVA for large mountains.",
            "The rough texture actually looks great for rock faces with minimal effort.",
        ],
        difficulty="Easy",
    ),
    DIYAlternative(
        name="Cardboard Layering",
        replaces="XPS Insulation Foam",
        source="Amazon boxes, cereal boxes, any corrugated cardboard",
        cost="Free",
        description="Stack and glue corrugated cardboard layers to build up elevation. Surprisingly sturdy when sealed.",
        tips=[
            "Cut progressively smaller layers for natural hill/mountain contours.",
            "Coat finished piece in PVA + tissue paper to smooth the stepped edges.",
            "Use a mix of corrugated (thick) and cereal box (thin) for varied contours.",
            "Seal well — cardboard warps if it gets damp during painting.",
        ],
        difficulty="Easy",
    ),
    DIYAlternative(
        name="Expanding Foam (Great Stuff)",
        replaces="XPS Insulation Foam",
        source="Hardware store — ~$5 per can",
        cost="$4-8",
        description="Spray expanding foam for organic rock and cave shapes. Expands to fill any form.",
        tips=[
            "Spray into a plastic bag or mould — it sticks to everything else.",
            "Let cure 24 hours, then carve with a craft knife.",
            "Creates fantastic organic, craggy rock textures naturally.",
            "Wear gloves — this stuff does NOT come off skin easily.",
        ],
        difficulty="Medium",
    ),

    # ── Plaster / Sculptamold replacements ─────────────────────────────
    DIYAlternative(
        name="Paper Mâché (Newspaper + Flour Paste)",
        replaces="Plaster Cloth / Sculptamold",
        source="Old newspapers + flour + water from the kitchen",
        cost="Free",
        description="The classic: torn newspaper strips soaked in flour-water paste. Creates a hard shell over any armature.",
        tips=[
            "Mix 1 part flour to 2 parts water. Add a pinch of salt to prevent mould.",
            "Apply 3-4 layers, letting each dry before the next for maximum strength.",
            "Tear strips (don't cut) for smoother, less visible seams.",
            "Finish with a layer of tissue paper for a smoother painting surface.",
        ],
        difficulty="Easy",
    ),
    DIYAlternative(
        name="Toilet Paper + PVA Pulp",
        replaces="Sculptamold",
        source="Toilet paper + PVA glue from home",
        cost="Free–$2",
        description="Shred toilet paper into PVA glue to make a sculptable pulp. Dries hard and lightweight.",
        tips=[
            "Soak TP in water, squeeze out excess, then mix with PVA until clay-like.",
            "Add a spoon of joint compound or plaster for faster drying if available.",
            "Sculpt rock faces, build up texture — works just like Sculptamold.",
            "Dries in 24-48 hours depending on thickness.",
        ],
        difficulty="Easy",
    ),
    DIYAlternative(
        name="Joint Compound / Spackle",
        replaces="Sculptamold",
        source="Hardware store or leftover from home repairs",
        cost="$3-8 per tub",
        description="Drywall joint compound is cheap, widely available, and great for terrain texture and smoothing.",
        tips=[
            "Apply thin layers — thick applications crack as they dry.",
            "Mix with PVA for a tougher, more flexible finish.",
            "Stipple with a sponge for rock texture, smooth with wet fingers for earth.",
            "A large tub will last dozens of terrain projects.",
        ],
        difficulty="Easy",
    ),

    # ── Sand & gravel replacements ─────────────────────────────────────
    DIYAlternative(
        name="Cat Litter (Non-Clumping)",
        replaces="Hobby Sand & Fine Gravel",
        source="Pet shop or supermarket — cheapest brand",
        cost="$2-4 per bag",
        description="Non-clumping clay cat litter is perfect for rubble, gravel, and rocky ground texture.",
        tips=[
            "Crush with a rolling pin for varied grain sizes.",
            "Sort through a kitchen sieve for fine/medium/coarse grades.",
            "Glue down with PVA, then seal with watered-down PVA before painting.",
            "MUST be non-clumping — clumping litter swells and disintegrates with paint/glue.",
        ],
        difficulty="Easy",
    ),
    DIYAlternative(
        name="Playground Sand / Garden Sand",
        replaces="Hobby Sand & Fine Gravel",
        source="Garden centre, playground, beach",
        cost="Free–$3",
        description="Regular sand works perfectly for terrain basing. Sieve it for consistent grain size.",
        tips=[
            "Bake in the oven at 200°F/100°C for 30 min to sterilise if collected outdoors.",
            "Run through a tea strainer for ultra-fine sand (perfect for desert boards).",
            "Mix fine and coarse grades for more natural-looking ground.",
        ],
        difficulty="Easy",
    ),
    DIYAlternative(
        name="Crushed Eggshells",
        replaces="Hobby Sand & Fine Gravel",
        source="Kitchen — save from cooking",
        cost="Free",
        description="Dried, crushed eggshells make excellent rocky rubble and slate-like debris.",
        tips=[
            "Wash, dry thoroughly, then crush to desired size.",
            "Larger pieces look like broken flagstones; fine crush looks like gravel.",
            "Glue flat side down for a natural stone slab effect.",
        ],
        difficulty="Easy",
    ),

    # ── Flock & static grass replacements ──────────────────────────────
    DIYAlternative(
        name="Dyed Sawdust",
        replaces="Flock / Scatter Turf",
        source="Any woodworking project, lumber yard, or pet bedding (hamster bedding)",
        cost="Free–$2",
        description="Fine sawdust dyed with acrylic paint or food colouring makes excellent flock.",
        tips=[
            "Mix sawdust with watered-down acrylic paint in a ziplock bag, shake, and spread to dry.",
            "Make multiple colours — dark green, light green, brown, autumn orange.",
            "Sieve for consistent particle size.",
            "Apply over PVA just like commercial flock.",
        ],
        difficulty="Easy",
    ),
    DIYAlternative(
        name="Dyed Steel Wool / Scrub Pad Fibres",
        replaces="Static Grass",
        source="Kitchen scrub pads (green Scotch-Brite type), steel wool",
        cost="$1-2",
        description="Pull apart green scrub pads for surprisingly convincing grass and hedge fibres.",
        tips=[
            "Tear and pull into thin wisps for grass tufts.",
            "Glue clumps onto terrain for hedges and overgrown vegetation.",
            "Spray paint to vary the green shades.",
            "Works especially well for dense jungle or swamp vegetation.",
        ],
        difficulty="Easy",
    ),
    DIYAlternative(
        name="Dried Tea Leaves / Herbs",
        replaces="Flock / Scatter Turf",
        source="Kitchen — used tea bags, dried oregano, thyme, parsley",
        cost="Free",
        description="Dried herbs and tea leaves make great leaf litter, dead foliage, and ground cover.",
        tips=[
            "Spread used tea leaves on a baking tray and dry in a low oven.",
            "Oregano = excellent leaf litter. Thyme = tiny bushes.",
            "Dye with a drop of green or brown paint for colour variation.",
            "Mix with PVA and apply for autumn forest floor effects.",
        ],
        difficulty="Easy",
    ),

    # ── Tree & vegetation replacements ─────────────────────────────────
    DIYAlternative(
        name="Wire + Sponge Trees",
        replaces="Tree Armatures & Foliage",
        source="Electrical wire or twist ties + kitchen/bath sponges",
        cost="Free–$2",
        description="Twist wire strands together for trunks/branches, then glue torn sponge pieces for foliage canopy.",
        tips=[
            "Use 5-8 strands of thin wire; twist the lower half tight (trunk), fan out the top (branches).",
            "Hot-glue torn green sponge chunks to branch tips.",
            "Paint trunk brown, drybrush grey for bark texture.",
            "Cheap bath sponges from the dollar store are perfect.",
        ],
        difficulty="Medium",
    ),
    DIYAlternative(
        name="Dried Real Plants & Twigs",
        replaces="Tree Armatures & Foliage",
        source="Garden, park, roadside — dried weeds, seed pods, twigs",
        cost="Free",
        description="Nature provides the best miniature trees. Dried baby's breath, thyme sprigs, and lichen are classics.",
        tips=[
            "Dried baby's breath (gypsophila) = instant deciduous trees at 28mm scale.",
            "Spray with hairspray or matte varnish to prevent crumbling.",
            "Twigs from bushes make great dead trees — just trim and base them.",
            "Collect seed pods for alien vegetation and exotic flora.",
        ],
        difficulty="Easy",
    ),

    # ── Cork / rock replacements ───────────────────────────────────────
    DIYAlternative(
        name="Bark Chips (Garden Mulch)",
        replaces="Cork Bark",
        source="Garden centre mulch bags, or collect from trees",
        cost="Free–$3",
        description="Real bark chips make the most convincing rock faces and cliff edges at any scale.",
        tips=[
            "Select flat, layered pieces for cliff faces; chunky pieces for boulders.",
            "Glue with hot glue or super glue — PVA is too weak for heavy bark.",
            "Paint and drybrush just like you would cork — results are often better.",
            "Bake at 200°F/100°C for 30 min to kill any insects.",
        ],
        difficulty="Easy",
    ),
    DIYAlternative(
        name="Crumpled Aluminium Foil Rocks",
        replaces="Cork Bark",
        source="Kitchen — aluminium foil",
        cost="Free",
        description="Tightly crumple foil into rock shapes, then coat with PVA + tissue paper for a paintable surface.",
        tips=[
            "Crumple loosely first for shape, then compress firmly.",
            "Wrap in tissue paper soaked in PVA to create a hard, paintable shell.",
            "Great for quick boulders and scatter rocks.",
            "Lightweight — won't damage your board if knocked.",
        ],
        difficulty="Easy",
    ),

    # ── Water effects replacements ─────────────────────────────────────
    DIYAlternative(
        name="PVA Glue (Thick Layers)",
        replaces="Resin Water Effects",
        source="Already in your hobby supplies",
        cost="Free–$3",
        description="Thick PVA dries clear and glossy — pour into river channels for cheap, easy water effects.",
        tips=[
            "Apply in thin layers (let each dry 24h) — thick pours stay cloudy.",
            "Tint with a tiny drop of blue/green ink or paint before pouring.",
            "Add ripple texture while tacky by poking with a toothpick.",
            "Finish with a coat of gloss varnish for extra shine.",
        ],
        difficulty="Easy",
    ),
    DIYAlternative(
        name="Hot Glue Water Effects",
        replaces="Resin Water Effects",
        source="Hot glue gun + sticks — dollar store",
        cost="$1-3",
        description="Pour hot glue into sealed channels for quick, glossy water. Dries in minutes instead of hours.",
        tips=[
            "Work fast — hot glue sets quickly. Do small sections at a time.",
            "Tint by mixing in a tiny amount of blue acrylic while molten.",
            "Creates natural ripple and wave textures as it cools.",
            "Best for small pools and streams; large rivers are tricky.",
        ],
        difficulty="Medium",
    ),
    DIYAlternative(
        name="Clear Packing Tape / Cling Film",
        replaces="Resin Water Effects",
        source="Kitchen drawer or office supplies",
        cost="Free",
        description="Stretch clear tape or cling film over a painted river bed for instant flat water.",
        tips=[
            "Paint the channel bed blue-green first for colour depth.",
            "Lay tape glossy-side up, trim to edges.",
            "Best for calm, still water — not rapids or waves.",
            "Surprisingly effective from tabletop viewing distance.",
        ],
        difficulty="Easy",
    ),

    # ── Ruins / structure replacements ─────────────────────────────────
    DIYAlternative(
        name="Foamcore / Foam Board Offcuts",
        replaces="MDF Laser-Cut Ruins",
        source="Art supply shops, dollar stores, or leftover from school projects",
        cost="$1-5",
        description="5mm foamcore is perfect for scratch-building walls, ruins, and buildings.",
        tips=[
            "Score one side of the paper and peel it away, then texture the foam with a pen for brickwork.",
            "Cut window and door openings with a craft knife.",
            "Cheap and fast — a single sheet can make 3-4 ruin pieces.",
            "Reinforce corners with hot glue for durability.",
        ],
        difficulty="Medium",
    ),
    DIYAlternative(
        name="Pizza Box / Cereal Box Ruins",
        replaces="MDF Laser-Cut Ruins",
        source="Recycling bin",
        cost="Free",
        description="Thick cardboard from food packaging, layered and textured, makes solid ruined walls.",
        tips=[
            "Laminate 2-3 layers of cereal box card with PVA for thickness.",
            "Score brick lines with an empty ballpoint pen before the glue dries.",
            "Tear the top edge jaggedly for a ruined, battle-damaged look.",
            "Coat with watered-down PVA to seal before painting.",
        ],
        difficulty="Easy",
    ),
    DIYAlternative(
        name="Aquarium Decorations",
        replaces="MDF Laser-Cut Ruins",
        source="Pet shops, charity shops/thrift stores",
        cost="$2-10",
        description="Aquarium castle/ruin decorations are pre-painted, waterproof, and often perfect 28mm scale.",
        tips=[
            "Check the scale — many aquarium ruins are surprisingly close to 28mm.",
            "Repaint to match your board's colour scheme.",
            "Thrift stores often have these for $1-2.",
            "Also check aquarium plants for alien vegetation.",
        ],
        difficulty="Easy",
    ),

    # ── Paint replacements ─────────────────────────────────────────────
    DIYAlternative(
        name="House Paint Samples / Testers",
        replaces="Craft Acrylic Paints",
        source="Hardware store paint aisle — sample pots",
        cost="$2-5 per pot",
        description="Sample pots of house paint are MUCH cheaper per ml than craft acrylics and come in every colour.",
        tips=[
            "Get 3 pots: dark brown, grey, and a tan/cream for 90% of terrain painting.",
            "Emulsion/latex house paint works identically to craft acrylics.",
            "One sample pot will paint an entire board — massive value.",
            "Some stores have 'mistint' paints for under $1 — always check.",
        ],
        difficulty="Easy",
    ),
    DIYAlternative(
        name="Coffee & Tea Staining",
        replaces="Craft Acrylic Paints",
        source="Kitchen — instant coffee, tea bags",
        cost="Free",
        description="Strong coffee or tea makes an excellent wash/stain for terrain, giving a natural aged earth tone.",
        tips=[
            "Brew triple-strength coffee or use instant coffee dissolved in minimal water.",
            "Brush or dip terrain pieces — builds up in recesses like an acrylic wash.",
            "Multiple coats deepen the colour. Seal with matte varnish when done.",
            "Especially good for desert/arid terrain and weathering stone.",
        ],
        difficulty="Easy",
    ),

    # ── Texture paint replacements ─────────────────────────────────────
    DIYAlternative(
        name="PVA + Sand + Paint Mix",
        replaces="Texture Paints",
        source="Mix from things you already have",
        cost="Free–$2",
        description="Mix PVA glue, sand, and acrylic paint together for a DIY texture paint identical to commercial products.",
        tips=[
            "Ratio: roughly 1 part PVA, 1 part sand, ½ part paint.",
            "Adjust consistency — thicker for mud, thinner for fine grit.",
            "Make a big batch in a jar; it keeps for weeks.",
            "This is literally what commercial texture paints are, at 1/10th the price.",
        ],
        difficulty="Easy",
    ),
]


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def get_alternatives_for(commercial_material: str) -> list[DIYAlternative]:
    """Find all DIY alternatives that replace a given commercial material."""
    term = commercial_material.lower()
    return [a for a in DIY_ALTERNATIVES if term in a.replaces.lower()]


def search_alternatives(query: str) -> list[DIYAlternative]:
    """Free-text search across all alternative fields."""
    q = query.lower()
    results = []
    for alt in DIY_ALTERNATIVES:
        searchable = f"{alt.name} {alt.replaces} {alt.source} {alt.description} {' '.join(alt.tips)}".lower()
        if q in searchable:
            results.append(alt)
    return results


def get_all_alternatives() -> list[DIYAlternative]:
    return list(DIY_ALTERNATIVES)


def format_alternative(alt: DIYAlternative) -> str:
    """Format a single alternative for display."""
    tips = "\n".join(f"    • {t}" for t in alt.tips)
    return (
        f"🔧 {alt.name}  (replaces: {alt.replaces})\n"
        f"   Cost: {alt.cost} | Difficulty: {alt.difficulty}\n"
        f"   Where: {alt.source}\n"
        f"   {alt.description}\n"
        f"   Tips:\n{tips}"
    )


def get_alternatives_summary() -> str:
    """Get a compact summary of all alternatives for LLM context."""
    lines = []
    for alt in DIY_ALTERNATIVES:
        lines.append(
            f"- {alt.name} (replaces {alt.replaces}, cost: {alt.cost}, "
            f"from: {alt.source}): {alt.description}"
        )
    return "\n".join(lines)

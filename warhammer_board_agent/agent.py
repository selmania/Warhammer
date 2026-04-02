"""Interactive CLI agent — the main conversational interface for board design."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm

from .terrain import (
    BOARD_THEMES,
    MATERIALS,
    TERRAIN_FEATURES,
    TerrainCategory,
    describe_feature,
    get_all_feature_names,
)
from .board_designer import BoardDesign, PlacedTerrain, create_themed_board
from .product_search import ProductSearchEngine, ProductResult, ForumPost
from .visualiser import render_board_image, HAS_PIL

console = Console()
search = ProductSearchEngine(rate_limit_seconds=1.0)

SAVE_DIR = Path("./board_designs")


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def show_welcome() -> None:
    console.print(Panel.fit(
        "[bold bright_green]⚔  WARHAMMER BOARD DESIGN AGENT  ⚔[/]\n\n"
        "Design a custom [bold]60 × 44″[/] Warhammer tabletop board\n"
        "with mountains, dry riverbeds, ruins, and more.\n\n"
        "I'll help you:\n"
        "  • Pick a theme and place terrain features\n"
        "  • Search online shops for the best materials & prices\n"
        "  • Browse forum advice from the community\n"
        "  • Export your design as an image and shopping list\n\n"
        "Type [bold cyan]help[/] at any time to see all commands.",
        border_style="bright_green",
    ))


def show_help() -> None:
    table = Table(title="Available Commands", show_header=True, header_style="bold cyan")
    table.add_column("Command", style="bold")
    table.add_column("Description")
    table.add_row("themes", "List available board themes")
    table.add_row("pick <theme>", "Start a new board from a theme (auto-places terrain)")
    table.add_row("new", "Start a blank custom board")
    table.add_row("features", "List all available terrain features")
    table.add_row("info <feature>", "Show details about a terrain feature")
    table.add_row("add <feature> <x> <y>", "Place terrain at position (x, y) in inches")
    table.add_row("remove <index>", "Remove terrain piece by index number")
    table.add_row("move <index> <x> <y>", "Move terrain piece to new position")
    table.add_row("board", "Show current board layout (ASCII map)")
    table.add_row("list", "List all placed terrain with indices")
    table.add_row("density", "Analyse terrain coverage and balance")
    table.add_row("materials", "Show all materials needed for current design")
    table.add_row("search <query>", "Search online shops for products")
    table.add_row("shop", "Build full shopping list for current design")
    table.add_row("forums <query>", "Search hobby forums for advice")
    table.add_row("export", "Export board as PNG image")
    table.add_row("save [name]", "Save board design to JSON file")
    table.add_row("load <name>", "Load a saved board design")
    table.add_row("rename <name>", "Rename the current board")
    table.add_row("notes", "Add/view build notes")
    table.add_row("help", "Show this help menu")
    table.add_row("quit", "Exit the agent")
    console.print(table)


def show_themes() -> None:
    table = Table(title="Board Themes", show_header=True, header_style="bold magenta")
    table.add_column("Key", style="bold")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Base Colour")
    for key, theme in BOARD_THEMES.items():
        table.add_row(key, theme["name"], theme["description"], theme["base_colour"])
    console.print(table)


def show_features() -> None:
    table = Table(title="Terrain Features", show_header=True, header_style="bold green")
    table.add_column("Key", style="bold")
    table.add_column("Name")
    table.add_column("Category")
    table.add_column("Size (W×D)")
    table.add_column("Height")
    for key, feat in TERRAIN_FEATURES.items():
        table.add_row(
            key,
            feat.name,
            feat.category.value,
            f"{feat.footprint_inches[0]}×{feat.footprint_inches[1]}″",
            f"{feat.min_height_inches}–{feat.max_height_inches}″",
        )
    console.print(table)


def show_board(design: BoardDesign) -> None:
    ascii_map = design.render_ascii(scale=0.5)
    console.print(Panel(ascii_map, title="Board Layout", border_style="blue"))


def show_placements(design: BoardDesign) -> None:
    if not design.placements:
        console.print("[yellow]No terrain placed yet.[/]")
        return
    table = Table(title="Placed Terrain", show_header=True, header_style="bold")
    table.add_column("#", style="bold cyan")
    table.add_column("Feature")
    table.add_column("Position")
    table.add_column("Size")
    for i, p in enumerate(design.placements):
        table.add_row(
            str(i),
            p.label or p.feature.name,
            f"({p.x}, {p.y})",
            f"{p.width}×{p.height}″",
        )
    console.print(table)


def show_materials(design: BoardDesign) -> None:
    mats = design.get_all_materials()
    if not mats:
        console.print("[yellow]No terrain on the board — no materials needed yet.[/]")
        return
    table = Table(title="Materials Needed", show_header=True, header_style="bold yellow")
    table.add_column("Material", style="bold")
    table.add_column("Description")
    table.add_column("Est. Price")
    for m in mats.values():
        table.add_row(m.name, m.description, m.typical_price_range)
    console.print(table)


def show_products(results: list[ProductResult], title: str = "Search Results") -> None:
    if not results:
        console.print("[yellow]No results found. Try different search terms.[/]")
        return
    table = Table(title=title, show_header=True, header_style="bold green")
    table.add_column("#", style="bold")
    table.add_column("Product", max_width=50)
    table.add_column("Price", style="bold cyan")
    table.add_column("Source")
    table.add_column("URL", max_width=40)
    for i, r in enumerate(results[:15]):
        table.add_row(str(i + 1), r.title[:50], r.price, r.source, r.url[:40] + "…" if len(r.url) > 40 else r.url)
    console.print(table)


def show_forum_posts(posts: list[ForumPost], title: str = "Forum Discussions") -> None:
    if not posts:
        console.print("[yellow]No forum posts found.[/]")
        return
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("#", style="bold")
    table.add_column("Title", max_width=60)
    table.add_column("Source")
    for i, p in enumerate(posts[:10]):
        table.add_row(str(i + 1), p.title[:60], p.source)
    console.print(table)


# ---------------------------------------------------------------------------
# Command processor
# ---------------------------------------------------------------------------

class BoardAgent:
    """Main agent loop — parses commands and drives the board designer."""

    def __init__(self) -> None:
        self.design: BoardDesign | None = None

    def ensure_board(self) -> bool:
        if self.design is None:
            console.print("[red]No board started yet. Use [bold]new[/bold] or [bold]pick <theme>[/bold] first.[/]")
            return False
        return True

    def run(self) -> None:
        show_welcome()
        console.print()

        while True:
            try:
                raw = Prompt.ask("\n[bold bright_green]board-agent>[/]").strip()
            except (EOFError, KeyboardInterrupt):
                console.print("\n[dim]Goodbye![/]")
                break

            if not raw:
                continue

            parts = raw.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1].strip() if len(parts) > 1 else ""

            try:
                self._dispatch(cmd, arg)
            except Exception as exc:
                console.print(f"[red]Error: {exc}[/]")

    def _dispatch(self, cmd: str, arg: str) -> None:
        handlers = {
            "help": lambda: show_help(),
            "quit": lambda: self._quit(),
            "exit": lambda: self._quit(),
            "themes": lambda: show_themes(),
            "features": lambda: show_features(),
            "new": lambda: self._new_board(),
            "pick": lambda: self._pick_theme(arg),
            "info": lambda: self._info(arg),
            "add": lambda: self._add(arg),
            "remove": lambda: self._remove(arg),
            "move": lambda: self._move(arg),
            "board": lambda: self._show_board(),
            "map": lambda: self._show_board(),
            "list": lambda: self._list(),
            "density": lambda: self._density(),
            "materials": lambda: self._materials(),
            "search": lambda: self._search(arg),
            "shop": lambda: self._shop(),
            "forums": lambda: self._forums(arg),
            "export": lambda: self._export(),
            "save": lambda: self._save(arg),
            "load": lambda: self._load(arg),
            "rename": lambda: self._rename(arg),
            "notes": lambda: self._notes(arg),
        }
        handler = handlers.get(cmd)
        if handler:
            handler()
        else:
            console.print(f"[yellow]Unknown command: {cmd}. Type [bold]help[/bold] to see options.[/]")

    # -- commands --------------------------------------------------------

    def _quit(self) -> None:
        if self.design and self.design.placements:
            if Confirm.ask("Save before quitting?"):
                self._save("")
        console.print("[dim]Goodbye! May your dice roll true. ⚔[/]")
        raise SystemExit(0)

    def _new_board(self) -> None:
        name = Prompt.ask("Board name", default="My Warhammer Board")
        colour = Prompt.ask("Base colour (e.g. brown, green, sand, grey, black)", default="brown")
        self.design = BoardDesign(name=name, base_colour=colour)
        console.print(f"[green]Created blank {self.design.width}×{self.design.height}″ board: [bold]{name}[/bold][/]")
        show_board(self.design)

    def _pick_theme(self, theme_key: str) -> None:
        if not theme_key:
            show_themes()
            theme_key = Prompt.ask("Enter theme key")
        name = Prompt.ask("Board name", default="")
        self.design = create_themed_board(theme_key, name)
        console.print(f"[green]Created [bold]{self.design.name}[/bold] with {len(self.design.placements)} terrain pieces.[/]")
        show_board(self.design)
        show_placements(self.design)

    def _info(self, key: str) -> None:
        if not key:
            key = Prompt.ask("Feature key (see [bold]features[/bold] for list)")
        text = describe_feature(key)
        console.print(Panel(text, title=f"Terrain: {key}", border_style="cyan"))
        # Also show construction tips
        feat = TERRAIN_FEATURES.get(key)
        if feat:
            console.print("[bold]Construction Tips:[/]")
            for i, tip in enumerate(feat.construction_tips, 1):
                console.print(f"  {i}. {tip}")

    def _add(self, arg: str) -> None:
        if not self.ensure_board():
            return
        parts = arg.split()
        if len(parts) < 3:
            console.print("[yellow]Usage: add <feature_key> <x> <y>[/]")
            console.print("Example: add mountain 10 5")
            return
        key = parts[0]
        x, y = float(parts[1]), float(parts[2])
        p = self.design.add_terrain(key, x, y)
        console.print(f"[green]Placed [bold]{p.label}[/bold] at ({p.x}, {p.y}).[/]")
        show_board(self.design)

    def _remove(self, arg: str) -> None:
        if not self.ensure_board():
            return
        if not arg:
            show_placements(self.design)
            arg = Prompt.ask("Index to remove")
        p = self.design.remove_terrain(int(arg))
        console.print(f"[red]Removed [bold]{p.label}[/bold].[/]")
        show_board(self.design)

    def _move(self, arg: str) -> None:
        if not self.ensure_board():
            return
        parts = arg.split()
        if len(parts) < 3:
            console.print("[yellow]Usage: move <index> <new_x> <new_y>[/]")
            return
        idx, x, y = int(parts[0]), float(parts[1]), float(parts[2])
        p = self.design.move_terrain(idx, x, y)
        console.print(f"[green]Moved [bold]{p.label}[/bold] to ({p.x}, {p.y}).[/]")
        show_board(self.design)

    def _show_board(self) -> None:
        if not self.ensure_board():
            return
        show_board(self.design)

    def _list(self) -> None:
        if not self.ensure_board():
            return
        show_placements(self.design)

    def _density(self) -> None:
        if not self.ensure_board():
            return
        pct = self.design.coverage_percent()
        assessment = self.design.terrain_density_assessment()
        console.print(f"[bold]Terrain coverage:[/] {pct:.1f}%")
        console.print(f"[bold]Assessment:[/] {assessment}")

    def _materials(self) -> None:
        if not self.ensure_board():
            return
        show_materials(self.design)

    def _search(self, query: str) -> None:
        if not query:
            query = Prompt.ask("Search for")
        console.print(f"[dim]Searching online shops for: {query}…[/]")
        results = search.search_products(query)
        show_products(results)

    def _shop(self) -> None:
        if not self.ensure_board():
            return
        mats = self.design.get_material_summary()
        if not mats:
            console.print("[yellow]No materials to shop for — add terrain first.[/]")
            return
        console.print(f"[dim]Building shopping list for {len(mats)} materials… this may take a moment.[/]")
        shopping = search.build_shopping_list(mats, limit_per_material=2)
        for mat_name, products in shopping.items():
            console.print(f"\n[bold underline]{mat_name}[/]")
            if products:
                show_products(products, title=mat_name)
            else:
                console.print("  [dim]No online results found — try a manual search.[/]")

    def _forums(self, query: str) -> None:
        if not query:
            query = Prompt.ask("Search forums for")
        console.print(f"[dim]Searching hobby forums for: {query}…[/]")
        posts = search.search_forums(query)
        show_forum_posts(posts)

    def _export(self) -> None:
        if not self.ensure_board():
            return
        if not HAS_PIL:
            console.print("[yellow]Pillow not installed — cannot render PNG. Install with: pip install Pillow[/]")
            console.print("[dim]Here's the ASCII version instead:[/]")
            show_board(self.design)
            return
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        filename = self.design.name.lower().replace(" ", "_") + ".png"
        path = SAVE_DIR / filename
        result = render_board_image(self.design, path)
        if result:
            console.print(f"[green]Board exported to: [bold]{result}[/bold][/]")
        else:
            console.print("[red]Export failed.[/]")

    def _save(self, name: str) -> None:
        if not self.ensure_board():
            return
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        filename = (name or self.design.name).lower().replace(" ", "_") + ".json"
        path = SAVE_DIR / filename
        self.design.save(path)
        console.print(f"[green]Board saved to: [bold]{path}[/bold][/]")

    def _load(self, name: str) -> None:
        if not name:
            # List available saves
            if SAVE_DIR.exists():
                files = list(SAVE_DIR.glob("*.json"))
                if files:
                    console.print("[bold]Saved designs:[/]")
                    for f in files:
                        console.print(f"  • {f.stem}")
                    name = Prompt.ask("Load which design?")
                else:
                    console.print("[yellow]No saved designs found.[/]")
                    return
            else:
                console.print("[yellow]No saved designs found.[/]")
                return
        path = SAVE_DIR / f"{name.lower().replace(' ', '_')}.json"
        if not path.exists():
            console.print(f"[red]File not found: {path}[/]")
            return
        self.design = BoardDesign.load(path)
        console.print(f"[green]Loaded: [bold]{self.design.name}[/bold] with {len(self.design.placements)} pieces.[/]")
        show_board(self.design)

    def _rename(self, name: str) -> None:
        if not self.ensure_board():
            return
        if not name:
            name = Prompt.ask("New board name")
        self.design.name = name
        console.print(f"[green]Board renamed to: [bold]{name}[/bold][/]")

    def _notes(self, arg: str) -> None:
        if not self.ensure_board():
            return
        if arg:
            self.design.notes += ("\n" if self.design.notes else "") + arg
            console.print("[green]Note added.[/]")
        if self.design.notes:
            console.print(Panel(self.design.notes, title="Build Notes", border_style="yellow"))
        elif not arg:
            note = Prompt.ask("Enter a build note")
            self.design.notes = note
            console.print("[green]Note saved.[/]")

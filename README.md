# Warhammer Board Design Agent

An interactive CLI agent for designing and building custom **60 × 44″** Warhammer tabletop boards.

## Features

- **Theme presets** — Arid Wasteland, Verdant Highlands, War-Torn City, Volcanic Hellscape, or fully custom
- **Terrain library** — Mountains, dry riverbeds, forests, ruins, craters, hills, rivers, bridges, dunes, rock outcrops
- **Board visualisation** — ASCII map in terminal + PNG image export
- **Online product search** — Scrapes Amazon, eBay, Miniature Market, Games Workshop, and more
- **Forum search** — Browse Reddit r/TerrainBuilding, r/Warhammer, DakkaDakka for community advice
- **Shopping list builder** — Aggregates all materials needed and finds prices online
- **Save/load designs** — Persist board layouts as JSON, reload and continue editing

## Quick Start

```bash
pip install -r requirements.txt
python -m warhammer_board_agent.main
```

## Commands

| Command | Description |
|---|---|
| `themes` | List board themes |
| `pick <theme>` | Start from a preset theme |
| `new` | Start a blank board |
| `features` | List all terrain types |
| `info <feature>` | Details + build tips for a feature |
| `add <feature> <x> <y>` | Place terrain at coordinates |
| `remove <index>` | Remove a terrain piece |
| `move <index> <x> <y>` | Reposition terrain |
| `board` | Show ASCII board map |
| `density` | Analyse terrain balance |
| `materials` | List all required materials |
| `search <query>` | Search online shops |
| `shop` | Auto-build shopping list for your design |
| `forums <query>` | Search hobby forums |
| `export` | Export board as PNG |
| `save` / `load` | Persist/restore designs |

## Running Tests

```bash
python -m tests.test_board_designer
```

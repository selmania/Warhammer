"""Tests for the board designer module."""

import json
import tempfile
from pathlib import Path

from warhammer_board_agent.board_designer import (
    BoardDesign,
    PlacedTerrain,
    create_themed_board,
    BOARD_WIDTH,
    BOARD_HEIGHT,
)
from warhammer_board_agent.terrain import TERRAIN_FEATURES, BOARD_THEMES


def test_board_dimensions():
    board = BoardDesign()
    assert board.width == 60
    assert board.height == 44


def test_add_terrain():
    board = BoardDesign()
    p = board.add_terrain("mountain", 10, 5)
    assert p.feature_key == "mountain"
    assert p.x == 10
    assert p.y == 5
    assert len(board.placements) == 1


def test_add_terrain_out_of_bounds():
    board = BoardDesign()
    try:
        board.add_terrain("mountain", 55, 40)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_add_terrain_overlap():
    board = BoardDesign()
    board.add_terrain("mountain", 10, 10)
    try:
        board.add_terrain("hill", 12, 12)
        assert False, "Should have raised ValueError for overlap"
    except ValueError:
        pass


def test_remove_terrain():
    board = BoardDesign()
    board.add_terrain("hill", 0, 0)
    board.add_terrain("crater", 20, 20)
    assert len(board.placements) == 2
    removed = board.remove_terrain(0)
    assert removed.feature_key == "hill"
    assert len(board.placements) == 1


def test_move_terrain():
    board = BoardDesign()
    board.add_terrain("hill", 0, 0)
    p = board.move_terrain(0, 30, 20)
    assert p.x == 30
    assert p.y == 20


def test_coverage():
    board = BoardDesign()
    assert board.coverage_percent() == 0.0
    board.add_terrain("mountain", 0, 0)
    assert board.coverage_percent() > 0


def test_auto_layout():
    board = BoardDesign()
    placed = board.auto_layout(["mountain", "hill", "dry_riverbed", "ruins"])
    assert len(placed) >= 3  # at least most should be placed


def test_themed_board():
    for theme_key in BOARD_THEMES:
        if theme_key == "custom":
            continue
        board = create_themed_board(theme_key)
        assert board.theme == theme_key
        assert len(board.placements) > 0


def test_ascii_render():
    board = create_themed_board("arid_wasteland")
    ascii_map = board.render_ascii()
    assert "─" in ascii_map
    assert len(ascii_map) > 100


def test_save_load():
    board = BoardDesign(name="Test Board")
    board.add_terrain("hill", 5, 5)
    board.add_terrain("crater", 25, 25)

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = Path(f.name)

    board.save(path)
    loaded = BoardDesign.load(path)
    assert loaded.name == "Test Board"
    assert len(loaded.placements) == 2
    assert loaded.placements[0].feature_key == "hill"
    path.unlink()


def test_material_summary():
    board = BoardDesign()
    board.add_terrain("mountain", 0, 0)
    board.add_terrain("dry_riverbed", 20, 20)
    mats = board.get_material_summary()
    assert len(mats) > 0
    assert all("name" in m for m in mats)


def test_density_assessment():
    board = BoardDesign()
    assert "Sparse" in board.terrain_density_assessment()
    board.auto_layout(["mountain", "mountain", "hill", "hill", "ruins", "ruins", "forest", "forest"])
    assessment = board.terrain_density_assessment()
    assert assessment  # should return some assessment string


def test_placed_terrain_centre():
    p = PlacedTerrain(feature_key="hill", x=10, y=20, width=8, height=6)
    assert p.centre == (14.0, 23.0)


if __name__ == "__main__":
    import sys
    # Simple test runner
    test_funcs = [v for k, v in globals().items() if k.startswith("test_")]
    passed = 0
    failed = 0
    for fn in test_funcs:
        try:
            fn()
            print(f"  PASS: {fn.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {fn.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)

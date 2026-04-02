"""Tests for the shopping advisor agent."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shopping_agent.diy_alternatives import (
    DIY_ALTERNATIVES,
    get_alternatives_for,
    search_alternatives,
    format_alternative,
    get_alternatives_summary,
)
from shopping_agent.advisor import ShoppingAdvisor, _build_system_prompt, _execute_tool


# ---------------------------------------------------------------------------
# DIY Alternatives knowledge base tests
# ---------------------------------------------------------------------------

def test_alternatives_not_empty():
    assert len(DIY_ALTERNATIVES) > 20, "Should have a substantial knowledge base"


def test_get_alternatives_for_xps():
    alts = get_alternatives_for("XPS Insulation Foam")
    assert len(alts) >= 2, "Should find multiple alternatives for XPS foam"
    names = [a.name for a in alts]
    assert any("Styrofoam" in n or "Cardboard" in n or "Expanding" in n for n in names)


def test_get_alternatives_for_flock():
    alts = get_alternatives_for("Flock")
    assert len(alts) >= 1


def test_get_alternatives_for_water():
    alts = get_alternatives_for("Resin Water Effects")
    assert len(alts) >= 2
    names = [a.name for a in alts]
    assert any("PVA" in n or "Hot Glue" in n or "Tape" in n for n in names)


def test_search_alternatives_keyword():
    results = search_alternatives("kitchen")
    assert len(results) >= 3, "Many alternatives come from the kitchen"


def test_search_alternatives_coffee():
    results = search_alternatives("coffee")
    assert len(results) >= 1
    assert any("Coffee" in r.name for r in results)


def test_format_alternative():
    alt = DIY_ALTERNATIVES[0]
    formatted = format_alternative(alt)
    assert alt.name in formatted
    assert alt.replaces in formatted
    assert alt.cost in formatted


def test_alternatives_summary():
    summary = get_alternatives_summary()
    assert len(summary) > 500, "Summary should be substantial"
    assert "replaces" in summary


def test_all_alternatives_have_required_fields():
    for alt in DIY_ALTERNATIVES:
        assert alt.name, f"Alternative missing name"
        assert alt.replaces, f"{alt.name} missing replaces"
        assert alt.source, f"{alt.name} missing source"
        assert alt.cost, f"{alt.name} missing cost"
        assert alt.description, f"{alt.name} missing description"
        assert len(alt.tips) >= 1, f"{alt.name} should have at least one tip"
        assert alt.difficulty in ("Easy", "Medium", "Advanced"), f"{alt.name} invalid difficulty"


# ---------------------------------------------------------------------------
# Advisor tests
# ---------------------------------------------------------------------------

def test_system_prompt_built():
    prompt = _build_system_prompt()
    assert "DIY" in prompt
    assert "XPS" in prompt
    assert len(prompt) > 1000


def test_advisor_offline_mode():
    advisor = ShoppingAdvisor()
    assert not advisor.is_configured
    response = advisor.chat("How do I build a mountain?")
    assert "offline" in response.lower() or "mountain" in response.lower()
    assert len(response) > 50


def test_advisor_offline_diy():
    advisor = ShoppingAdvisor()
    response = advisor.chat("XPS foam alternatives")
    assert len(response) > 50


def test_advisor_offline_material():
    advisor = ShoppingAdvisor()
    response = advisor.chat("Tell me about static grass")
    assert len(response) > 50


def test_advisor_reset():
    advisor = ShoppingAdvisor()
    advisor.chat("hello")
    assert len(advisor.history) >= 1
    advisor.reset()
    assert len(advisor.history) == 0


def test_execute_tool_terrain_info():
    result = _execute_tool("terrain_info", {"feature": "mountain"})
    assert "Mountain" in result
    assert "Construction Tips" in result


def test_execute_tool_terrain_info_unknown():
    result = _execute_tool("terrain_info", {"feature": "nonexistent"})
    assert "Unknown" in result


def test_execute_tool_diy_alternatives():
    result = _execute_tool("diy_alternatives", {"query": "foam"})
    assert len(result) > 50


def test_execute_tool_unknown():
    result = _execute_tool("nonexistent_tool", {})
    assert "Unknown tool" in result


# ---------------------------------------------------------------------------
# Flask app tests
# ---------------------------------------------------------------------------

def test_flask_app_creates():
    from shopping_agent.app import app
    assert app is not None


def test_flask_index():
    from shopping_agent.app import app
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Terrain Shopping Advisor" in resp.data


def test_flask_status():
    from shopping_agent.app import app
    client = app.test_client()
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "api_configured" in data


def test_flask_chat():
    from shopping_agent.app import app
    client = app.test_client()
    resp = client.post("/api/chat", json={"message": "How do I build mountains?"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "reply" in data
    assert len(data["reply"]) > 20


def test_flask_chat_empty():
    from shopping_agent.app import app
    client = app.test_client()
    resp = client.post("/api/chat", json={"message": ""})
    assert resp.status_code == 400


def test_flask_reset():
    from shopping_agent.app import app
    client = app.test_client()
    resp = client.post("/api/reset")
    assert resp.status_code == 200


if __name__ == "__main__":
    test_funcs = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
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

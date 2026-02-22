"""Render fallback smoke tests."""

import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(REPO_ROOT, "data", "catalog.json")


def _load_catalog():
    with open(CATALOG_PATH) as f:
        return json.load(f)


def test_all_primitives_have_fallback():
    """Every primitive must define a render fallback."""
    catalog = _load_catalog()
    for name, prim in catalog["primitives"].items():
        assert "fallback" in prim["render"], f"{name} missing render fallback"


def test_fallback_always_resolves():
    """resolve_render must always return a valid descriptor, even with no renderers."""
    from render.fallback import resolve_render

    catalog = _load_catalog()
    for name, prim in catalog["primitives"].items():
        desc = resolve_render(prim, available_renderers=set())
        assert desc["mode"] == "fallback", f"{name}: expected fallback mode"
        assert "type" in desc, f"{name}: missing fallback type"
        assert "color" in desc, f"{name}: missing fallback color"
        assert len(desc["color"]) == 4, f"{name}: color must be RGBA"

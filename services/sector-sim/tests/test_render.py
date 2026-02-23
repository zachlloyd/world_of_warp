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


def test_neon_light_strip_emissive_fallback():
    """neon_light_strip_v2 fallback must resolve as emissive strip with glow metadata."""
    from render.fallback import resolve_render

    catalog = _load_catalog()
    prim = catalog["primitives"]["neon_light_strip_v2"]
    desc = resolve_render(prim, available_renderers=set())

    assert desc["mode"] == "fallback"
    assert desc["type"] == "emissive_strip"
    assert desc["emissive"] is True
    assert "glow_intensity" in desc, "emissive fallback must include glow_intensity"
    assert desc["glow_intensity"] > 0
    assert "color_palette" in desc, "emissive fallback must include color_palette"
    assert len(desc["color_palette"]) >= 1, "color_palette must have at least one entry"

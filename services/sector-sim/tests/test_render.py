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


def test_emissive_strip_fallback():
    """neon_light_strip_v2 fallback must resolve as emissive strip with glow and palette."""
    from render.fallback import resolve_render

    catalog = _load_catalog()
    prim = catalog["primitives"]["neon_light_strip_v2"]
    desc = resolve_render(prim, available_renderers=set())

    assert desc["mode"] == "fallback"
    assert desc["type"] == "emissive_strip"
    assert desc["emissive"] is True
    assert desc["glow_intensity"] == 3.5
    assert "color_palette" in desc
    assert len(desc["color_palette"]) == 3
    # Each palette entry must be RGBA
    for color in desc["color_palette"]:
        assert len(color) == 4


def test_emissive_fallback_with_unknown_renderer():
    """An unknown renderer must still gracefully display the emissive strip fallback."""
    from render.fallback import resolve_render

    catalog = _load_catalog()
    prim = catalog["primitives"]["neon_light_strip_v2"]
    # Simulate renderers that don't know about the neon mesh
    desc = resolve_render(prim, available_renderers={"other_mesh.glb"})

    assert desc["mode"] == "fallback"
    assert desc["type"] == "emissive_strip"
    assert desc["emissive"] is True

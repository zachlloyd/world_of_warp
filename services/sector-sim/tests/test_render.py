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


def test_neon_light_strip_v2_fallback_emissive_strip():
    """neon_light_strip_v2 must render as emissive_strip when no renderer is available.

    This is the render fallback smoke test: an unknown renderer must
    gracefully display the primitive as a bright emissive strip.
    """
    from render.fallback import resolve_render

    catalog = _load_catalog()
    prim = catalog["primitives"]["neon_light_strip_v2"]

    # Simulate an unknown renderer by providing an empty set
    desc = resolve_render(prim, available_renderers=set())
    assert desc["mode"] == "fallback"
    assert desc["type"] == "emissive_strip"
    assert desc["emissive"] is True
    assert desc["glow_intensity"] > 0, "Emissive strip must have positive glow"
    assert "color_palette" in desc, "Emissive strip must include color palette"
    assert len(desc["color"]) == 4


def test_neon_light_strip_v2_fallback_with_unknown_renderer():
    """Even with a renderer set that doesn't include the mesh, fallback works."""
    from render.fallback import resolve_render

    catalog = _load_catalog()
    prim = catalog["primitives"]["neon_light_strip_v2"]

    # Provide renderers that don't know about neon_light_strip_v2.glb
    desc = resolve_render(prim, available_renderers={"other_mesh.glb", "basic.glb"})
    assert desc["mode"] == "fallback"
    assert desc["type"] == "emissive_strip"

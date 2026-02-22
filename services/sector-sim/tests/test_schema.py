"""Schema validation tests for the primitive catalog."""

import json
import os

import jsonschema

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(REPO_ROOT, "data", "catalog.json")
SCHEMA_PATH = os.path.join(REPO_ROOT, "schema", "catalog.schema.json")


def _load_json(path):
    with open(path) as f:
        return json.load(f)


def test_catalog_validates_against_schema():
    """The entire catalog must pass JSON-schema validation."""
    catalog = _load_json(CATALOG_PATH)
    schema = _load_json(SCHEMA_PATH)
    jsonschema.validate(instance=catalog, schema=schema)


def test_all_primitives_have_required_fields():
    """Every primitive must declare category, capabilities, sim, render, constraints, rollout."""
    catalog = _load_json(CATALOG_PATH)
    required = {"category", "capabilities", "sim", "render", "constraints", "rollout"}
    for name, prim in catalog["primitives"].items():
        missing = required - set(prim.keys())
        assert not missing, f"{name} missing fields: {missing}"


def test_tick_handlers_registered():
    """Every tick_handler referenced in the catalog must exist in the handler registry."""
    from sim.capabilities import TICK_HANDLERS

    catalog = _load_json(CATALOG_PATH)
    for name, prim in catalog["primitives"].items():
        handler = prim["sim"]["tick_handler"]
        assert handler in TICK_HANDLERS, (
            f"{name} references unknown tick handler '{handler}'"
        )


def test_neon_light_strip_v2_schema():
    """neon_light_strip_v2 must validate and have correct field values."""
    catalog = _load_json(CATALOG_PATH)
    schema = _load_json(SCHEMA_PATH)
    jsonschema.validate(instance=catalog, schema=schema)

    prim = catalog["primitives"]["neon_light_strip_v2"]
    assert prim["category"] == "ENTITY"
    assert set(prim["capabilities"]) == {"AESTHETIC", "LIGHTING", "WAYFINDING"}
    assert prim["sim"]["power_generation_kw"] == 0.0
    assert prim["sim"]["power_consumption_kw"] > 0
    assert prim["sim"]["visibility_score"] > 0
    assert prim["sim"]["max_contiguous_segments"] == 32
    assert prim["constraints"]["max_contiguous_length"] == 32
    assert prim["rollout"] == "EXPERIMENTAL"


def test_neon_light_strip_v2_fallback_is_emissive():
    """neon_light_strip_v2 fallback must be an emissive_strip with glow and palette."""
    catalog = _load_json(CATALOG_PATH)
    fb = catalog["primitives"]["neon_light_strip_v2"]["render"]["fallback"]
    assert fb["type"] == "emissive_strip"
    assert fb["emissive"] is True
    assert fb["glow_intensity"] > 0
    assert len(fb["color_palette"]) >= 1
    for color in fb["color_palette"]:
        assert len(color) == 4, "Each palette entry must be RGBA"

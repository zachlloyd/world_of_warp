"""Sim engine smoke tests."""

import json
import copy
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(REPO_ROOT, "data", "catalog.json")


def _load_catalog():
    with open(CATALOG_PATH) as f:
        return json.load(f)


def _make_entity(primitive_def, entity_id="test-entity"):
    """Build a minimal entity dict from a primitive definition."""
    entity = copy.deepcopy(primitive_def)
    entity["id"] = entity_id
    return entity


def test_power_gen_tick_deterministic():
    """solar_panel_v1 tick is deterministic across seeds."""
    from sim.capabilities import run_tick

    catalog = _load_catalog()
    prim = catalog["primitives"]["solar_panel_v1"]
    entity = _make_entity(prim)

    results = []
    for seed in (1, 2, 42, 9999):
        state = {}
        for tick in range(10):
            state = run_tick(entity, state, tick, seed)
        results.append(state["power_pool_kw"])

    # All seeds must produce the same deterministic output
    assert all(r == results[0] for r in results), f"Non-deterministic: {results}"


def test_storage_tick_deterministic():
    """cargo_crate_v1 tick is deterministic across seeds."""
    from sim.capabilities import run_tick

    catalog = _load_catalog()
    prim = catalog["primitives"]["cargo_crate_v1"]
    entity = _make_entity(prim)

    results = []
    for seed in (1, 2, 42, 9999):
        state = {}
        for tick in range(10):
            state = run_tick(entity, state, tick, seed)
        results.append(state["power_pool_kw"])

    assert all(r == results[0] for r in results), f"Non-deterministic: {results}"


def test_neon_light_strip_tick_deterministic():
    """neon_light_strip_v2 tick is deterministic across seeds."""
    from sim.capabilities import run_tick

    catalog = _load_catalog()
    prim = catalog["primitives"]["neon_light_strip_v2"]
    entity = _make_entity(prim)

    results = []
    for seed in (1, 2, 42, 9999):
        state = {}
        for tick in range(10):
            state = run_tick(entity, state, tick, seed)
        results.append(
            (state["power_pool_kw"], state["lighting_level"], state["local_visibility_score"])
        )

    # All seeds must produce identical deterministic output
    assert all(r == results[0] for r in results), f"Non-deterministic: {results}"
    # Verify expected values after 10 ticks (use approx for floating-point)
    import pytest
    power, lighting, visibility = results[0]
    assert power == pytest.approx(-3.0), f"Expected -3.0 power, got {power}"  # 10 * -0.3
    assert lighting == pytest.approx(10.0), f"Expected 10.0 lighting, got {lighting}"  # 10 * 1.0
    assert visibility == pytest.approx(6.0), f"Expected 6.0 visibility, got {visibility}"  # 10 * 0.6

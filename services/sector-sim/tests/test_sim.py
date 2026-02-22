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

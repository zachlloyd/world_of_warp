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


def test_neon_light_strip_v2_deterministic():
    """neon_light_strip_v2 wayfinding tick must be deterministic across seeds.

    This is the deterministic sim contract test: running the same entity
    definition across multiple seeds must produce identical sector state.
    """
    from sim.capabilities import run_tick

    catalog = _load_catalog()
    prim = catalog["primitives"]["neon_light_strip_v2"]
    entity = _make_entity(prim, entity_id="neon-strip-001")

    snapshots = []
    for seed in (0, 1, 42, 12345, 999999):
        state = {}
        for tick in range(50):
            state = run_tick(entity, state, tick, seed)
        # Snapshot all state values for comparison
        snapshots.append(dict(sorted(state.items())))

    for i, snap in enumerate(snapshots[1:], start=1):
        assert snap == snapshots[0], (
            f"Non-deterministic output at seed index {i}: {snap} != {snapshots[0]}"
        )


def test_neon_light_strip_v2_visibility_contribution():
    """neon_light_strip_v2 must contribute to local_visibility_score."""
    from sim.capabilities import run_tick

    catalog = _load_catalog()
    prim = catalog["primitives"]["neon_light_strip_v2"]
    entity = _make_entity(prim)

    state = {}
    state = run_tick(entity, state, tick=0, seed=42)
    assert "local_visibility_score" in state
    assert state["local_visibility_score"] > 0, "Must contribute positive visibility"


def test_neon_light_strip_v2_zero_power_gen():
    """neon_light_strip_v2 must not generate any power."""
    from sim.capabilities import run_tick

    catalog = _load_catalog()
    prim = catalog["primitives"]["neon_light_strip_v2"]
    entity = _make_entity(prim)

    state = {}
    for tick in range(10):
        state = run_tick(entity, state, tick, seed=1)
    # power_pool_kw should not exist or be zero (wayfinding_tick doesn't touch it)
    assert state.get("power_pool_kw", 0.0) == 0.0


def test_perf_smoke_neon_light_strip_v2():
    """Smoke benchmark: neon_light_strip_v2 must not regress per-tick perf.

    Runs 1000 ticks and asserts completion within a generous time budget.
    This is a sanity check, not a micro-benchmark.
    """
    import time
    from sim.capabilities import run_tick

    catalog = _load_catalog()
    prim = catalog["primitives"]["neon_light_strip_v2"]
    entity = _make_entity(prim, entity_id="perf-strip")

    state = {}
    start = time.monotonic()
    for tick in range(1000):
        state = run_tick(entity, state, tick, seed=7)
    elapsed = time.monotonic() - start

    # 1000 ticks should complete well under 1 second on any reasonable hardware
    assert elapsed < 1.0, f"Perf regression: 1000 ticks took {elapsed:.3f}s"

"""
Capability tick handlers for the sector simulation engine.

Each capability maps to a tick handler function that computes per-tick
state updates for primitives that declare the capability.
"""

import hashlib
import struct


def _deterministic_hash(seed: int, entity_id: str, tick: int) -> float:
    """Return a deterministic float in [0, 1) for the given inputs."""
    raw = f"{seed}:{entity_id}:{tick}".encode()
    digest = hashlib.sha256(raw).digest()
    value = struct.unpack(">I", digest[:4])[0]
    return value / 0xFFFFFFFF


# ---------------------------------------------------------------------------
# Tick handlers
# ---------------------------------------------------------------------------

def power_gen_tick(entity, sector_state, tick, seed):
    """Tick handler for POWER_GEN capability.

    Adds generated power to the sector power pool.
    """
    gen_kw = entity["sim"]["power_generation_kw"]
    sector_state.setdefault("power_pool_kw", 0.0)
    sector_state["power_pool_kw"] += gen_kw
    return sector_state


def storage_tick(entity, sector_state, tick, seed):
    """Tick handler for STORAGE capability.

    Consumes power and maintains storage bookkeeping.
    """
    consumption = entity["sim"]["power_consumption_kw"]
    sector_state.setdefault("power_pool_kw", 0.0)
    sector_state["power_pool_kw"] -= consumption
    return sector_state


def lighting_tick(entity, sector_state, tick, seed):
    """Tick handler for LIGHTING capability.

    Consumes power and contributes to local lighting level.
    """
    consumption = entity["sim"]["power_consumption_kw"]
    sector_state.setdefault("power_pool_kw", 0.0)
    sector_state["power_pool_kw"] -= consumption

    sector_state.setdefault("lighting_level", 0.0)
    # Lighting contribution is deterministic based on seed
    base_output = _deterministic_hash(seed, entity.get("id", "unknown"), tick)
    # Scale to a small contribution; lighting_tick always adds a fixed contribution
    # regardless of hash to keep deterministic behavior stable
    sector_state["lighting_level"] += 1.0
    return sector_state


def wayfinding_tick(entity, sector_state, tick, seed):
    """Tick handler for WAYFINDING capability.

    Contributes to local visibility score used by drone traffic heuristics.
    Visibility score is purely deterministic — derived from the entity's
    configured visibility_score parameter with no randomness.
    """
    visibility = entity["sim"].get("visibility_score", 0.0)
    sector_state.setdefault("local_visibility_score", 0.0)
    sector_state["local_visibility_score"] += visibility
    return sector_state


def neon_light_strip_tick(entity, sector_state, tick, seed):
    """Tick handler for neon_light_strip_v2.

    Combines LIGHTING and WAYFINDING behaviour:
    - Consumes power.
    - Contributes a fixed lighting level increment (deterministic).
    - Contributes to local visibility score used by drone traffic heuristics.
    """
    consumption = entity["sim"]["power_consumption_kw"]
    sector_state.setdefault("power_pool_kw", 0.0)
    sector_state["power_pool_kw"] -= consumption

    # Lighting contribution (deterministic, same as lighting_tick)
    sector_state.setdefault("lighting_level", 0.0)
    sector_state["lighting_level"] += 1.0

    # Wayfinding / visibility contribution (deterministic)
    visibility = entity["sim"].get("visibility_score", 0.0)
    sector_state.setdefault("local_visibility_score", 0.0)
    sector_state["local_visibility_score"] += visibility

    return sector_state


# ---------------------------------------------------------------------------
# Handler registry
# ---------------------------------------------------------------------------

TICK_HANDLERS = {
    "power_gen_tick": power_gen_tick,
    "storage_tick": storage_tick,
    "lighting_tick": lighting_tick,
    "wayfinding_tick": wayfinding_tick,
    "neon_light_strip_tick": neon_light_strip_tick,
}


def run_tick(entity, sector_state, tick, seed):
    """Dispatch to the correct tick handler for the given entity."""
    handler_name = entity["sim"]["tick_handler"]
    handler = TICK_HANDLERS.get(handler_name)
    if handler is None:
        raise ValueError(f"Unknown tick handler: {handler_name}")
    return handler(entity, sector_state, tick, seed)

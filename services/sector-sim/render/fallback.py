"""
Render fallback resolver for the sector simulation.

When a renderer does not support a primitive's primary mesh, the fallback
config is used to produce a safe, visible representation.
"""


def resolve_render(primitive_def, available_renderers=None):
    """Resolve the render output for a primitive definition.

    If the primary mesh is supported by one of the available renderers,
    return a mesh render descriptor. Otherwise, return the fallback
    descriptor so the primitive is always visible.

    Args:
        primitive_def: The primitive definition dict from catalog.json.
        available_renderers: Set of renderer names that support mesh loading.
            If None or empty, fallback is always used.

    Returns:
        A render descriptor dict.
    """
    if available_renderers is None:
        available_renderers = set()

    render_cfg = primitive_def.get("render", {})
    mesh = render_cfg.get("mesh")

    # If there is a mesh and a renderer supports it, use the mesh path
    if mesh and mesh in available_renderers:
        return {"mode": "mesh", "mesh": mesh}

    # Otherwise use the fallback
    fallback = render_cfg.get("fallback", {})
    descriptor = {
        "mode": "fallback",
        "type": fallback.get("type", "box"),
        "color": fallback.get("color", [1.0, 1.0, 1.0, 1.0]),
        "emissive": fallback.get("emissive", False),
    }

    # Emissive-specific properties
    if descriptor["emissive"]:
        descriptor["glow_intensity"] = fallback.get("glow_intensity", 1.0)
        if "color_palette" in fallback:
            descriptor["color_palette"] = fallback["color_palette"]

    return descriptor

"""Prepare human-friendly explanations from structured simulation data."""

def prepare_explanation(simulation: dict) -> str:
    parts = simulation.get("model", {}).get("parts", [])
    materials = simulation.get("materials", [])
    steps = simulation.get("steps", [])
    lines = []
    if parts:
        lines.append(f"Model has {len(parts)} part(s).")
    if materials:
        lines.append(f"Materials: {', '.join(m.get('name','?') for m in materials)}")
    if steps:
        lines.append(f"Steps: {', '.join(s.get('name','?') for s in steps)}")
    return " ".join(lines)

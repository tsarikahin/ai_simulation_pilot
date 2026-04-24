"""Rule-based validators for the parsed simulation."""

def validate_simulation(simulation: dict) -> list:
    issues = []
    if not simulation.get("model") or not simulation["model"].get("parts"):
        issues.append("No parts detected in the model.")
    return issues

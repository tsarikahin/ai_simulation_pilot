"""Minimal Abaqus .inp parser that extracts top-level blocks into a dict.

This parser is intentionally simple for the MVP and recognizes common keywords like *Part, *Material, *Nset, *Elset, *Boundary, *Cload, *Step.
"""

from .section_splitter import split_sections
from .utils import parse_card_header


def parse_sections(inp_text: str) -> dict:
    parsed = {
        "model": {"parts": []},
        "sets": {"node_sets": [], "element_sets": []},
        "materials": [],
        "boundary_conditions": [],
        "loads": [],
        "steps": [],
    }

    for sec in split_sections(inp_text):
        lines = [l for l in sec.splitlines() if l.strip()]
        if not lines:
            continue
        header = lines[0]
        key, params = parse_card_header(header)
        key = key.lower()
        if key == "part":
            name = params.get("name") or params.get("part") or "Part-1"
            parsed["model"]["parts"].append({"name": name, "node_count": 0, "element_count": 0, "element_types": []})
        elif key in ("nset", "nset,", "nset ") or key == "nset":
            # naive: collect name if present
            name = params.get("nset") or params.get("name") or "NSET"
            parsed["sets"]["node_sets"].append({"name": name, "size": 0})
        elif key in ("elset",):
            name = params.get("elset") or params.get("name") or "ELSET"
            parsed["sets"]["element_sets"].append({"name": name, "size": 0})
        elif key == "material":
            name = params.get("name") or (lines[0].split("=", 1)[-1].strip() if "=" in lines[0] else "Material-1")
            parsed["materials"].append({"name": name, "type": "unknown", "properties": {}})
        elif key == "boundary":
            parsed["boundary_conditions"].append({"type": "displacement", "target": None, "dofs": [], "value": None})
        elif key == "cload":
            parsed["loads"].append({"type": "cload", "target": None, "dof": None, "value": None})
        elif key == "step":
            parsed["steps"].append({"name": params.get("name") or "Step-1", "analysis_type": "static"})

    return parsed

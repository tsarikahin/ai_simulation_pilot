"""Minimal Abaqus .inp parser that extracts top-level blocks into a dict.

This parser is intentionally simple for the MVP and recognizes common keywords like *Part, *Material, *Nset, *Elset, *Boundary, *Cload, *Step.
"""

from typing import List

from .section_splitter import split_sections
from .utils import parse_card_header


def _parse_int(value: str):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_float(value: str):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_data_rows(lines: List[str]) -> List[List[str]]:
    rows = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("**"):
            continue
        rows.append([token.strip() for token in stripped.split(",") if token.strip()])
    return rows


def _count_set_size(rows: List[List[str]], is_generate: bool) -> int:
    if not rows:
        return 0

    if is_generate:
        total = 0
        for row in rows:
            if len(row) < 3:
                continue
            start = _parse_int(row[0])
            end = _parse_int(row[1])
            inc = _parse_int(row[2])
            if start is None or end is None or inc in (None, 0):
                continue
            span = end - start
            if span * inc < 0:
                continue
            total += (abs(span) // abs(inc)) + 1
        return total

    total = 0
    for row in rows:
        for token in row:
            if _parse_int(token) is not None:
                total += 1
    return total


def parse_sections(inp_text: str) -> dict:
    parsed = {
        "model": {"parts": []},
        "sets": {"node_sets": [], "element_sets": []},
        "materials": [],
        "boundary_conditions": [],
        "loads": [],
        "steps": [],
    }

    current_part = None
    current_material = None

    for sec in split_sections(inp_text):
        lines = [l for l in sec.splitlines() if l.strip()]
        if not lines:
            continue
        header = lines[0]
        data_rows = _parse_data_rows(lines[1:])
        key, params = parse_card_header(header)
        key = key.lower()

        if key == "part":
            name = params.get("name") or params.get("part") or "Part-1"
            current_part = {
                "name": name,
                "node_count": 0,
                "element_count": 0,
                "element_types": [],
                "nodes": {},
                "elements": [],
            }
            parsed["model"]["parts"].append(current_part)
        elif key == "end part":
            current_part = None
        elif key == "node":
            if current_part is not None:
                current_part["node_count"] += len(data_rows)
                for row in data_rows:
                    if len(row) < 3:
                        continue
                    nid = _parse_int(row[0])
                    x = _parse_float(row[1])
                    y = _parse_float(row[2])
                    z = _parse_float(row[3]) if len(row) > 3 else 0.0
                    if nid is not None:
                        current_part["nodes"][nid] = [x, y, z]
        elif key == "element":
            if current_part is not None:
                current_part["element_count"] += len(data_rows)
                etype = (params.get("type") or "").upper()
                if etype and etype not in current_part["element_types"]:
                    current_part["element_types"].append(etype)
                for row in data_rows:
                    if len(row) < 2:
                        continue
                    eid = _parse_int(row[0])
                    node_ids = [_parse_int(n) for n in row[1:] if _parse_int(n) is not None]
                    current_part["elements"].append({"id": eid, "type": etype, "nodes": node_ids})
        elif key == "nset":
            name = params.get("nset") or params.get("name") or "NSET"
            size = _count_set_size(data_rows, is_generate=("generate" in params or "generate" in header.lower()))
            parsed["sets"]["node_sets"].append({"name": name, "size": size})
        elif key == "elset":
            name = params.get("elset") or params.get("name") or "ELSET"
            size = _count_set_size(data_rows, is_generate=("generate" in params or "generate" in header.lower()))
            parsed["sets"]["element_sets"].append({"name": name, "size": size})
        elif key == "material":
            name = params.get("name") or (lines[0].split("=", 1)[-1].strip() if "=" in lines[0] else "Material-1")
            current_material = {"name": name, "type": "unknown", "properties": {}}
            parsed["materials"].append(current_material)
        elif key == "elastic":
            if current_material is not None and data_rows:
                row = data_rows[0]
                e = _parse_float(row[0]) if len(row) > 0 else None
                nu = _parse_float(row[1]) if len(row) > 1 else None
                current_material["type"] = "elastic"
                current_material["properties"] = {
                    "youngs_modulus": e,
                    "poisson_ratio": nu,
                }
        elif key == "boundary":
            for row in data_rows:
                if len(row) < 3:
                    continue
                target = row[0]
                dof_start = _parse_int(row[1])
                dof_end = _parse_int(row[2])
                value = _parse_float(row[3]) if len(row) > 3 else 0.0
                if dof_start is None or dof_end is None:
                    continue
                dofs = list(range(dof_start, dof_end + 1)) if dof_end >= dof_start else [dof_start]
                parsed["boundary_conditions"].append(
                    {"type": "displacement", "target": target, "dofs": dofs, "value": value}
                )
        elif key == "cload":
            for row in data_rows:
                if len(row) < 3:
                    continue
                parsed["loads"].append(
                    {
                        "type": "cload",
                        "target": row[0],
                        "dof": _parse_int(row[1]),
                        "value": _parse_float(row[2]),
                    }
                )
        elif key == "step":
            parsed["steps"].append({"name": params.get("name") or "Step-1", "analysis_type": "static"})

    return parsed

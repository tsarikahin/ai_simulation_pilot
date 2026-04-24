import os
from simcopilot.parser.inp_reader import read_inp
from simcopilot.parser.abaqus_parser import parse_sections


def test_read_and_parse_sample():
    root = os.path.dirname(os.path.dirname(__file__))
    sample = os.path.normpath(os.path.join(root, "samples", "simple_beam.inp"))
    content = read_inp(sample)
    assert "*Part" in content or "*PART" in content
    parsed = parse_sections(content)
    assert isinstance(parsed, dict)


def test_parse_hoist_has_mesh_and_conditions():
    root = os.path.dirname(os.path.dirname(__file__))
    sample = os.path.normpath(os.path.join(root, "samples", "hoist.inp"))
    content = read_inp(sample)

    parsed = parse_sections(content)

    assert parsed["model"]["parts"]
    part = parsed["model"]["parts"][0]
    assert part["name"] == "Hoist"
    assert part["node_count"] == 5
    assert part["element_count"] == 7
    assert "T2D2" in part["element_types"]

    material = parsed["materials"][0]
    assert material["name"] == "Steel"
    assert material["type"] == "elastic"
    assert material["properties"]["youngs_modulus"] == 2e11
    assert material["properties"]["poisson_ratio"] == 0.3

    # Hoist input has 3 boundary rows and 1 cload row.
    assert len(parsed["boundary_conditions"]) == 3
    assert len(parsed["loads"]) == 1
    assert parsed["loads"][0]["target"] == "Set-3"
    assert parsed["loads"][0]["dof"] == 2
    assert parsed["loads"][0]["value"] == -10000.0

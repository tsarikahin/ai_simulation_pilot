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

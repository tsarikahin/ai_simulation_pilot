"""Small parser utilities."""

from typing import Tuple, Dict


def parse_card_header(line: str) -> Tuple[str, Dict[str, str]]:
    """Parse a header like '*Nset, nset=LEFT' and return (keyword, params).

    Params keys are lower-cased.
    """
    line = line.strip().lstrip("*")
    parts = [p.strip() for p in line.split(",") if p.strip()]
    if not parts:
        return "", {}
    keyword = parts[0]
    params = {}
    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            params[k.strip().lower()] = v.strip()
    return keyword, params

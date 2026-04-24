"""Simple .inp file reader."""

def read_inp(path: str) -> str:
    """Return the contents of an Abaqus `.inp` file as text."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

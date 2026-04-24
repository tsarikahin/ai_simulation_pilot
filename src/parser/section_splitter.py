"""Split an Abaqus `.inp` file into keyword sections.

This is a lightweight, conservative splitter: every line starting with `*` begins a new section.
"""

def split_sections(inp_text: str) -> list:
    """Return a list of sections (each section is the raw text block starting with `*`)."""
    sections = []
    current = []
    for line in inp_text.splitlines():
        if line.strip().startswith("*"):
            if current:
                sections.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current))
    return sections

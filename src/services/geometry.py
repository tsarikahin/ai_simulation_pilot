"""Deterministic mesh visualization — renders the mesh wireframe as a PNG using PyVista.

No LLM is involved. Input is the parsed simulation dict from abaqus_parser.parse_sections().
"""

import io
from typing import Any, Dict, List

import numpy as np
import pyvista as pv
from PIL import Image

# ---------------------------------------------------------------------------
# VTK cell type constants
# ---------------------------------------------------------------------------
_VTK_LINE = 3
_VTK_TETRA = 10
_VTK_HEX = 12
_VTK_WEDGE = 13

# Map Abaqus element type -> VTK type (for solid/volume elements only)
_ETYPE_TO_VTK = {
    "C3D4": _VTK_TETRA,
    "C3D4H": _VTK_TETRA,
    "C3D8": _VTK_HEX,
    "C3D8R": _VTK_HEX,
    "C3D8I": _VTK_HEX,
    "C3D6": _VTK_WEDGE,
    "C3D6H": _VTK_WEDGE,
}

# 2-node (and 3-node midside) line/truss/beam element types
_LINE_ETYPES = frozenset({"T2D2", "T2D3", "T3D2", "T3D3", "B31", "B32", "CONN3D2"})


def render_mesh_png(parsed: Dict[str, Any]) -> bytes:
    """Render the mesh of all parts as a PNG wireframe using PyVista.

    Args:
        parsed: The dict returned by abaqus_parser.parse_sections().

    Returns:
        Raw PNG bytes.

    Raises:
        ValueError: If no parts or no node coordinates are found.
    """
    parts = parsed.get("model", {}).get("parts", [])
    if not parts:
        raise ValueError("No parts found in parsed simulation.")

    all_nodes: Dict[int, List[float]] = {}
    all_elements: List[Dict[str, Any]] = []
    for part in parts:
        all_nodes.update(part.get("nodes", {}))
        all_elements.extend(part.get("elements", []))

    if not all_nodes:
        raise ValueError("No node coordinates found — cannot render mesh.")

    # Build ordered point array and 0-based ID map
    node_ids_sorted = sorted(all_nodes.keys())
    id_to_idx = {nid: i for i, nid in enumerate(node_ids_sorted)}
    points = np.array(
        [[all_nodes[nid][0], all_nodes[nid][1], all_nodes[nid][2]] for nid in node_ids_sorted],
        dtype=float,
    )

    plotter = pv.Plotter(off_screen=True, window_size=[900, 700])
    plotter.set_background("white")

    # Separate elements into line cells and solid/volume cells
    line_connectivity: List[int] = []
    solid_cells: List[List[int]] = []
    solid_vtk_types: List[int] = []

    for elem in all_elements:
        etype = elem.get("type", "")
        nids = [id_to_idx[n] for n in elem["nodes"] if n in id_to_idx]

        if etype in _LINE_ETYPES:
            if len(nids) >= 2:
                line_connectivity.extend([2, nids[0], nids[1]])
        else:
            vtk_type = _ETYPE_TO_VTK.get(etype)
            if vtk_type is not None and len(nids) >= 2:
                solid_cells.append([len(nids)] + nids)
                solid_vtk_types.append(vtk_type)

    # Render line/truss/beam elements
    if line_connectivity:
        mesh = pv.PolyData(points)
        mesh.lines = np.array(line_connectivity, dtype=int)
        plotter.add_mesh(mesh, color="#1565C0", line_width=3, render_lines_as_tubes=True)

    # Render solid elements as wireframe (edge extraction via VTK)
    if solid_cells:
        flat = []
        for cell in solid_cells:
            flat.extend(cell)
        ugrid = pv.UnstructuredGrid(
            np.array(flat, dtype=int),
            np.array(solid_vtk_types, dtype=np.uint8),
            points,
        )
        edges = ugrid.extract_all_edges()
        plotter.add_mesh(edges, color="#1565C0", line_width=2)

    # Node point cloud
    cloud = pv.PolyData(points)
    plotter.add_mesh(cloud, color="#E53935", point_size=12, render_points_as_spheres=True)

    # Camera: isometric for 3D, top-down (XY) for 2D flat meshes
    z_range = points[:, 2].max() - points[:, 2].min()
    if z_range > 1e-10:
        plotter.view_isometric()
    else:
        plotter.view_xy()

    part_names = ", ".join(p["name"] for p in parts)
    plotter.add_text(
        f"{part_names}  |  {len(all_nodes)} nodes  {len(all_elements)} elements",
        position="upper_edge",
        font_size=10,
        color="black",
    )

    img_array = plotter.screenshot(return_img=True)
    plotter.close()

    buf = io.BytesIO()
    Image.fromarray(img_array).save(buf, format="PNG")
    buf.seek(0)
    return buf.read()

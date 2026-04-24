"""Lightweight data models for the parsed simulation (dataclasses).

Using dataclasses avoids requiring external dependencies for the MVP.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Part:
    name: str
    node_count: int = 0
    element_count: int = 0
    element_types: List[str] = field(default_factory=list)


@dataclass
class NodeSet:
    name: str
    size: int = 0


@dataclass
class ElementSet:
    name: str
    size: int = 0


@dataclass
class Material:
    name: str
    data_type: str = "elastic"
    properties: Dict[str, Optional[float]] = field(default_factory=dict)


@dataclass
class BoundaryCondition:
    data_type: str
    target: str
    dofs: List[int]
    value: Optional[float]


@dataclass
class Load:
    data_type: str
    target: str
    dof: int
    value: float


@dataclass
class Step:
    name: str
    analysis_type: str


@dataclass
class Simulation:
    model: Dict[str, Any] = field(default_factory=lambda: {"parts": []})
    sets: Dict[str, List[Any]] = field(default_factory=lambda: {"node_sets": [], "element_sets": []})
    materials: List[Material] = field(default_factory=list)
    boundary_conditions: List[BoundaryCondition] = field(default_factory=list)
    loads: List[Load] = field(default_factory=list)
    steps: List[Step] = field(default_factory=list)

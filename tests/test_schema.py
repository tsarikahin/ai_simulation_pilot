from simcopilot.schema.simulation_schema import Simulation


def test_simulation_dataclass():
    sim = Simulation()
    assert hasattr(sim, "model")

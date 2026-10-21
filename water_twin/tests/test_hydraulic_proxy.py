import pytest
from water_twin.src.hydraulic_proxy import Scenario, simulate, run_sweep

def test_no_leak_baseline():
    assert simulate(Scenario()) == simulate(Scenario(leak_m3s=0))

def test_leak_lowers_pressure():
    normal=simulate(Scenario())
    leak=simulate(Scenario(leak_m3s=0.005))
    assert leak['service_pressure_m'] < normal['service_pressure_m']
    assert leak['pipe_a_flow_m3s'] > normal['pipe_a_flow_m3s']

def test_negative_leak_rejected():
    with pytest.raises(ValueError):
        simulate(Scenario(leak_m3s=-0.01))

def test_sweep_writes_six_rows(tmp_path):
    rows=run_sweep(tmp_path/'sweep.csv')
    assert len(rows)==6
    assert (tmp_path/'sweep.csv').exists()

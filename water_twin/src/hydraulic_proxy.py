"""Illustrative, uncalibrated steady-state two-pipe hydraulic proxy (NOT WNTR/EPANET).
Assumes quadratic frictional head loss h=r*q*abs(q) with arbitrary illustrative resistances.
Not field telemetry; run python water_twin/src/hydraulic_proxy.py for a demonstrative sweep.
"""
from dataclasses import dataclass
import csv
from pathlib import Path

@dataclass(frozen=True)
class Scenario:
    leak_m3s: float = 0.0
    upstream_demand_m3s: float = 0.010
    service_demand_m3s: float = 0.012
    source_head_m: float = 110.0
    service_elevation_m: float = 65.0
    r_a: float = 16000.0
    r_b: float = 22000.0

def simulate(s: Scenario) -> dict:
    for key in ('leak_m3s','upstream_demand_m3s','service_demand_m3s','r_a','r_b'):
        if getattr(s,key) < 0: raise ValueError(key+' must be nonnegative')
    q_b=s.service_demand_m3s+s.leak_m3s
    q_a=s.upstream_demand_m3s+q_b
    loss_a=s.r_a*q_a*q_a
    loss_b=s.r_b*q_b*q_b
    return {'pipe_a_flow_m3s':q_a,'pipe_b_flow_m3s':q_b,'service_pressure_m':s.source_head_m-s.service_elevation_m-loss_a-loss_b,'upstream_loss_m':loss_a,'downstream_loss_m':loss_b}

def run_sweep(path='hydraulic_proxy_results.csv'):
    base=simulate(Scenario())
    rows=[]
    for leak in (0,0.001,0.002,0.003,0.004,0.005):
        result=simulate(Scenario(leak_m3s=leak))
        rows.append({'leak_m3s':leak,**result,'pressure_drop_from_baseline_m':base['service_pressure_m']-result['service_pressure_m']})
    with Path(path).open('w',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=rows[0].keys())
        writer.writeheader();writer.writerows(rows)
    return rows

if __name__ == '__main__':
    for row in run_sweep(): print(row)

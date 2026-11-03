"""Two-hour PyPSA/HiGHS smoke test for signed generator spillage.

Run before the 744-hour exchange regression. This isolates solver compatibility
from source-file loading and month-long optimization.
"""
import json
import pypsa

def main():
    n=pypsa.Network()
    n.set_snapshots(["2024-01-01 00:00","2024-01-01 01:00"])
    n.add("Bus","test")
    n.add("Load","demand",bus="test",p_set=[50.0,70.0])
    n.add("Generator","fixed_import",bus="test",p_nom=70.0,
          p_min_pu=[1.0,0.0],p_max_pu=[1.0,0.0],marginal_cost=0.0)
    n.add("Generator","dispatchable",bus="test",p_nom=100.0,marginal_cost=55.0)
    n.add("Generator","unserved",bus="test",p_nom=100.0,marginal_cost=100000.0)
    n.add("Generator","spill",bus="test",p_nom=70.0,
          p_min_pu=-1.0,p_max_pu=0.0,marginal_cost=-1.0)
    status,condition=n.optimize(solver_name="highs")
    print("PyPSA version:",pypsa.__version__)
    print("Solver status:",status,condition)
    if status!="ok" or condition!="optimal":
        raise RuntimeError("Short-horizon HiGHS solve failed")
    g=n.generators_t.p
    actual={
       "first_hour_import_mw":float(g.loc[g.index[0],"fixed_import"]),
       "first_hour_spill_mw":float(g.loc[g.index[0],"spill"]),
       "second_hour_local_mw":float(g.loc[g.index[1],"dispatchable"]),
       "unserved_mwh":float(g["unserved"].sum())
    }
    print(json.dumps(actual,indent=2))
    if abs(actual["first_hour_import_mw"]-70)>1e-5:
        raise AssertionError("Fixed import schedule not respected")
    if abs(actual["first_hour_spill_mw"]+20)>1e-5:
        raise AssertionError("Signed spillage modeling failed")
    if abs(actual["second_hour_local_mw"]-70)>1e-5:
        raise AssertionError("Local dispatch incorrectly calculated")
    if actual["unserved_mwh"]>1e-5:
        raise AssertionError("Unexpected unserved energy")
if __name__=="__main__":
    main()

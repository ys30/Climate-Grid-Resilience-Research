"""Bridge full-calendar PyPSA monthly generation into HY/PS comparison format.

Requires an explicitly identified real-model provenance file; synthetic runs
may be used for interface testing but never certified as historical validation.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

MAP={"hydro":"HY","HY":"HY","pumped_storage":"PS","PS":"PS"}
BAS={"AZPS","BPAT","CISO","SRP"}

def adapt(monthly_csv, provenance_json, output_dir):
    data=pd.read_csv(monthly_csv)
    needed={"ba","technology","period","generation_mwh"}
    if not needed.issubset(data):raise ValueError("Missing full-month PyPSA fields")
    if data.empty or data[list(needed)].isna().any().any():raise ValueError("No complete modeled data")
    provenance=json.loads(Path(provenance_json).read_text())
    if provenance.get("full_month_utc_coverage") is not True:
        raise ValueError("Missing certified full-calendar-hour coverage manifest")
    if not data.ba.isin(BAS).all():raise ValueError("Unexpected model balancing authority")
    if not data.technology.isin(MAP).all():
        raise ValueError("Unknown technology; no implicit mapping to HY or PS")
    data=data.copy()
    data["prime_mover"]=data.technology.map(MAP)
    data["reported_ba"]=data.ba
    if not data.period.astype(str).str.fullmatch(r"2024-(0[1-9]|1[0-2])").all():
        raise ValueError("Expected exact 2024 monthly periods")
    if data.duplicated(["reported_ba","prime_mover","period"]).any():
        raise ValueError("Duplicate mapped BA/prime-mover/month: cannot add technologies implicitly")
    data["modeled_net_generation_mwh"]=pd.to_numeric(data.generation_mwh,errors="raise")
    if not data.modeled_net_generation_mwh.map(lambda x:-float("inf")<float(x)<float("inf")).all():
        raise ValueError("Nonfinite modeled MWh")
    # The model may be a gross generation proxy. Require an explicit
    # net-generation definition before treating comparison errors as meaningful.
    net_verified=provenance.get("modeled_generation_is_net_mwh") is True
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    data[["reported_ba","prime_mover","period","modeled_net_generation_mwh"]].sort_values(
        ["reported_ba","prime_mover","period"]).to_csv(out/"modeled_hy_ps_monthly_for_comparison.csv",index=False)
    result={"modeled_cells":len(data),"modeled_generation_is_net_mwh":net_verified,
            "historical_calibration_certified":False,
            "comparison_eligible":net_verified and provenance.get("historical_inputs_verified") is True,
            "warning":"A synthetic full-month solve is not historic calibration; observed plant inventory, net/gross basis and historic inputs require independent evidence."}
    (out/"model_hy_ps_adapter_manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--monthly",required=True);p.add_argument("--provenance",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(adapt(a.monthly,a.provenance,a.output),indent=2))
if __name__=="__main__":main()

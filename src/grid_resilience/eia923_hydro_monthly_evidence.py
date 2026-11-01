"""Extract observed monthly hydro/PS net generation, without inventing dispatch caps."""
import argparse,json
from pathlib import Path
import pandas as pd

BAS={"AZPS","BPAT","CISO","SRP"}
HYDRO_CODES={"HY","PS"}

def summarize(path,output):
    df=pd.read_csv(path,keep_default_na=False)
    required={"reported_ba","prime_mover","period","net_generation_mwh","negative_records","generator_month_records"}
    if not required.issubset(df.columns):raise ValueError("Missing prime mover audit columns")
    sub=df.loc[df.reported_ba.isin(BAS)&df.prime_mover.isin(HYDRO_CODES)].copy()
    if sub.empty:
        out=Path(output);out.mkdir(parents=True,exist_ok=True)
        report={"data_kind":"EIA-923 Page 4 generator-month extraction",
          "hydro_monthly_evidence_available":False,
          "observed_prime_mover_codes":sorted(df.prime_mover.unique().tolist()),
          "requested_hydro_codes":sorted(HYDRO_CODES),
          "february_2024":[],
          "hydro_values_inferred_or_zero_filled":False,
          "historical_hourly_hydro_availability_calibrated":False,
          "blocked_reason":"Current Page 4 extractor contains no HY/PS rows. Need hydro-specific source coverage before numerical hydro calibration."}
        pd.DataFrame(columns=[*df.columns]).to_csv(out/"hydro_pumped_month_evidence.csv",index=False)
        (out/"hydro_pumped_month_evidence_manifest.json").write_text(json.dumps(report,indent=2)+"\\n")
        return report
    if sub.duplicated(["reported_ba","prime_mover","period"]).any():raise ValueError("Duplicate monthly category")
    sub.net_generation_mwh=pd.to_numeric(sub.net_generation_mwh,errors="raise")
    if not sub.net_generation_mwh.map(lambda x:-float("inf")<x<float("inf")).all():
        raise ValueError("Nonfinite hydro reported generation")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    sub=sub.sort_values(["reported_ba","period","prime_mover"])
    sub.to_csv(out/"hydro_pumped_month_evidence.csv",index=False)
    feb=sub[sub.period=="2024-02"]
    report={"data_kind":"reported EIA-923 monthly net generation, not generation potential or dispatch cap",
        "target_bas":sorted(BAS),"observed_codes":sorted(sub.prime_mover.unique().tolist()),
        "february_2024":feb[["reported_ba","prime_mover","net_generation_mwh","generator_month_records","negative_records"]].to_dict("records"),
        "historical_hourly_hydro_availability_calibrated":False,
        "missing_ba_code_months_not_imputed":True,
        "caution":"HY hydro turbine and PS pumped storage are distinct. Monthly net energy is not plant availability, reservoir balance, or hourly transfer capacity."}
    (out/"hydro_pumped_month_evidence_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    return report
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    print(json.dumps(summarize(a.input,a.output),indent=2))
if __name__=="__main__":main()

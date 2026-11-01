import json
import pandas as pd
from grid_resilience.eia923_hydro_monthly_evidence import summarize

def test_missing_hydro_is_coverage_gap_not_zero(tmp_path):
    source=tmp_path/"prime.csv"
    pd.DataFrame([{"reported_ba":"BPAT","prime_mover":"ST","period":"2024-02","net_generation_mwh":55,"negative_records":0,"generator_month_records":1}]).to_csv(source,index=False)
    report=summarize(source,tmp_path/"out")
    assert report["hydro_monthly_evidence_available"] is False
    assert report["hydro_values_inferred_or_zero_filled"] is False
    assert json.loads((tmp_path/"out"/"hydro_pumped_month_evidence_manifest.json").read_text())==report

def test_hy_ps_are_kept_separate(tmp_path):
    source=tmp_path/"prime.csv"
    pd.DataFrame([{"reported_ba":"BPAT","prime_mover":"HY","period":"2024-02","net_generation_mwh":50,"negative_records":0,"generator_month_records":1},{"reported_ba":"BPAT","prime_mover":"PS","period":"2024-02","net_generation_mwh":-5,"negative_records":1,"generator_month_records":1}]).to_csv(source,index=False)
    report=summarize(source,tmp_path/"out")
    assert len(report["february_2024"])==2
    assert sorted(x["net_generation_mwh"] for x in report["february_2024"])==[-5,50]

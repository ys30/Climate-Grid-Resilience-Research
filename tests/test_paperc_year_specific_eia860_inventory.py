import pandas as pd
import pytest
from grid_resilience.paperc_year_specific_eia860_inventory import compare, extract_year


def test_comparison_retains_annual_candidate_scope():
    a=pd.DataFrame({"ba":["AZPS","BPAT"],"technology":["gas","wind"],
                    "nameplate_capacity_mw":[100.,10.],"generator_rows":[2,1],
                    "source_year":[2023,2023]})
    b=pd.DataFrame({"ba":["AZPS","SRP"],"technology":["gas","wind"],
                    "nameplate_capacity_mw":[110.,30.],"generator_rows":[3,1],
                    "source_year":[2024,2024]})
    out=compare(a,b)
    assert len(out)==3
    assert out.loc[out.ba.eq("AZPS"),"nameplate_difference_mw"].iloc[0]==10
    assert out.loc[out.ba.eq("BPAT"),"yearly_coverage"].iloc[0]=="left_only"
    assert out.loc[out.ba.eq("SRP"),"yearly_coverage"].iloc[0]=="right_only"
    assert not out.estimated_hourly_firm_capacity.any()
    assert not out.previous_frozen_2024_partial_fleet_valid_for_2023.any()


def test_year_mismatch_rejected():
    a=pd.DataFrame({"source_year":[2024],"ba":["AZPS"],"technology":["gas"],
                    "nameplate_capacity_mw":[1]})
    with pytest.raises(ValueError,match="2023 and 2024"):
        compare(a,a)


def test_only_reviewed_annual_vintages_admitted():
    with pytest.raises(ValueError,match="year"):
        extract_year("not-a-file.zip",2025)

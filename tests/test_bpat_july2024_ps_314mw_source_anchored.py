import json
import pytest
from grid_resilience.bpat_july2024_ps_314mw_source_anchored import settings_from_admission

def admission(tmp_path, **changes):
    data={"target_ba":"BPAT","bpat_ps_prime_mover_records":6,
          "bpat_ps_positive_nameplate_records":6,
          "bpat_ps_positive_nameplate_mw":314.0,
          "bpat_ps_exact_generator_storage_sheet_matches":0,
          "physical_ps_672h_dispatch_parameters_admitted":False}
    data.update(changes)
    p=tmp_path/"admission.json"
    p.write_text(json.dumps(data))
    return p

def test_source_capacity_is_not_misrepresented_as_real_mwh(tmp_path):
    x,m=settings_from_admission(admission(tmp_path))
    assert x==((0.,0.,1.),(314.,628.,.80),(314.,1256.,.80),(314.,1256.,.90))
    assert m["physical_ps_672h_dispatch_parameters_admitted"] is False

def test_refuse_missing_eia860_ps_generator_roster(tmp_path):
    with pytest.raises(ValueError,match="six BPAT"):
        settings_from_admission(admission(tmp_path,bpat_ps_prime_mover_records=5))

def test_refuse_unaudited_nameplate(tmp_path):
    with pytest.raises(ValueError,match="six BPAT"):
        settings_from_admission(admission(tmp_path,bpat_ps_positive_nameplate_mw=1000.))

def test_refuse_falsely_complete_storage_sheet(tmp_path):
    with pytest.raises(ValueError,match="six BPAT"):
        settings_from_admission(admission(tmp_path,physical_ps_672h_dispatch_parameters_admitted=True))

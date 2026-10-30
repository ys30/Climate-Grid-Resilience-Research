import pandas as pd
import pytest
from grid_resilience.research_run import fingerprint,run

def test_fingerprint_is_deterministic(tmp_path):
    p=tmp_path/"data.csv"
    p.write_text("a,b\n1,2\n")
    assert len(fingerprint(p))==64
    assert fingerprint(p)==fingerprint(p)

def test_rejects_unsupported_rating_claim(tmp_path):
    paths=[tmp_path/x for x in ("d.csv","w.csv","c.csv","l.csv")]
    pd.DataFrame([{"from_ba":"AZPS","to_ba":"CISO","capacity_mw":20}]).to_csv(paths[3],index=False)
    with pytest.raises(ValueError,match="per-link provenance"):
        run(*paths,output=tmp_path/"out",event_id="E",network_variant="base",
            link_evidence="verified_ratings")

def test_rejects_unknown_evidence_classification(tmp_path):
    with pytest.raises(ValueError,match="classification"):
        run("a","b","c","d",tmp_path/"out","E","base","unspecified")

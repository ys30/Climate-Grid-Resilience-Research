import pandas as pd
import pytest
from grid_resilience.paperc_year_specific_capacity_adapter import adapt


def data(year=2023):
    return pd.DataFrame([{"ba":ba,"technology":tech,"source_year":year,
                          "nameplate_capacity_mw":float(100+i*20+j)}
                         for i,ba in enumerate(("AZPS","BPAT","CISO","SRP"))
                         for j,tech in enumerate(("gas","wind"))])


def test_four_ba_nameplate_source_admitted():
    x=adapt(data(2023),2023)
    assert len(x)==4
    assert set(x.source_year)=={2023}
    assert x.capacity_source.str.contains("NOT_FIRM_MW").all()


def test_wrong_vintage_rejected():
    with pytest.raises(ValueError,match="year"):
        adapt(data(2024),2023)


def test_missing_wind_rejected():
    with pytest.raises(ValueError,match="Missing year-specific"):
        adapt(data().query("not (ba=='AZPS' and technology=='wind')"),2023)


def test_duplicate_source_rejected():
    with pytest.raises(ValueError,match="Duplicate"):
        adapt(pd.concat([data(),data().iloc[:1]],ignore_index=True),2023)


def test_zero_nameplate_rejected():
    d=data();d.loc[0,"nameplate_capacity_mw"]=0
    with pytest.raises(ValueError,match="Nonpositive"):
        adapt(d,2023)

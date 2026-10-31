"""Smoke checks for independent meteorological input provenance and coverage."""
import tempfile
from pathlib import Path
import pandas as pd
from grid_resilience.independent_weather_gate import validate
with tempfile.TemporaryDirectory() as directory:
    root=Path(directory)
    rows=[{"timestamp":t.isoformat(),"ba":ba,"wind_speed_ms":5.,
           "weather_source":"synthetic_unit_test","source_variable":"synthetic_10m_wind"}
          for t in pd.date_range("2024-02-01T00:00:00Z",periods=2,freq="h")
          for ba in ("AZPS","BPAT","CISO","SRP")]
    p=root/"synthetic_weather.csv";pd.DataFrame(rows).to_csv(p,index=False)
    out=validate(p,root/"out",hours=2)
    assert out["weather_rows"]==8
    bad=root/"missing_weather.csv";pd.DataFrame(rows[:-1]).to_csv(bad,index=False)
    try:validate(bad,root/"bad",hours=2)
    except ValueError:pass
    else:raise AssertionError("Missing BA-hour not rejected")
    bad2=root/"eia930_generation.csv";pd.DataFrame(rows).to_csv(bad2,index=False)
    try:validate(bad2,root/"bad2",hours=2)
    except ValueError:pass
    else:raise AssertionError("Power-generation provenance not rejected")
print("Independent weather input gate smoke tests passed")

"""EIA-930 UTC hour-ending to model interval-start alignment.

EIA explicitly publishes integrated BA hourly values at *end* of interval.
For a model UTC start-hour t, request the EIA hour-ending period t+1h
and assign the result to t. Never infer or fill a missing boundary hour.
"""
import pandas as pd


def hour_ending_to_start(series):
    """Return UTC-aware interval-start timestamps from EIA hour-ending labels."""
    stamps=pd.to_datetime(series,utc=True,errors="raise")
    if stamps.isna().any():
        raise ValueError("Missing EIA hour-ending timestamp")
    return stamps-pd.Timedelta(hours=1)


def api_hour_ending_bounds(start, end_exclusive):
    """Inclusive API bounds for requested model start hours [start,end)."""
    st=pd.Timestamp(start)
    en=pd.Timestamp(end_exclusive)
    if st.tzinfo is None or en.tzinfo is None:
        raise ValueError("UTC timezone-aware bounds required")
    st=st.tz_convert("UTC")
    en=en.tz_convert("UTC")
    if en<=st or any((x.minute or x.second or x.microsecond) for x in (st,en)):
        raise ValueError("Nonempty whole-hour interval required")
    # The final model interval begins at end_exclusive - 1h; its EIA label
    # is end_exclusive, an inclusive API endpoint.
    return st+pd.Timedelta(hours=1),en

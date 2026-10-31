"""Classify wind-weather proxy evidence without overstating BA representativeness."""
import argparse,json
from pathlib import Path

def report(comparison_path,output):
    metrics=json.loads(Path(comparison_path).read_text())
    hours=int(metrics["hours"])
    r=float(metrics["pearson_hourly_correlation"])
    mean_proxy=float(metrics["era5_city_point_mean_idealized_wind_proxy"])
    mean_observed=float(metrics["eia930_reported_wind_mean_to_eia860_nameplate"])
    if hours!=696 or not -1<=r<=1 or not 0<=mean_proxy<=1:
        raise ValueError("Invalid comparison metrics")
    result={
      "dataset":"BPAT February 2024 696-hour point-proxy diagnostic",
      "pearson_r":r,"point_proxy_mean":mean_proxy,
      "observed_output_to_nameplate_mean":mean_observed,
      "absolute_mean_gap_percentage_points":100*abs(mean_proxy-mean_observed),
      "status":"illustrative_only_not_ba_weather_validated",
      "point_weather_represents_all_wind_farms":False,
      "historical_reliability_calibrated":False,
      "required_next_evidence":[
        "EIA-860 linked wind-generator locations and rated capacity",
        "Independent meteorological weather sampling at actual wind-farm sites",
        "Installed-capacity-weighted hourly meteorology and power curves",
        "Holdout checks against observed EIA-930 BA wind output",
        "Curtailment and plant-fleet coverage limitations assessed"],
      "note":"Pearson correlation is diagnostic and not alone a calibration criterion; BA reported net generation is not pure weather potential."
    }
    target=Path(output);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,indent=2)+"\n")
    return result
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--comparison",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();print(json.dumps(report(a.comparison,a.output),indent=2))
if __name__=="__main__":main()

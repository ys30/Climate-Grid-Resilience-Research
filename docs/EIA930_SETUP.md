# EIA-930 historical demand workflow setup

The research repository uses a separate GitHub Actions secret. Repository secrets are not inherited from Project B or portfolio repositories.

1. Open [Research repository Actions secrets](https://github.com/ys30/Climate-Grid-Resilience-Research/settings/secrets/actions).
2. Add repository secret **EIA_API_KEY** with your existing EIA API key. Never place the key in code, issues, commit messages, or Actions logs.
3. Open [EIA-930 live observed demand audit](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/workflows/eia930-live-demand.yml) and select **Run workflow** after saving the secret.

This workflow checks **CISO, AZPS, BPAT and SRP**, UTC **2024-07-01 00:00 through 2024-07-07 23:00**, requiring **672 BA-hour observations** and rejecting duplicates, missing hours and nonpositive demand. It writes an observed-data CSV and source manifest to the downloadable Actions artifact.

An initial workflow run [41096821914](https://github.com/ys30/Climate-Grid-Resilience-Research/actions/runs/41096821914) stopped at the missing-secret check; **no real data were downloaded** in that run.

The downloaded demand will not, on its own, constitute calibration. ERA5 weather, EIA-860 capacity, qualified EIA-923 observed dispatch and defensible transfer-limit assumptions still need reconciliation and separate validation before publishing new physical grid results.

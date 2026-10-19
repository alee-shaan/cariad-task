# Notes
**Run:** `pip install pandas pytest` then `pytest -q` and `python solution.py`.

- **Grid:** 0.1 s steps counted in whole tenths (no float drift); 0.2 s to 29.9 s for drive.csv.
- **Speed:** raw + grid times merged, then `interpolate(method="index")` (uses real time gaps); fills the 14.0–14.5 s dropout. Values there are estimates, not measurements.
- **Brake:** forward-filled from the last known raw value, so it stays 0/1.
- **Event bounds:** `start_s`/`end_s` are the first/last *pressed* grid samples, `duration_s = end_s - start_s`. A one-sample press has duration 0. Presses of exactly `min_duration_s` are kept.
- **Result:** two events (5.1–8.0 s, drop ≈19 km/h; 20.1–22.5 s, drop ≈28 km/h); the 12.1 s tap is ignored.
- **With more time:** flag events that overlap interpolated gaps (and cap max gap length), handle presses still active at the end of the log, add input validation and type hints/CI (pytest + ruff on GitHub Actions).
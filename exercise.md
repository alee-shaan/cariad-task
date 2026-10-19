# Practical exercise: braking events from a drive log

**Time:** about 60-90 minutes, at home before the interview. Python 3.10+, `pandas`, `pytest`, or any other programming language. Any AI assistant is allowed, but you must be able to explain your code.

## Context
`drive.csv` is a 30-second drive recorded at roughly 10 Hz. The timestamps are slightly irregular, and the speed signal has a short dropout.

| column | meaning |
|---|---|
| `timestamp_s` | time in seconds |
| `speed_kmh` | vehicle speed (can be NaN) |
| `brake_pressed` | 1 while the brake pedal is pressed, else 0 |

## Task
The Python starter code is supplied as `solution.py.txt` because of email attachment restrictions. If using Python, rename it to `solution.py` before starting. For another programming language, create an equivalent source file and use an equivalent table structure wherever a DataFrame is mentioned.

Implement the two functions in `solution.py`:

1. `resample_signals(df)`: takes the raw `drive.csv` data and returns a DataFrame with `speed_kmh` and `brake_pressed` on a regular **10 Hz grid** (0.1 s steps).
   - The index is the time in seconds as floats (0.2, 0.3, …), from the first 0.1 s step at or after the first timestamp to the last 0.1 s step at or before the last timestamp.
   - Interpolate `speed_kmh` linearly over time, including the dropout.
   - `brake_pressed` must stay 0/1. Use the last known value, not an interpolated one.
2. `find_braking_events(df, min_duration_s=0.5)`: takes the output of `resample_signals` and returns a DataFrame with one row per braking event.
   - Columns: `start_s`, `end_s`, `duration_s`, `speed_drop_kmh` (speed at start minus speed at end). Keep these columns even when there are no events.
   - Ignore presses shorter than `min_duration_s`.

Then write **2-3 pytest tests** in `test_solution.py`. Use small hand-made DataFrames, not only `drive.csv`. Cover at least: a short press that is ignored, and the NaN gap.

### What does "interpolate" mean for `speed_kmh`?
Interpolation estimates a speed value between two known measurements.

| Time | Recorded speed |
|---|---|
| 1.0 s | 50 km/h |
| 1.1 s | missing |
| 1.2 s | 40 km/h |

With **linear interpolation**, we assume speed changes steadily between the known values. Since 1.1 s is halfway between them, we estimate **45 km/h**. For other timestamps, the estimate depends on their relative position in time between the two known measurements.

In this exercise, interpolation fills both missing speed measurements (the sensor dropout) and new timestamps introduced by the regular 0.1 s grid.

These are **estimates, not actual measurements**. Interpolation does not recover what really happened during a gap. It applies to speed here, not to the 0/1 brake state.

## Deliverable
Push your solution to a public GitHub repository and reply to the invitation email with the link before the interview. If you prefer a private repository, ask us which GitHub accounts to invite. ZIP submissions are not accepted. Add a short `NOTES.md` (max 10 lines) with your assumptions and what you would improve with more time.

## Notes
- Don't over-engineer. Clear, readable code matters more than performance.
- If something in the task is unclear, make a reasonable assumption and note it in `NOTES.md`; that is part of the exercise.

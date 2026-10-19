import math

import pandas as pd

EVENT_COLUMNS = ["start_s", "end_s", "duration_s", "speed_drop_kmh"]


def resample_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Return df on a regular 10 Hz grid (see exercise.md)."""
    raw = df.sort_values("timestamp_s").set_index("timestamp_s")

    # Build a grid of time steps from the first to the last timestamp.
    first_step = math.ceil(round(raw.index.min() * 10, 6))
    last_step = math.floor(round(raw.index.max() * 10, 6))
    grid = [round(step / 10, 1) for step in range(first_step, last_step + 1)]

    # 2. Put raw times and grid times together in one sorted table.
    all_times = sorted(set(raw.index) | set(grid))
    combined = raw.reindex(all_times)
    print(combined)

    # 3. Speed: straight line between known values, using real time distances.
    combined["speed_kmh"] = combined["speed_kmh"].interpolate(method="index")

    # 4. Brake: copy the last known value forward, so it stays 0 or 1.
    combined["brake_pressed"] = combined["brake_pressed"].ffill().astype(int)

    # 5. Keep only the grid rows.
    result = combined.loc[grid]
    result.index.name = "timestamp_s"
    return result


def find_braking_events(df: pd.DataFrame, min_duration_s: float = 0.5) -> pd.DataFrame:
    """Return one row per braking event (see exercise.md)."""
    times = df.index.tolist()
    brake = df["brake_pressed"].tolist()
    speed = df["speed_kmh"].tolist()

    events = []
    start = None  # position where the current press started

    for i in range(len(brake)):
        # Press starts
        if brake[i] == 1 and start is None:
            start = i

        # Press ends: this sample is pressed, and the next one is not (or there is no next one)
        is_last_pressed = brake[i] == 1 and (i == len(brake) - 1 or brake[i + 1] == 0)
        if is_last_pressed:
            duration = round(times[i] - times[start], 6)  # round away float noise like 0.4999999
            if duration >= min_duration_s:
                events.append({
                    "start_s": times[start],
                    "end_s": times[i],
                    "duration_s": duration,
                    "speed_drop_kmh": speed[start] - speed[i],
                })
            start = None

    # columns= keeps the 4 columns even when there are no events
    return pd.DataFrame(events, columns=EVENT_COLUMNS)


if __name__ == "__main__":
    raw = pd.read_csv("drive.csv")
    print(find_braking_events(resample_signals(raw)))
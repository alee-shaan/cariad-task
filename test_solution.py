import pandas as pd
import pytest

from solution import EVENT_COLUMNS, find_braking_events, resample_signals


def make_raw(times, speeds, brakes):
    return pd.DataFrame(
        {"timestamp_s": times, "speed_kmh": speeds, "brake_pressed": brakes}
    )


def make_grid(speeds, brakes, start_s=0.0):
    index = [round(start_s + i * 0.1, 1) for i in range(len(speeds))]
    return pd.DataFrame(
        {"speed_kmh": speeds, "brake_pressed": brakes},
        index=pd.Index(index, name="timestamp_s"),
    )


def test_nan_gap_is_interpolated_linearly_and_brake_is_held():
    # Irregular timestamps, speed dropout between 0.15 s and 0.45 s.
    raw = make_raw(
        times=[0.05, 0.15, 0.25, 0.35, 0.45],
        speeds=[50.0, 50.0, None, None, 20.0],
        brakes=[0, 1, 1, 0, 0],
    )

    out = resample_signals(raw)

    # Grid: first 0.1 step >= 0.05 to last step <= 0.45.
    assert list(out.index) == [0.1, 0.2, 0.3, 0.4]
    # 0.15 -> 50, 0.45 -> 20: 10 km/h per 0.1 s; 0.1 lies between 0.05 and 0.15.
    assert out["speed_kmh"].tolist() == pytest.approx([50.0, 45.0, 35.0, 25.0])
    assert not out["speed_kmh"].isna().any()
    # Brake uses the last known value and stays 0/1.
    assert out["brake_pressed"].tolist() == [0, 1, 1, 0]


def test_short_press_is_ignored_long_press_is_kept():
    brakes = [0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0]   # 0.1 s press, then 0.5 s press
    speeds = [50, 50, 50, 50, 50, 50, 48, 46, 44, 42, 40, 40]

    events = find_braking_events(make_grid(speeds, brakes), min_duration_s=0.5)

    assert len(events) == 1
    event = events.iloc[0]
    assert event["start_s"] == pytest.approx(0.5)
    assert event["end_s"] == pytest.approx(1.0)
    assert event["duration_s"] == pytest.approx(0.5)
    assert event["speed_drop_kmh"] == pytest.approx(10.0)


def test_no_events_keeps_columns():
    events = find_braking_events(make_grid([50, 50, 50], [0, 0, 0]))

    assert events.empty
    assert list(events.columns) == EVENT_COLUMNS


def test_drive_csv_finds_the_two_real_braking_events():
    events = find_braking_events(resample_signals(pd.read_csv("drive.csv")))

    assert events["start_s"].tolist() == pytest.approx([5.1, 20.1])
    assert events["end_s"].tolist() == pytest.approx([8.0, 22.5])
    assert (events["speed_drop_kmh"] > 0).all()

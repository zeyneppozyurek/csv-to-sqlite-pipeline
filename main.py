from pathlib import Path
import json
BASE = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
OUT = BASE / "outputs"
OUT.mkdir(exist_ok=True)
import sqlite3
import pandas as pd
rows = [
["s01", "2026-01-01T10:00:00Z", "training", 120, 40],
["s02", "2026-01-01T10:05:00Z", "exploration", 250, 60],
["s03", "2026-01-01T10:10:00Z", "training", 180, 35],
["s04", "bad-date", "training", 150, 20],
["s05", "2026-01-01T10:20:00Z", "exploration", -10, 30],
["s06", "2026-01-01T10:25:00Z", "training", "oops", 25],
["s07", "2026-01-01T10:30:00Z", "exploration", 90, None],
["s01", "2026-01-01T10:00:00Z", "training", 120, 40],
["s08", "2026-01-01T10:35:00Z", "exploration", 110, 50]]
columns = ["session_id", "timestamp", "scenario", "duration_seconds", "latency_ms"]
pd.DataFrame(rows, columns=columns).to_csv(OUT / "input_sessions.csv", index=False)
raw = pd.read_csv(OUT / "input_sessions.csv")
frame = raw.drop_duplicates().copy()
frame["timestamp"] = pd.to_datetime(frame.timestamp, errors="coerce", utc=True)
for column in ["duration_seconds", "latency_ms"]:
    frame[column] = pd.to_numeric(frame[column], errors="coerce")
def reasons(row):
    problems = []
    if pd.isna(row.session_id) or not str(row.session_id).strip(): problems.append("missing_id")
    if pd.isna(row.timestamp): problems.append("invalid_timestamp")
    if pd.isna(row.scenario) or row.scenario not in {"training", "exploration"}: problems.append("invalid_scenario")
    if pd.isna(row.duration_seconds) or row.duration_seconds <= 0: problems.append("invalid_duration")
    if pd.isna(row.latency_ms) or row.latency_ms < 0: problems.append("invalid_latency")
    return "|".join(problems)
frame["rejection_reason"] = frame.apply(reasons, axis=1)
rejected = frame[frame.rejection_reason != ""]
valid = frame[frame.rejection_reason == ""].copy()
assert valid.session_id.is_unique, "Conflicting session IDs must be resolved before loading"
valid["timestamp"] = valid.timestamp.astype(str)
rejected.to_csv(OUT / "rejected_rows.csv", index=False)
valid[columns].to_csv(OUT / "validated_rows.csv", index=False)
with sqlite3.connect(OUT / "sessions.sqlite") as con:
    con.execute("CREATE TABLE IF NOT EXISTS sessions (session_id TEXT PRIMARY KEY, timestamp TEXT NOT NULL, scenario TEXT NOT NULL, duration_seconds REAL CHECK(duration_seconds > 0), latency_ms REAL CHECK(latency_ms >= 0))")
    query = "INSERT OR IGNORE INTO sessions VALUES (?, ?, ?, ?, ?)"
    records = list(valid[columns].itertuples(index=False, name=None))
    con.executemany(query, records)
    first_count = con.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    con.executemany(query, records)
    second_count = con.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    assert first_count == second_count == len(valid)
    summary = pd.read_sql_query("SELECT scenario, COUNT(*) AS sessions, AVG(duration_seconds) AS mean_duration, AVG(latency_ms) AS mean_latency FROM sessions GROUP BY scenario", con)
summary.to_csv(OUT / "sql_summary.csv", index=False)
metrics = {"input_rows": len(raw), "exact_duplicates_removed": len(raw)-len(frame), "rejected_rows": len(rejected), "valid_rows": len(valid), "database_rows": second_count, "repeat_load_idempotent": first_count == second_count}
(OUT / "metrics.json").write_text(json.dumps(metrics, indent=2))
print(json.dumps(metrics, indent=2))

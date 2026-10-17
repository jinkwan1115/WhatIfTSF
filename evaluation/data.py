"""Load evaluation data and model inputs."""

import csv
import hashlib
import json
import math
from pathlib import Path

from .relations import DOMAINS, validate_relations


def numeric_series(value, label, length=None):
    if isinstance(value, str):
        value = json.loads(value)
    if (not isinstance(value, list) or not value
            or any(type(x) not in (int, float) or not math.isfinite(x) for x in value)
            or (length is not None and len(value) != length)):
        raise ValueError(f"{label}: expected {length or 'a nonempty list of'} finite numbers")
    return value


def read_rows(path, columns, id_column="id"):
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if not set(columns) <= set(reader.fieldnames or []):
            raise ValueError(f"{path}: required columns: {columns}")
        rows = [{column: row[column] for column in columns} for row in reader]
    ids = [row[id_column] for row in rows]
    if (len(ids) != len(set(ids)) or any(not key for key in ids)
            or any(None in row.values() for row in rows)):
        raise ValueError(f"{path}: duplicate/empty IDs or malformed rows")
    return rows


def load_benchmark(data_dir, domains=DOMAINS, limit=None):
    """Load cases and reuse predictions for identical inputs."""
    if not domains or len(set(domains)) != len(domains) or set(domains) - set(DOMAINS):
        raise ValueError(f"Choose distinct domains from {DOMAINS}")
    if limit is not None and limit < 1:
        raise ValueError("limit must be positive")
    benchmark = {"requests": {}, "cases": {}}
    root = Path(data_dir)
    for domain in domains:
        folder = root / domain
        background = (folder / "domain_background.txt").read_text(encoding="utf-8").strip()
        factual_dir = folder / "factual_scenarios"
        series = read_rows(factual_dir / "time_series.csv", ("id", "history", "observed_future"))
        scenarios = read_rows(factual_dir / "factual_scenarios.csv", ("id", "scenario"))
        texts = {row["id"]: row["scenario"] for row in scenarios}
        horizon = len(numeric_series(series[0]["observed_future"], domain))

        def request(history, scenario=None):
            values = numeric_series(history, f"{domain} history")
            inputs = {"history": values, "background": background,
                      "scenario": scenario, "horizon": horizon}
            digest = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
            key = f"{domain}/{digest}"
            benchmark["requests"][key] = inputs
            return key

        cases = {"factual": [], "relational": [], "grounded": []}
        benchmark["cases"][domain] = cases
        for row in series[:limit]:
            cases["factual"].append({
                "id": row["id"], "neutral": request(row["history"]),
                "scenario": request(row["history"], texts[row["id"]]),
                "observed_future": numeric_series(row["observed_future"], domain, horizon),
            })

        relational_dir = folder / "relational_comparison_sets"
        alternatives = read_rows(relational_dir / "alternatives.csv", ("ID", "scenario"), "ID")
        irrelevant = read_rows(relational_dir / "irrelevant.csv", ("ID", "scenario"), "ID")
        validate_relations(domain, [row["ID"] for row in alternatives])
        anchors = read_rows(relational_dir / "time_series.csv", ("id", "history"))
        for row in anchors[:limit]:
            cases["relational"].append({
                "id": row["id"], "neutral": request(row["history"]),
                "alternatives": {s["ID"]: request(row["history"], s["scenario"]) for s in alternatives},
                "irrelevant": {s["ID"]: request(row["history"], s["scenario"]) for s in irrelevant},
            })

        paths = sorted((folder / "grounded_sets").glob("grounded_set_*.csv"))
        for path in paths[:limit]:
            columns = ("role", "id", "history", "observed_future", "scenario")
            rows = read_rows(path, columns)
            anchors = [row for row in rows if row["role"] == "anchor"]
            matches = [row for row in rows if row["role"] == "matched_case"]
            anchor = anchors[0]

            cases["grounded"].append({
                "id": path.stem, "neutral": request(anchor["history"]),
                "scenario": request(anchor["history"], anchor["scenario"]),
                "matches": [{
                    "id": row["id"], "neutral": request(row["history"]),
                    "observed_future": numeric_series(row["observed_future"], str(path), horizon),
                } for row in matches],
            })
    return benchmark

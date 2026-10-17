"""WIT comparison metrics (paper v2, Section 4 and Appendix D)."""

import math
from statistics import fmean

from .relations import get_relations

TOLERANCES = {"energy": 0.01, "economy": 0.02, "politics": 0.10}
CATEGORIES = ("direction", "contrast", "intensity", "restraint")


def _mean(values):
    return fmean(values) if values and all(value is not None for value in values) else None


def _gain(error, baseline):
    return 100 * (1 - error / baseline) if baseline not in (None, 0) else None


def _finite_number(value):
    try:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    except OverflowError:
        return False


def _series(values, horizon, label):
    if not isinstance(values, list) or len(values) != horizon:
        raise ValueError(f"{label}: expected a list of {horizon} forecast values")
    if not all(_finite_number(value) for value in values):
        raise ValueError(f"{label}: values must be finite numbers, excluding booleans")
    return values


def _difference(left, right):
    if len(left) != len(right) or not left:
        raise ValueError("Compared paths must have the same nonzero horizon")
    return [a - b for a, b in zip(left, right)]


def _mae(left, right):
    return fmean(abs(value) for value in _difference(left, right))


def _mse(left, right):
    return fmean(value ** 2 for value in _difference(left, right))


def _score(outcomes):
    return {"passed": sum(outcomes), "total": len(outcomes),
            "SLA": 100 * fmean(outcomes) if outcomes else None}


def _restraint(changes, tolerance):
    return {**_score([change <= tolerance for change in changes]),
            "mean_absolute_change": _mean(changes)}


def _aggregate_scores(scores):
    eligible = [score for score in scores if score["total"]]
    return {"passed": sum(score["passed"] for score in eligible),
            "total": sum(score["total"] for score in eligible),
            "anchors": len(eligible), "SLA": _mean([score["SLA"] for score in eligible])}


def evaluate(benchmark: dict, predictions: dict[str, list[float]],
             restraint_tolerance: float | None = None) -> dict:
    """Return per-domain metrics and per-case details."""
    requests = benchmark["requests"]
    if not isinstance(predictions, dict):
        raise ValueError("Predictions must map request IDs to forecast lists")
    missing, extra = requests.keys() - predictions.keys(), predictions.keys() - requests.keys()
    if missing or extra:
        raise ValueError(f"Prediction IDs mismatch: missing={sorted(missing)!r}, extra={sorted(extra)!r}")
    for request_id, request in requests.items():
        horizon = request["horizon"]
        if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon <= 0:
            raise ValueError(f"{request_id}: horizon must be a positive integer")
        _series(predictions[request_id], horizon, request_id)
    if restraint_tolerance is not None and (
        not _finite_number(restraint_tolerance) or restraint_tolerance < 0
    ):
        raise ValueError("Restraint tolerance must be a finite nonnegative number")

    domains = {}
    for domain, cases in benchmark["cases"].items():
        factual = []
        for case in cases.get("factual", []):
            neutral, scenario = predictions[case["neutral"]], predictions[case["scenario"]]
            observed = _series(case["observed_future"], len(neutral), case["id"])
            neutral_mse, scenario_mse = _mse(neutral, observed), _mse(scenario, observed)
            factual.append({"id": case["id"], "neutral_mse": neutral_mse,
                            "scenario_mse": scenario_mse, "win": scenario_mse < neutral_mse})
        factual_error = _mean([row["scenario_mse"] for row in factual])
        neutral_error = _mean([row["neutral_mse"] for row in factual])
        factual_summary = {
            "count": len(factual), "FFE": factual_error, "neutral_mse": neutral_error,
            "FSG": _gain(factual_error, neutral_error),
            "CWR": 100 * fmean(row["win"] for row in factual) if factual else None,
            "details": factual,
        }

        eta = TOLERANCES[domain]
        tau = eta if restraint_tolerance is None else restraint_tolerance
        relational = []
        for case in cases.get("relational", []):
            rules = get_relations(domain)
            neutral = predictions[case["neutral"]]
            revisions = {sid: fmean(_difference(predictions[rid], neutral))
                         for sid, rid in case["alternatives"].items()}
            case_outcomes = {
                "direction": [sign * revisions[sid] > eta for sid, sign in rules["direction"]
                              if sid in revisions],
                "contrast": [revisions[up] - revisions[down] > eta for up, down in rules["contrast"]
                             if up in revisions and down in revisions],
                "intensity": [sign * (revisions[strong] - revisions[weak]) > eta
                              for weak, strong, sign in rules["intensity"]
                              if weak in revisions and strong in revisions],
            }
            restraint_details = [{"id": sid, "mean_absolute_change": _mae(predictions[rid], neutral)}
                                 for sid, rid in case["irrelevant"].items()]
            for row in restraint_details:
                row["passed"] = row["mean_absolute_change"] <= tau
            case_changes = [row["mean_absolute_change"] for row in restraint_details]
            detail = {"id": case["id"], **{kind: _score(values) for kind, values in case_outcomes.items()},
                      "restraint": {**_restraint(case_changes, tau), "details": restraint_details}}
            relational.append(detail)
        relational_summary = {kind: _aggregate_scores([row[kind] for row in relational])
                              for kind in CATEGORIES}
        relational_summary["restraint"]["mean_absolute_change"] = _mean([
            row["restraint"]["mean_absolute_change"] for row in relational if row["restraint"]["total"]
        ])
        relational_summary.update(
            SLA=_mean([relational_summary[kind]["SLA"] for kind in CATEGORIES]),
            eta=eta, tau=tau, details=relational,
        )

        grounded = []
        for case in cases.get("grounded", []):
            revision = _difference(predictions[case["scenario"]], predictions[case["neutral"]])
            if not case["matches"]:
                raise ValueError(f"{case['id']}: grounded sets require at least one matched case")
            matches = []
            for match in case["matches"]:
                matched_neutral = predictions[match["neutral"]]
                observed = _series(match["observed_future"], len(matched_neutral), match["id"])
                residual = _difference(observed, matched_neutral)
                matches.append({"id": match["id"],
                                "revision_mse": _mse(revision, residual),
                                "neutral_mse": fmean(value ** 2 for value in residual)})
            detail = {"id": case["id"], "matches": matches}
            for metric in ("revision_mse", "neutral_mse"):
                detail[metric] = fmean(row[metric] for row in matches)
            grounded.append(detail)
        grounded_error = _mean([row["revision_mse"] for row in grounded])
        grounded_baseline = _mean([row["neutral_mse"] for row in grounded])
        grounded_summary = {
            "count": len(grounded), "revision_mse": grounded_error, "neutral_mse": grounded_baseline,
            "GCE": math.sqrt(grounded_error) if grounded_error is not None else None,
            "GSG": _gain(grounded_error, grounded_baseline), "details": grounded,
        }
        domains[domain] = {"factual": factual_summary, "relational": relational_summary,
                           "grounded": grounded_summary}
    overall = {
        "factual": {metric: _mean([result["factual"][metric] for result in domains.values()
                                   if result["factual"]["count"]]) for metric in ("FSG", "CWR")},
        "relational": {
            kind: {"SLA": _mean([result["relational"][kind]["SLA"] for result in domains.values()
                                 if result["relational"][kind]["anchors"]])} for kind in CATEGORIES
        },
        "grounded": {"GSG": _mean([result["grounded"]["GSG"] for result in domains.values()
                                    if result["grounded"]["count"]])},
    }
    overall["relational"]["SLA"] = _mean([
        result["relational"]["SLA"] for result in domains.values() if result["relational"]["details"]
    ])
    return {"domains": domains, "overall": overall}

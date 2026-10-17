"""Domain-specific comparison rules."""

from collections import Counter
from collections.abc import Iterable
from typing import TypedDict


class Relations(TypedDict):
    direction: list[tuple[str, int]]
    contrast: list[tuple[str, str]]
    intensity: list[tuple[str, str, int]]


_ADJACENT_THREE = (("1", "2"), ("2", "3"))
_NUMERIC_GRID = (("1", "2"), ("3", "4"), ("1", "3"), ("2", "4"))
_LETTER_GRID = (("a", "b"), ("c", "d"), ("a", "c"), ("b", "d"))

# Each entry specifies (group, matched P/M suffixes, weak-to-strong edges).
# A grid intentionally has only its four edges, with no diagonal comparisons.
_GROUPS = {
    "energy": (
        ("E-W", ("1", "2", "3"), _ADJACENT_THREE),
        ("E-PR", ("a", "b"), (("a", "b"),)),
        ("E-PI", ("1", "2"), (("1", "2"),)),
        ("E-ST", ("1", "2"), (("1", "2"),)),
        ("E-LN", ("1", "2"), (("1", "2"),)),
        ("E-FS", ("1", "2", "3", "4"), _NUMERIC_GRID),
    ),
    "economy": (
        ("M-IR", ("1", "2", "3"), _ADJACENT_THREE),
        ("M-EC", ("1", "2", "3"), _ADJACENT_THREE),
        ("M-RI", ("1", "2", "3"), _ADJACENT_THREE),
        ("M-CF", ("1", "2", "3"), _ADJACENT_THREE),
    ),
    "politics": (
        ("P-EC", ("a", "b", "c", "d"), _LETTER_GRID),
        ("P-GV", ("a", "b", "c", "d"), _LETTER_GRID),
        ("P-LD", ("U", "A"), ()),
        ("P-PO", ("1", "2"), (("1", "2"),)),
    ),
}
_DIRECTION_ONLY = {
    "politics": (("P-CO-M1", -1), ("P-CO-M2", -1), ("P-CO-M3", -1)),
}

DOMAINS = tuple(_GROUPS)


def get_relations(domain: str) -> Relations:
    """Return direction, contrast, and intensity rules."""
    if domain not in _GROUPS:
        raise ValueError(f"Unknown domain {domain!r}; expected one of {', '.join(DOMAINS)}")

    rules: Relations = {"direction": [], "contrast": [], "intensity": []}
    for group, suffixes, edges in _GROUPS[domain]:
        rules["contrast"].extend(
            (f"{group}-P{suffix}", f"{group}-M{suffix}") for suffix in suffixes
        )
        for polarity, sign in (("P", 1), ("M", -1)):
            rules["direction"].extend(
                (f"{group}-{polarity}{suffix}", sign) for suffix in suffixes
            )
            rules["intensity"].extend(
                (f"{group}-{polarity}{weak}", f"{group}-{polarity}{strong}", sign)
                for weak, strong in edges
            )
    rules["direction"].extend(_DIRECTION_ONLY.get(domain, ()))
    return rules


def validate_relations(domain: str, scenario_ids: Iterable[str]) -> None:
    """Check scenario IDs against the configured rules."""
    rules = get_relations(domain)
    counts = Counter(list(scenario_ids))
    duplicates = sorted(scenario_id for scenario_id, count in counts.items() if count > 1)
    if duplicates:
        raise ValueError(f"{domain}: duplicate scenario IDs: {', '.join(duplicates)}")

    directions = dict(rules["direction"])
    missing = sorted(directions.keys() - counts.keys())
    extra = sorted(counts.keys() - directions.keys())
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing IDs: {', '.join(missing)}")
        if extra:
            details.append(f"unexpected IDs: {', '.join(extra)}")
        raise ValueError(f"{domain}: " + "; ".join(details))


from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


ALL_2D = [f"{i:02d}" for i in range(100)]


def normalize_2d(value) -> str:
    """Convert a valid lottery 2-digit value to text, preserving leading zero."""
    if pd.isna(value):
        return ""
    s = str(value).strip()
    if s.endswith(".0"):
        s = s[:-2]
    s = "".join(ch for ch in s if ch.isdigit())
    if not s:
        return ""
    if len(s) == 1:
        return f"0{s}"
    if len(s) == 2:
        return s
    return ""


def frequency_scores(history: pd.Series) -> Dict[str, float]:
    counts = history.value_counts().reindex(ALL_2D, fill_value=0)
    if counts.max() == counts.min():
        return {k: 0.0 for k in ALL_2D}
    scores = (counts - counts.min()) / (counts.max() - counts.min())
    return scores.to_dict()


def cold_scores(history: pd.Series) -> Dict[str, float]:
    fs = frequency_scores(history)
    return {k: 1.0 - v for k, v in fs.items()}


def gap_scores(history: pd.Series) -> Dict[str, float]:
    """Overdue score by current gap divided by average gap."""
    hist = list(history)
    n = len(hist)
    result = {}
    ratios = []
    for num in ALL_2D:
        idxs = [i for i, x in enumerate(hist) if x == num]
        if not idxs:
            current_gap = n
            avg_gap = n
        else:
            current_gap = n - 1 - idxs[-1]
            if len(idxs) >= 2:
                gaps = np.diff(idxs)
                avg_gap = float(np.mean(gaps))
            else:
                avg_gap = max(1.0, n / 2)
        ratio = current_gap / max(avg_gap, 1.0)
        result[num] = ratio
        ratios.append(ratio)
    min_r, max_r = min(ratios), max(ratios)
    if max_r == min_r:
        return {k: 0.0 for k in ALL_2D}
    return {k: (v - min_r) / (max_r - min_r) for k, v in result.items()}


def recent_trend_scores(history: pd.Series, window: int = 12) -> Dict[str, float]:
    recent = history.tail(window)
    return frequency_scores(recent)


def digit_level_scores(history: pd.Series) -> Dict[str, float]:
    tens = [int(x[0]) for x in history if len(x) == 2]
    ones = [int(x[1]) for x in history if len(x) == 2]
    tens_counts = pd.Series(tens).value_counts().reindex(range(10), fill_value=0)
    ones_counts = pd.Series(ones).value_counts().reindex(range(10), fill_value=0)

    def norm(s):
        if s.max() == s.min():
            return s * 0
        return (s - s.min()) / (s.max() - s.min())

    tens_s = norm(tens_counts)
    ones_s = norm(ones_counts)
    scores = {}
    for num in ALL_2D:
        scores[num] = float((tens_s[int(num[0])] + ones_s[int(num[1])]) / 2)
    return scores


def pattern_scores(history: pd.Series) -> Dict[str, float]:
    """Lightweight pattern score: parity, high/low, sum of digits based on recent distribution."""
    if history.empty:
        return {k: 0.0 for k in ALL_2D}

    recent = history.tail(24)
    parity_patterns = [("E" if int(x[0]) % 2 == 0 else "O") + ("E" if int(x[1]) % 2 == 0 else "O") for x in recent]
    highlow_patterns = [("L" if int(x[0]) <= 4 else "H") + ("L" if int(x[1]) <= 4 else "H") for x in recent]
    sums = [int(x[0]) + int(x[1]) for x in recent]

    parity_freq = pd.Series(parity_patterns).value_counts(normalize=True).to_dict()
    highlow_freq = pd.Series(highlow_patterns).value_counts(normalize=True).to_dict()
    sum_mean = float(np.mean(sums))
    sum_std = float(np.std(sums)) or 1.0

    scores = {}
    for num in ALL_2D:
        p = ("E" if int(num[0]) % 2 == 0 else "O") + ("E" if int(num[1]) % 2 == 0 else "O")
        h = ("L" if int(num[0]) <= 4 else "H") + ("L" if int(num[1]) <= 4 else "H")
        s = int(num[0]) + int(num[1])
        sum_score = max(0.0, 1.0 - abs(s - sum_mean) / (3 * sum_std))
        scores[num] = float(0.35 * parity_freq.get(p, 0) + 0.35 * highlow_freq.get(h, 0) + 0.30 * sum_score)
    max_v = max(scores.values()) or 1.0
    return {k: v / max_v for k, v in scores.items()}


def combine_scores(*score_maps: Tuple[Dict[str, float], float]) -> Dict[str, float]:
    result = {k: 0.0 for k in ALL_2D}
    total_weight = sum(w for _, w in score_maps) or 1.0
    for smap, weight in score_maps:
        for k in ALL_2D:
            result[k] += smap.get(k, 0.0) * weight
    return {k: v / total_weight for k, v in result.items()}


def pick_top(scores: Dict[str, float], k: int = 5) -> List[str]:
    return [x for x, _ in sorted(scores.items(), key=lambda item: item[1], reverse=True)[:k]]


def model_predictions(history: pd.Series, model_name: str, k: int = 5, rng=None) -> List[str]:
    rng = rng or np.random.default_rng(42)
    history = pd.Series(history).dropna().map(normalize_2d)
    history = history[history.str.len() == 2]

    if model_name == "Random":
        return list(rng.choice(ALL_2D, size=k, replace=False))

    if history.empty:
        return model_predictions(history, "Random", k, rng)

    if model_name == "Hot Frequency":
        return pick_top(frequency_scores(history), k)

    if model_name == "Cold Frequency":
        return pick_top(cold_scores(history), k)

    if model_name == "Gap Overdue":
        return pick_top(gap_scores(history), k)

    if model_name == "Recent Trend":
        return pick_top(recent_trend_scores(history), k)

    if model_name == "Digit-Level":
        return pick_top(digit_level_scores(history), k)

    if model_name == "Pattern":
        return pick_top(pattern_scores(history), k)

    if model_name == "Hybrid":
        scores = combine_scores(
            (frequency_scores(history), 0.15),
            (gap_scores(history), 0.25),
            (recent_trend_scores(history), 0.20),
            (digit_level_scores(history), 0.25),
            (pattern_scores(history), 0.15),
        )
        return pick_top(scores, k)

    raise ValueError(f"Unknown model: {model_name}")


MODEL_NAMES = [
    "Random",
    "Hot Frequency",
    "Cold Frequency",
    "Gap Overdue",
    "Recent Trend",
    "Digit-Level",
    "Pattern",
    "Hybrid",
]

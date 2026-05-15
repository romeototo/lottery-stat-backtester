from __future__ import annotations

import pandas as pd
import numpy as np
from scipy.stats import binomtest
from models import MODEL_NAMES, model_predictions


def rolling_backtest(df: pd.DataFrame, model_name: str, pick_count: int = 5, warmup: int = 12, seed: int = 42) -> pd.DataFrame:
    rows = []
    rng = np.random.default_rng(seed)

    data = df.dropna(subset=["date"]).copy()
    data = data[data["last_2_digits"].str.match(r"^\d{2}$", na=False)].reset_index(drop=True)

    for i in range(warmup, len(data)):
        history = data.iloc[:i]["last_2_digits"]
        actual = data.iloc[i]["last_2_digits"]
        preds = model_predictions(history, model_name, pick_count, rng=rng)
        hit = actual in preds
        rows.append({
            "date": data.iloc[i]["date"].date().isoformat(),
            "actual": actual,
            "model": model_name,
            "predictions": ", ".join(preds),
            "hit": bool(hit),
        })
    return pd.DataFrame(rows)


def model_tournament(df: pd.DataFrame, pick_count: int = 5, warmup: int = 12, seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    all_details = []
    summary_rows = []

    for model in MODEL_NAMES:
        details = rolling_backtest(df, model, pick_count=pick_count, warmup=warmup, seed=seed)
        all_details.append(details)
        total = len(details)
        hits = int(details["hit"].sum()) if total else 0
        hit_rate = hits / total * 100 if total else 0.0
        summary_rows.append({
            "model": model,
            "test_draws": total,
            "hits": hits,
            "hit_rate_percent": round(hit_rate, 2),
            "theoretical_random_percent": round(pick_count / 100 * 100, 2),
            "edge_vs_random_percent": round(hit_rate - pick_count, 2),
            "status": "มี edge เบื้องต้น" if hit_rate > pick_count else "ยังไม่ชนะสุ่ม",
        })

    summary = pd.DataFrame(summary_rows).sort_values("hit_rate_percent", ascending=False).reset_index(drop=True)
    details_df = pd.concat(all_details, ignore_index=True) if all_details else pd.DataFrame()
    return summary, details_df


def random_baseline_simulation(draw_count: int, pick_count: int = 5, runs: int = 1000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    # Probability hit per draw = pick_count / 100.
    p = pick_count / 100
    hits = rng.binomial(draw_count, p, size=runs)
    return pd.DataFrame({
        "run": np.arange(1, runs + 1),
        "hits": hits,
        "hit_rate_percent": hits / max(draw_count, 1) * 100,
    })


def random_baseline_summary(baseline: pd.DataFrame) -> pd.DataFrame:
    if baseline.empty:
        return pd.DataFrame([{
            "runs": 0,
            "mean_hit_rate_percent": 0.0,
            "median_hit_rate_percent": 0.0,
            "p05_hit_rate_percent": 0.0,
            "p95_hit_rate_percent": 0.0,
            "mean_hits": 0.0,
            "median_hits": 0.0,
            "p05_hits": 0.0,
            "p95_hits": 0.0,
        }])

    return pd.DataFrame([{
        "runs": int(len(baseline)),
        "mean_hit_rate_percent": round(float(baseline["hit_rate_percent"].mean()), 4),
        "median_hit_rate_percent": round(float(baseline["hit_rate_percent"].median()), 4),
        "p05_hit_rate_percent": round(float(baseline["hit_rate_percent"].quantile(0.05)), 4),
        "p95_hit_rate_percent": round(float(baseline["hit_rate_percent"].quantile(0.95)), 4),
        "mean_hits": round(float(baseline["hits"].mean()), 4),
        "median_hits": round(float(baseline["hits"].median()), 4),
        "p05_hits": round(float(baseline["hits"].quantile(0.05)), 4),
        "p95_hits": round(float(baseline["hits"].quantile(0.95)), 4),
    }])


def statistical_significance_table(tournament: pd.DataFrame, pick_count: int = 5, confidence_level: float = 0.95) -> pd.DataFrame:
    rows = []
    chance = min(max(pick_count / 100, 0), 1)

    for _, row in tournament.iterrows():
        draws = int(row["test_draws"])
        hits = int(row["hits"])
        hit_rate = hits / draws if draws else 0.0
        if draws:
            result = binomtest(hits, draws, chance, alternative="greater")
            ci = result.proportion_ci(confidence_level=confidence_level, method="wilson")
            p_value = float(result.pvalue)
            ci_low = float(ci.low * 100)
            ci_high = float(ci.high * 100)
        else:
            p_value = np.nan
            ci_low = np.nan
            ci_high = np.nan

        has_statistical_edge = bool(draws and p_value < 0.05 and hit_rate > chance)
        rows.append({
            "model": row["model"],
            "test_draws": draws,
            "hits": hits,
            "hit_rate_percent": round(hit_rate * 100, 4),
            "random_chance_percent": round(chance * 100, 4),
            "p_value_vs_random": p_value,
            "ci_low_percent": round(ci_low, 4) if not np.isnan(ci_low) else np.nan,
            "ci_high_percent": round(ci_high, 4) if not np.isnan(ci_high) else np.nan,
            "has_statistical_edge": has_statistical_edge,
            "interpretation": "มีนัยสำคัญเหนือโอกาสสุ่มในข้อมูลทดสอบนี้" if has_statistical_edge else "ยังไม่พบ edge ทางสถิติเมื่อเทียบกับการสุ่ม",
        })

    return pd.DataFrame(rows)


def compare_models_to_random_baseline(tournament: pd.DataFrame, baseline_summary_df: pd.DataFrame) -> pd.DataFrame:
    if baseline_summary_df.empty:
        comparison_rate = 0.0
    else:
        comparison_rate = float(baseline_summary_df.iloc[0]["p95_hit_rate_percent"])

    out = tournament.copy()
    out["random_baseline_p95_percent"] = round(comparison_rate, 4)
    out["beats_random_baseline"] = out["hit_rate_percent"] > comparison_rate
    out["random_baseline_status"] = np.where(
        out["beats_random_baseline"],
        "สูงกว่า random baseline p95",
        "ยังไม่ชนะ random baseline p95",
    )
    return out


def no_edge_warning_messages(tournament: pd.DataFrame) -> list[str]:
    if tournament.empty or "beats_random_baseline" not in tournament.columns:
        return ["No Edge: backtest results are not available or random baseline comparison has not run."]

    weak_models = tournament[~tournament["beats_random_baseline"]]
    if weak_models.empty:
        return []

    return [
        f"No Edge: {row['model']} did not beat the random baseline p95. Do not treat this model as predictive."
        for _, row in weak_models.iterrows()
    ]

from __future__ import annotations

import pandas as pd
import numpy as np
from scipy.stats import chisquare
from models import ALL_2D, normalize_2d, frequency_scores, gap_scores, digit_level_scores, pattern_scores, combine_scores, pick_top


VALID_LAST2_PATTERN = r"^\d{2}$"
TRUST_WARNING = "Trust score is low. Do not rely on prediction scores; use this dataset only for data cleanup and review."


def _last2_raw_text(value) -> str:
    if pd.isna(value):
        return ""
    s = str(value).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s


def load_lottery_file(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, dtype=str)
    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file, dtype=str)
    else:
        raise ValueError("รองรับเฉพาะ CSV / Excel")
    return prepare_dataframe(df)


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    if "source_row" not in df.columns:
        df.insert(0, "source_row", range(2, len(df) + 2))

    if "date" not in df.columns:
        raise ValueError("ต้องมีคอลัมน์ date")
    if "last_2_digits" not in df.columns:
        raise ValueError("ต้องมีคอลัมน์ last_2_digits")

    df["date"] = pd.to_datetime(df["date"], errors="coerce", format="mixed")
    raw_last2 = df["last_2_digits"].map(_last2_raw_text)
    df["last_2_digits_raw"] = raw_last2
    df["last_2_digits_missing"] = raw_last2.eq("")
    df["last_2_digits_invalid"] = ~df["last_2_digits_missing"] & ~raw_last2.str.match(r"^\d{1,2}$", na=False)
    df["last_2_digits"] = raw_last2.map(normalize_2d)
    df = df.sort_values("date").reset_index(drop=True)
    return df


def data_quality_report(df: pd.DataFrame) -> dict:
    total = len(df)
    missing_date = int(df["date"].isna().sum())
    if "last_2_digits_missing" in df.columns:
        missing_last2 = int(df["last_2_digits_missing"].sum())
    else:
        missing_last2 = int(df["last_2_digits"].fillna("").eq("").sum())
    if "last_2_digits_invalid" in df.columns:
        invalid_last2 = int(df["last_2_digits_invalid"].sum())
    else:
        present_last2 = df["last_2_digits"].fillna("").ne("")
        invalid_last2 = int((present_last2 & ~df["last_2_digits"].str.match(VALID_LAST2_PATTERN, na=False)).sum())
    duplicate_dates = int(df.loc[df["date"].notna(), "date"].duplicated().sum())
    min_date = df["date"].min()
    max_date = df["date"].max()

    usable = df.dropna(subset=["date"])
    usable = usable[usable["last_2_digits"].str.match(VALID_LAST2_PATTERN, na=False)]

    return {
        "total_rows": total,
        "usable_rows": len(usable),
        "missing_date": missing_date,
        "missing_last_2_digits": missing_last2,
        "duplicate_dates": duplicate_dates,
        "invalid_last_2_digits": invalid_last2,
        "min_date": "" if pd.isna(min_date) else min_date.date().isoformat(),
        "max_date": "" if pd.isna(max_date) else max_date.date().isoformat(),
    }


def data_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    issue_rows = []
    duplicate_dates = df["date"].notna() & df["date"].duplicated(keep=False)

    for idx, row in df.iterrows():
        missing_date = bool(pd.isna(row["date"]))
        missing_last2 = bool(row.get("last_2_digits_missing", pd.isna(row.get("last_2_digits")) or row.get("last_2_digits", "") == ""))
        invalid_last2 = bool(row.get("last_2_digits_invalid", False))
        duplicate_date = bool(duplicate_dates.iloc[idx])
        issues = []
        if missing_date:
            issues.append("missing_date")
        if missing_last2:
            issues.append("missing_last_2_digits")
        if invalid_last2:
            issues.append("invalid_last_2_digits_format")
        if duplicate_date:
            issues.append("duplicate_date")
        if not issues:
            continue

        date_value = row["date"]
        issue_rows.append({
            "source_row": row.get("source_row", idx + 2),
            "date": "" if pd.isna(date_value) else date_value.date().isoformat(),
            "last_2_digits_raw": row.get("last_2_digits_raw", row.get("last_2_digits", "")),
            "last_2_digits": row.get("last_2_digits", ""),
            "missing_date": missing_date,
            "missing_last_2_digits": missing_last2,
            "invalid_last_2_digits_format": invalid_last2,
            "duplicate_date": duplicate_date,
            "issues": ", ".join(issues),
        })

    return pd.DataFrame(issue_rows)


def missing_draw_periods(df: pd.DataFrame, max_gap_days: int = 25) -> pd.DataFrame:
    dates = df["date"].dropna().drop_duplicates().sort_values().reset_index(drop=True)
    rows = []
    for idx in range(1, len(dates)):
        previous_date = dates.iloc[idx - 1]
        current_date = dates.iloc[idx]
        gap_days = int((current_date - previous_date).days)
        if gap_days <= max_gap_days:
            continue
        estimated_missing_draws = max(round(gap_days / 15.2) - 1, 1)
        rows.append({
            "previous_draw_date": previous_date.date().isoformat(),
            "next_draw_date": current_date.date().isoformat(),
            "gap_days": gap_days,
            "estimated_missing_draws": estimated_missing_draws,
        })
    return pd.DataFrame(rows)


def invalid_prize_format_report(df: pd.DataFrame) -> pd.DataFrame:
    expected_widths = {
        "first_prize": 6,
        "last_2_digits": 2,
        "front_3_1": 3,
        "front_3_2": 3,
        "last_3_1": 3,
        "last_3_2": 3,
    }
    rows = []
    for column, width in expected_widths.items():
        if column not in df.columns:
            continue
        values = df[column].fillna("").astype(str).str.strip()
        invalid_mask = values.ne("") & ~values.str.match(fr"^\d{{{width}}}$", na=False)
        for idx, value in values[invalid_mask].items():
            date_value = df.loc[idx, "date"] if "date" in df.columns else pd.NaT
            rows.append({
                "source_row": df.loc[idx, "source_row"] if "source_row" in df.columns else idx + 2,
                "date": "" if pd.isna(date_value) else date_value.date().isoformat(),
                "field": column,
                "value": value,
                "expected_format": f"{width} digits",
            })
    return pd.DataFrame(rows)


def calibration_report(df: pd.DataFrame, before_trust_score: int | None = None) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    quality = data_quality_report(df)
    trust_summary, _ = data_trust_score(df)
    missing_periods = missing_draw_periods(df)
    invalid_prizes = invalid_prize_format_report(df)
    calibration = {
        "rows_imported": quality["total_rows"],
        "usable_rows": quality["usable_rows"],
        "date_range": f"{quality['min_date']} to {quality['max_date']}" if quality["min_date"] and quality["max_date"] else "",
        "missing_draw_periods": int(len(missing_periods)),
        "duplicate_draw_dates": quality["duplicate_dates"],
        "invalid_prize_formats": int(len(invalid_prizes)),
        "trust_score_before_normalization": before_trust_score,
        "trust_score_after_normalization": trust_summary["trust_score"],
        "trust_level_after_normalization": trust_summary["trust_level"],
    }
    return calibration, missing_periods, invalid_prizes


def _source_score(df: pd.DataFrame) -> tuple[int, str]:
    if "source" not in df.columns:
        return 10, "source column missing; treated as unknown"

    sources = df["source"].fillna("").astype(str).str.lower()
    official_terms = ("glo", "official_glo", "government lottery office", "official", "สำนักงานสลาก")
    manual_terms = ("manual", "sample")

    official_count = int(sources.str.contains("|".join(official_terms), regex=True).sum())
    manual_count = int(sources.str.contains("|".join(manual_terms), regex=True).sum())
    known_count = int(sources.ne("").sum())
    total = max(len(sources), 1)

    if official_count / total >= 0.8:
        return 20, "mostly official source"
    if manual_count / total >= 0.8:
        return 8, "mostly manual/sample source"
    if known_count / total >= 0.8:
        return 8, "source present but not recognized as official"
    return 4, "mostly unknown source"


def _continuity_score(df: pd.DataFrame) -> tuple[int, str]:
    dates = df["date"].dropna().drop_duplicates().sort_values()
    if len(dates) < 2:
        return 0, "not enough dated rows to assess continuity"

    span_days = max(int((dates.max() - dates.min()).days), 1)
    expected_draws = max(1, round(span_days / 15.2) + 1)
    coverage_ratio = min(len(dates) / expected_draws, 1.0)
    score = round(coverage_ratio * 15)
    return int(score), f"date coverage ratio {coverage_ratio:.2f} across {len(dates)} dated draws"


def data_trust_score(df: pd.DataFrame, min_backtest_rows: int = 36) -> tuple[dict, pd.DataFrame]:
    quality = data_quality_report(df)
    total = max(int(quality["total_rows"]), 1)

    source_points, source_explanation = _source_score(df)
    missing_date_penalty = min(15, int(round(quality["missing_date"] / total * 30)))
    missing_last2_penalty = min(15, int(round(quality["missing_last_2_digits"] / total * 30)))
    invalid_last2_penalty = min(15, int(round(quality["invalid_last_2_digits"] / total * 30)))
    duplicate_penalty = min(15, int(round(quality["duplicate_dates"] / total * 30)))

    date_quality_points = max(0, 15 - missing_date_penalty)
    last2_quality_points = max(0, 20 - missing_last2_penalty - invalid_last2_penalty)
    duplicate_points = max(0, 15 - duplicate_penalty)
    row_ratio = min(quality["usable_rows"] / max(min_backtest_rows, 1), 1.0)
    row_points = int(round(row_ratio * 15))
    continuity_points, continuity_explanation = _continuity_score(df)

    breakdown = pd.DataFrame([
        {"component": "source", "points": source_points, "max_points": 20, "explanation": source_explanation},
        {"component": "date_quality", "points": date_quality_points, "max_points": 15, "explanation": f"{quality['missing_date']} missing dates"},
        {"component": "last_2_digits_quality", "points": last2_quality_points, "max_points": 20, "explanation": f"{quality['missing_last_2_digits']} missing, {quality['invalid_last_2_digits']} invalid"},
        {"component": "duplicate_dates", "points": duplicate_points, "max_points": 15, "explanation": f"{quality['duplicate_dates']} duplicate dates"},
        {"component": "historical_rows", "points": row_points, "max_points": 15, "explanation": f"{quality['usable_rows']} usable rows; target {min_backtest_rows}+"},
        {"component": "date_coverage_continuity", "points": continuity_points, "max_points": 15, "explanation": continuity_explanation},
    ])
    score = int(breakdown["points"].sum())
    if score >= 85:
        level = "High trust"
    elif score >= 60:
        level = "Medium trust"
    else:
        level = "Low trust"

    summary = {
        "trust_score": score,
        "trust_level": level,
        "warning": trust_warning_message(score),
    }
    return summary, breakdown


def trust_warning_message(score: int) -> str:
    return TRUST_WARNING if score < 60 else ""


def frequency_table(df: pd.DataFrame) -> pd.DataFrame:
    s = df["last_2_digits"].dropna()
    s = s[s.str.match(VALID_LAST2_PATTERN, na=False)]
    counts = s.value_counts().reindex(ALL_2D, fill_value=0)
    out = pd.DataFrame({
        "number": counts.index,
        "frequency": counts.values,
        "percent": counts.values / max(len(s), 1) * 100,
    })
    return out.sort_values(["frequency", "number"], ascending=[False, True]).reset_index(drop=True)


def hot_cold_tables(df: pd.DataFrame, top_n: int = 20):
    freq = frequency_table(df)
    hot = freq.head(top_n).copy()
    cold = freq.sort_values(["frequency", "number"], ascending=[True, True]).head(top_n).copy()
    return hot, cold


def chi_square_test(df: pd.DataFrame) -> dict:
    freq = frequency_table(df).sort_values("number")
    observed = freq["frequency"].values
    if observed.sum() == 0:
        return {"chi_square": None, "p_value": None, "df": 99, "interpretation": "ไม่มีข้อมูลพอ"}
    expected = np.ones(100) * observed.sum() / 100
    stat, p = chisquare(observed, expected)
    return {
        "chi_square": float(stat),
        "p_value": float(p),
        "df": 99,
        "interpretation": "ไม่พบหลักฐานว่าการแจกแจงต่างจากสม่ำเสมออย่างมีนัยสำคัญ" if p >= 0.05 else "พบสัญญาณว่าการแจกแจงอาจไม่สม่ำเสมอ แต่ต้องระวัง sample size และ data quality",
    }


def gap_table(df: pd.DataFrame) -> pd.DataFrame:
    hist = list(df["last_2_digits"].dropna())
    rows = []
    n = len(hist)
    for num in ALL_2D:
        idxs = [i for i, x in enumerate(hist) if x == num]
        if idxs:
            current_gap = n - 1 - idxs[-1]
            last_seen = df.iloc[idxs[-1]]["date"]
            if len(idxs) >= 2:
                avg_gap = float(np.mean(np.diff(idxs)))
            else:
                avg_gap = max(1.0, n / 2)
        else:
            current_gap = n
            avg_gap = n
            last_seen = pd.NaT
        overdue_score = current_gap / max(avg_gap, 1.0)
        rows.append({
            "number": num,
            "current_gap": current_gap,
            "average_gap": round(avg_gap, 2),
            "overdue_score": round(overdue_score, 3),
            "last_seen": "" if pd.isna(last_seen) else last_seen.date().isoformat(),
        })
    return pd.DataFrame(rows).sort_values("overdue_score", ascending=False).reset_index(drop=True)


def prediction_table(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    history = df["last_2_digits"].dropna()
    scores = combine_scores(
        (frequency_scores(history), 0.15),
        (gap_scores(history), 0.25),
        (frequency_scores(history.tail(12)), 0.20),
        (digit_level_scores(history), 0.25),
        (pattern_scores(history), 0.15),
    )

    rows = []
    for num in pick_top(scores, top_n):
        rows.append({
            "number": num,
            "model_score": round(scores[num] * 100, 2),
            "reason": "Hybrid: frequency + gap + recent trend + digit-level + pattern",
            "risk": "สูง: หวยเป็นเหตุการณ์สุ่ม ไม่รับประกันผล",
        })
    return pd.DataFrame(rows)


def digit_analysis(df: pd.DataFrame) -> pd.DataFrame:
    s = df["last_2_digits"].dropna()
    tens = s.str[0].value_counts().reindex([str(i) for i in range(10)], fill_value=0)
    ones = s.str[1].value_counts().reindex([str(i) for i in range(10)], fill_value=0)
    return pd.DataFrame({
        "digit": [str(i) for i in range(10)],
        "tens_frequency": tens.values,
        "ones_frequency": ones.values,
        "total_digit_frequency": tens.values + ones.values,
    }).sort_values("total_digit_frequency", ascending=False).reset_index(drop=True)

from __future__ import annotations

from io import BytesIO
import pandas as pd
from analyzer import calibration_report, data_quality_report, data_quality_issues, data_trust_score, frequency_table, hot_cold_tables, chi_square_test, gap_table, digit_analysis, prediction_table
from backtester import (
    compare_models_to_random_baseline,
    model_tournament,
    random_baseline_simulation,
    random_baseline_summary,
    statistical_significance_table,
)


def build_excel_report(df: pd.DataFrame, pick_count: int, warmup: int, random_runs: int) -> bytes:
    output = BytesIO()

    quality = pd.DataFrame([data_quality_report(df)])
    quality_issues = data_quality_issues(df)
    trust_summary, trust_breakdown = data_trust_score(df)
    trust_sheet = pd.concat([pd.DataFrame([trust_summary]), trust_breakdown], ignore_index=True, sort=False)
    calibration, missing_periods, invalid_prizes = calibration_report(df)
    freq = frequency_table(df)
    hot, cold = hot_cold_tables(df)
    chi = pd.DataFrame([chi_square_test(df)])
    gaps = gap_table(df)
    digits = digit_analysis(df)
    prediction = prediction_table(df)
    tournament, details = model_tournament(df, pick_count=pick_count, warmup=warmup)
    baseline = random_baseline_simulation(len(details[details["model"] == "Random"]) if not details.empty else 0, pick_count, runs=random_runs)
    baseline_summary = random_baseline_summary(baseline)
    tournament = compare_models_to_random_baseline(tournament, baseline_summary)
    significance = statistical_significance_table(tournament, pick_count=pick_count)
    tournament = tournament.merge(
        significance[["model", "p_value_vs_random", "ci_low_percent", "ci_high_percent", "has_statistical_edge"]],
        on="model",
        how="left",
    )
    baseline_distribution = baseline["hit_rate_percent"].round(2).value_counts().sort_index().rename_axis("hit_rate_percent").reset_index(name="runs")

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Raw Data", index=False)
        quality.to_excel(writer, sheet_name="Data Quality", index=False)
        quality_issues.to_excel(writer, sheet_name="Data Quality Issues", index=False)
        trust_sheet.to_excel(writer, sheet_name="Data Trust Score", index=False)
        pd.DataFrame([calibration]).to_excel(writer, sheet_name="Calibration Report", index=False)
        missing_periods.to_excel(writer, sheet_name="Missing Draw Periods", index=False)
        invalid_prizes.to_excel(writer, sheet_name="Invalid Prize Formats", index=False)
        freq.to_excel(writer, sheet_name="Frequency", index=False)
        hot.to_excel(writer, sheet_name="Hot Numbers", index=False)
        cold.to_excel(writer, sheet_name="Cold Numbers", index=False)
        chi.to_excel(writer, sheet_name="Chi Square", index=False)
        gaps.to_excel(writer, sheet_name="Gap Analysis", index=False)
        digits.to_excel(writer, sheet_name="Digit Analysis", index=False)
        tournament.to_excel(writer, sheet_name="Model Tournament", index=False)
        details.to_excel(writer, sheet_name="Backtest Details", index=False)
        baseline.to_excel(writer, sheet_name="Random Baseline", index=False)
        baseline_summary.to_excel(writer, sheet_name="Random Baseline Summary", index=False)
        significance.to_excel(writer, sheet_name="Statistical Significance", index=False)
        baseline_distribution.to_excel(writer, sheet_name="Random Distribution", index=False)
        prediction.to_excel(writer, sheet_name="Prediction Summary", index=False)

        workbook = writer.book
        warning_format = workbook.add_format({"bold": True, "font_color": "red", "text_wrap": True})
        ws = workbook.add_worksheet("Disclaimer")
        ws.write("A1", "หวยเป็นเหตุการณ์สุ่ม ไม่มีวิธีใดรับประกันผลลัพธ์ได้ โปรแกรมนี้ใช้เพื่อการศึกษาเชิงสถิติ การทดสอบโมเดล และการคุมความเสี่ยงเท่านั้น", warning_format)
        ws.set_column("A:A", 120)

        charts = workbook.add_worksheet("Charts")
        if len(freq) > 0:
            chart = workbook.add_chart({"type": "column"})
            chart.add_series({
                "name": "Top 20 Frequency",
                "categories": ["Frequency", 1, 0, min(20, len(freq)), 0],
                "values": ["Frequency", 1, 1, min(20, len(freq)), 1],
            })
            chart.set_title({"name": "Frequency Top 20"})
            charts.insert_chart("A1", chart)
        if len(gaps) > 0:
            chart = workbook.add_chart({"type": "column"})
            chart.add_series({
                "name": "Top Overdue",
                "categories": ["Gap Analysis", 1, 0, min(20, len(gaps)), 0],
                "values": ["Gap Analysis", 1, 3, min(20, len(gaps)), 3],
            })
            chart.set_title({"name": "Gap Overdue Top 20"})
            charts.insert_chart("I1", chart)
        if len(tournament) > 0:
            chart = workbook.add_chart({"type": "column"})
            chart.add_series({
                "name": "Hit Rate",
                "categories": ["Model Tournament", 1, 0, len(tournament), 0],
                "values": ["Model Tournament", 1, 3, len(tournament), 3],
            })
            chart.set_title({"name": "Model Hit Rate"})
            charts.insert_chart("A18", chart)
        if len(baseline_distribution) > 0:
            chart = workbook.add_chart({"type": "column"})
            chart.add_series({
                "name": "Random Baseline Runs",
                "categories": ["Random Distribution", 1, 0, len(baseline_distribution), 0],
                "values": ["Random Distribution", 1, 1, len(baseline_distribution), 1],
            })
            chart.set_title({"name": "Random Baseline Distribution"})
            charts.insert_chart("I18", chart)

    return output.getvalue()

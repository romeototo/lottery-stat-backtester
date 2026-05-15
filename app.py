from __future__ import annotations

import streamlit as st
import pandas as pd

from analyzer import (
    load_lottery_file,
    prepare_dataframe,
    data_quality_report,
    data_quality_issues,
    data_trust_score,
    calibration_report,
    frequency_table,
    hot_cold_tables,
    chi_square_test,
    gap_table,
    digit_analysis,
    prediction_table,
)
from backtester import (
    compare_models_to_random_baseline,
    model_tournament,
    random_baseline_simulation,
    random_baseline_summary,
    no_edge_warning_messages,
    statistical_significance_table,
)
from data_sources.glo_importer import load_glo_file
from exporter import build_excel_report


st.set_page_config(
    page_title="Lottery Stat Backtester",
    page_icon="📊",
    layout="wide",
)

DISCLAIMER = "หวยเป็นเหตุการณ์สุ่ม ไม่มีวิธีใดรับประกันผลลัพธ์ได้ โปรแกรมนี้ใช้เพื่อการศึกษาเชิงสถิติ การทดสอบโมเดล และการคุมความเสี่ยงเท่านั้น"

st.title("📊 Lottery Stat Backtester")
st.warning(DISCLAIMER)

st.sidebar.header("Settings")
pick_count = st.sidebar.slider("จำนวนเลขที่เลือกต่อหนึ่งงวด / Picks per draw", min_value=1, max_value=20, value=5)
warmup = st.sidebar.slider("จำนวนงวดตั้งต้นก่อน Backtest / Warmup draws", min_value=5, max_value=100, value=12)
random_runs = st.sidebar.slider("จำนวนรอบสุ่มเทียบ baseline / Random baseline runs", min_value=100, max_value=10000, value=1000, step=100)
import_mode = st.sidebar.radio(
    "รูปแบบไฟล์นำเข้า / Import Mode",
    ["Standard CSV/Excel schema", "GLO-style official file import"],
)

uploaded = st.file_uploader("อัปโหลดไฟล์ผลหวยย้อนหลัง CSV / Excel", type=["csv", "xlsx", "xls"])

if uploaded is None:
    st.info("ยังไม่ได้อัปโหลดไฟล์ ใช้ไฟล์ตัวอย่างจาก data/sample_thai_lottery.csv ได้")
    try:
        df = prepare_dataframe(pd.read_csv("data/sample_thai_lottery.csv", dtype=str))
        st.caption("กำลังแสดงข้อมูลตัวอย่าง")
    except Exception:
        st.stop()
else:
    try:
        if import_mode == "GLO-style official file import":
            df = load_glo_file(uploaded)
        else:
            df = load_lottery_file(uploaded)
    except Exception as e:
        st.error(f"อ่านไฟล์ไม่ได้: {e}")
        st.stop()
    st.subheader("Normalized Preview")
    st.caption("ตรวจดูข้อมูลหลังแปลงให้อยู่ใน schema กลางก่อนเริ่มวิเคราะห์")
    st.dataframe(df.head(20), width="stretch")

q = data_quality_report(df)
trust_summary, trust_breakdown = data_trust_score(df)
calibration, missing_periods, invalid_prizes = calibration_report(df)

tab_quality, tab_stats, tab_backtest, tab_risk, tab_export = st.tabs([
    "1) Data Quality",
    "2) Analysis",
    "3) Backtest",
    "4) Budget / Risk",
    "5) Export",
])

with tab_quality:
    st.subheader("Data Quality Check")
    st.caption("ตรวจความพร้อมของข้อมูลก่อนนำไปวิเคราะห์ เช่น วันที่หาย เลขผิดรูปแบบ งวดซ้ำ และคะแนนความน่าเชื่อถือ")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", q["total_rows"])
    c2.metric("Usable Rows", q["usable_rows"])
    c3.metric("Duplicate Dates", q["duplicate_dates"])
    c4.metric("Invalid Last 2", q["invalid_last_2_digits"])

    st.json(q)
    st.subheader("Data Trust Score")
    t1, t2 = st.columns(2)
    t1.metric("Trust Score", f"{trust_summary['trust_score']}/100")
    t2.metric("Trust Level", trust_summary["trust_level"])
    if trust_summary["warning"]:
        st.warning(trust_summary["warning"])
        st.warning("คะแนนความน่าเชื่อถือต่ำ ไม่ควรพึ่งพา Prediction Score จากชุดข้อมูลนี้")
    st.dataframe(trust_breakdown, width="stretch")
    st.subheader("Calibration Report")
    st.json(calibration)
    if not missing_periods.empty:
        st.write("Missing Draw Periods")
        st.dataframe(missing_periods, width="stretch")
    if not invalid_prizes.empty:
        st.write("Invalid Prize Formats")
        st.dataframe(invalid_prizes, width="stretch")

    issues = data_quality_issues(df)
    st.subheader("Row-Level Data Quality Issues")
    if issues.empty:
        st.success("ไม่พบปัญหาคุณภาพข้อมูลระดับแถว")
    else:
        st.dataframe(issues, width="stretch")
    st.dataframe(df, width="stretch")

with tab_stats:
    st.subheader("Frequency / Hot / Cold")
    st.caption("ดูภาพรวมสถิติที่เกิดขึ้นในอดีตเท่านั้น ไม่ใช่การรับประกันเลขในอนาคต")
    hot, cold = hot_cold_tables(df, top_n=20)
    col1, col2 = st.columns(2)
    with col1:
        st.write("Hot Numbers")
        st.dataframe(hot, width="stretch")
        st.bar_chart(hot.set_index("number")["frequency"])
    with col2:
        st.write("Cold Numbers")
        st.dataframe(cold, width="stretch")

    st.subheader("Chi-Square Test")
    chi = chi_square_test(df)
    st.json(chi)

    st.subheader("Gap Analysis")
    gaps = gap_table(df)
    st.dataframe(gaps.head(30), width="stretch")
    st.bar_chart(gaps.head(20).set_index("number")["overdue_score"])

    st.subheader("Digit-Level Analysis")
    st.dataframe(digit_analysis(df), width="stretch")

    st.subheader("Prediction Score")
    if trust_summary["trust_level"] == "Low trust":
        st.warning("Trust Score ต่ำ: ซ่อน Prediction Score ไว้เพื่อลดความเข้าใจผิด ควรแก้ข้อมูลก่อนใช้งานส่วนนี้")
        with st.expander("Show Prediction Score anyway"):
            st.caption("นี่คือคะแนนโมเดล ไม่ใช่ความน่าจะเป็นถูกรางวัลจริง")
            st.dataframe(prediction_table(df, top_n=20), width="stretch")
    else:
        st.caption("นี่คือคะแนนโมเดล ไม่ใช่ความน่าจะเป็นถูกรางวัลจริง")
        st.dataframe(prediction_table(df, top_n=20), width="stretch")

with tab_backtest:
    st.subheader("Model Tournament")
    st.caption("ทดสอบย้อนหลังแบบ rolling: แต่ละงวดใช้เฉพาะข้อมูลก่อนหน้างวดนั้น และเทียบกับ random baseline")
    st.caption("Rolling Backtest: ทุกงวดใช้เฉพาะข้อมูลก่อนหน้างวดนั้น")
    tournament, details = model_tournament(df, pick_count=pick_count, warmup=warmup)
    draw_count = len(details[details["model"] == "Random"]) if not details.empty else 0
    baseline = random_baseline_simulation(draw_count, pick_count=pick_count, runs=random_runs)
    baseline_summary = random_baseline_summary(baseline)
    tournament = compare_models_to_random_baseline(tournament, baseline_summary)
    significance = statistical_significance_table(tournament, pick_count=pick_count)
    tournament = tournament.merge(
        significance[["model", "p_value_vs_random", "ci_low_percent", "ci_high_percent", "has_statistical_edge"]],
        on="model",
        how="left",
    )
    no_edge_messages = no_edge_warning_messages(tournament)
    for message in no_edge_messages[:5]:
        st.warning(message)
    if len(no_edge_messages) > 5:
        st.warning(f"No Edge: {len(no_edge_messages) - 5} additional models also did not beat random baseline p95.")
    st.dataframe(tournament, width="stretch")
    st.bar_chart(tournament.set_index("model")["hit_rate_percent"])

    st.subheader("Statistical Significance")
    st.caption("p-value ทดสอบว่า hit rate สูงกว่าโอกาสสุ่มหรือไม่ ไม่ใช่การรับประกันผลอนาคต")
    st.dataframe(significance, width="stretch")

    st.subheader("Backtest Details")
    st.dataframe(details, width="stretch")

    st.subheader("Random Baseline Simulation")
    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Random Mean", f"{baseline_summary.iloc[0]['mean_hit_rate_percent']:.2f}%")
    b2.metric("Random Median", f"{baseline_summary.iloc[0]['median_hit_rate_percent']:.2f}%")
    b3.metric("Random P05", f"{baseline_summary.iloc[0]['p05_hit_rate_percent']:.2f}%")
    b4.metric("Random P95", f"{baseline_summary.iloc[0]['p95_hit_rate_percent']:.2f}%")
    st.dataframe(baseline_summary, width="stretch")
    st.dataframe(baseline.describe().T, width="stretch")
    baseline_distribution = baseline["hit_rate_percent"].round(2).value_counts().sort_index().rename_axis("hit_rate_percent").reset_index(name="runs")
    st.bar_chart(baseline_distribution.set_index("hit_rate_percent")["runs"])

with tab_risk:
    st.subheader("Budget / Expected Loss Calculator")
    st.caption("คำนวณความเสี่ยงและ expected loss เพื่อคุมงบ ไม่ใช่คำแนะนำให้ซื้อหวย")
    st.caption("ใช้สำหรับคุมงบ ไม่ใช่ชวนเล่น")

    col1, col2, col3 = st.columns(3)
    with col1:
        numbers_bought = st.number_input("ซื้อกี่เลขต่อ 1 งวด", min_value=1, max_value=100, value=5)
        cost_per_number = st.number_input("ต้นทุนต่อเลข/ใบ/ชุด", min_value=0.0, value=100.0, step=10.0)
    with col2:
        payout = st.number_input("เงินจ่ายถ้าถูกต่อเลข", min_value=0.0, value=2000.0, step=100.0)
        draws = st.number_input("จำนวนงวดที่จะเล่น", min_value=1, max_value=1000, value=4)
    with col3:
        p_per_draw = min(numbers_bought / 100, 1.0)
        prob_at_least_one = 1 - (1 - p_per_draw) ** draws
        total_cost = numbers_bought * cost_per_number * draws
        expected_wins = p_per_draw * draws
        expected_payout = expected_wins * payout
        expected_profit = expected_payout - total_cost

        st.metric("โอกาสถูกอย่างน้อย 1 ครั้ง", f"{prob_at_least_one*100:.2f}%")
        st.metric("เงินที่ใช้รวม", f"{total_cost:,.2f}")
        st.metric("Expected Profit/Loss", f"{expected_profit:,.2f}")

    st.warning("ถ้า Expected Profit/Loss ติดลบ แปลว่าระยะยาวเสียเปรียบทางคณิตศาสตร์")

with tab_export:
    st.subheader("Export Excel Report")
    st.caption("ดาวน์โหลดรายงาน Excel รวมข้อมูลดิบ คุณภาพข้อมูล Trust Score Backtest Random Baseline และ Disclaimer")
    st.write("Export รายงานครบ: Raw Data, Data Quality, Frequency, Gap, Backtest, Random Baseline, Prediction")
    excel_bytes = build_excel_report(df, pick_count=pick_count, warmup=warmup, random_runs=random_runs)
    st.download_button(
        label="Download Excel Report",
        data=excel_bytes,
        file_name="lottery_backtest_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.caption(DISCLAIMER)

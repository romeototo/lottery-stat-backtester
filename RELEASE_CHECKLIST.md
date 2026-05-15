# V1 Release Checklist

> Disclaimer: หวยเป็นเหตุการณ์สุ่ม ไม่มีวิธีใดรับประกันผลลัพธ์ได้ โปรแกรมนี้ใช้เพื่อการศึกษาเชิงสถิติ การทดสอบโมเดล และการคุมความเสี่ยงเท่านั้น

## Setup

- [ ] Create a virtual environment.
- [ ] Install dependencies with `pip install -r requirements.txt`.
- [ ] Run `streamlit run app.py`.
- [ ] Confirm the app opens without startup errors.
- [ ] Confirm no generated logs, reports, virtualenv files, or private local data are staged.

## Import Test

- [ ] Load `data/sample_thai_lottery.csv` with the standard import mode.
- [ ] Upload a synthetic or downloaded GLO CSV/Excel file with `GLO-style official file import`.
- [ ] Confirm the normalized preview shows `date`, `first_prize`, `last_2_digits`, 3-digit prize columns, and `source`.
- [ ] Confirm leading zeros such as `06`, `009`, and `095` are preserved.

## Data Quality Test

- [ ] Review Data Quality counts.
- [ ] Review row-level issues.
- [ ] Review Data Trust Score and its breakdown.
- [ ] Confirm low-trust files show warnings.

## Backtest Test

- [ ] Run Model Tournament with default settings.
- [ ] Confirm Random Baseline summary appears.
- [ ] Confirm No Edge warnings appear for models that do not beat random baseline p95.
- [ ] Confirm statistical significance table includes p-values and confidence intervals.

## Export Test

- [ ] Download the Excel report.
- [ ] Open the workbook successfully.
- [ ] Confirm these sheets exist: Data Quality, Data Quality Issues, Data Trust Score, Calibration Report, Model Tournament, Random Baseline Summary, Statistical Significance, Disclaimer.
- [ ] Confirm the Disclaimer sheet is present.

## GitHub Readiness

- [ ] README quick start is accurate.
- [ ] `data/sample_thai_lottery.csv` is clearly marked as sample data.
- [ ] Screenshot files are added or the placeholder instructions remain in `screenshots/README.md`.
- [ ] No private/local paths are present in tracked docs or source files.
- [ ] License is present.
- [ ] Changelog is updated.

## Known Limitations

- No live GLO API fetcher in V1.
- No React frontend in V1.
- No Lao lottery support in V1.
- No database persistence in V1.
- No 1M Monte Carlo simulation in V1.
- Missing draw period detection is gap-based, not an official draw-calendar lookup.
- Backtest results do not guarantee future outcomes.

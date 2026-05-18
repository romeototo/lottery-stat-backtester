<div align="center">
  <h1>🎯 Lottery Stat Backtester</h1>
  <p>Local Streamlit app for Thai lottery historical-data validation, statistical backtesting, random-baseline comparison, and Excel reporting.</p>

  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-App-red?style=for-the-badge&logo=streamlit" alt="Streamlit" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
  <img src="https://img.shields.io/badge/Status-V1%20Release%20Candidate-orange?style=for-the-badge" alt="Status" />
</div>

<br />

โปรแกรมวิเคราะห์สถิติหวยไทยแบบรันในเครื่อง เน้นตรวจคุณภาพข้อมูล ทดสอบย้อนหลัง และส่งออกรายงาน Excel

> ⚠️ **Disclaimer:** หวยเป็นเหตุการณ์สุ่ม ไม่มีวิธีใดรับประกันผลลัพธ์ได้ โปรแกรมนี้ใช้เพื่อการศึกษาเชิงสถิติ การทดสอบโมเดล และการคุมความเสี่ยงเท่านั้น

## เป้าหมายของ V1

- Upload CSV / Excel
- ตรวจคุณภาพข้อมูล
- Frequency Analysis
- Gap Analysis
- Digit-Level Analysis
- Rolling Backtest
- Random Baseline
- Model Tournament
- Prediction Score
- Budget / Expected Loss Calculator
- Export Excel Report

V1 focuses on Thai lottery data only. Lao lottery support is listed as a future limitation, not part of this release.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal. The app loads `data/sample_thai_lottery.csv` automatically when no file is uploaded.

> Reminder: หวยเป็นเหตุการณ์สุ่ม ไม่มีวิธีใดรับประกันผลลัพธ์ได้ Backtest และ Prediction Score ใช้เพื่อการศึกษาและตรวจความเสี่ยงเท่านั้น

## วิธีติดตั้ง

```bash
cd lottery-stat-backtester
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## รูปแบบข้อมูล CSV / Excel

ต้องมีอย่างน้อยคอลัมน์เหล่านี้:

```csv
date,last_2_digits
2024-01-17,61
2024-02-01,09
```

คอลัมน์เสริมที่รองรับ:

```csv
first_prize,last_3_digits,front_3_1,front_3_2,last_3_1,last_3_2,source
```

## How to import GLO data

1. Download a CSV or Excel file from the official Thai Government Lottery Office (GLO) / Open Data source.
2. Run the app:

```bash
streamlit run app.py
```

3. In the sidebar, choose `GLO-style official file import`.
4. Upload the downloaded GLO file.
5. Review the normalized preview, calibration report, row-level data issues, and Data Trust Score before using Backtest or Prediction Score.

You may place downloaded files in `data/real_samples/` for local testing. Do not hardcode private or local-only file paths in the code.

## Optional GLO API fetcher

V1 keeps file import as the stable path. The app also includes an optional GLO API fetcher for quick checks:

- `GLO API latest draw` fetches the latest official draw.
- `GLO API by draw date` fetches one selected official draw date.

If the API is unavailable or changes its response shape, use `GLO-style official file import` instead. API-fetched data is normalized into the same app schema and uses `source = official_glo_api`.

This feature is for convenience only. It does not change the disclaimer: lottery results are random and no model output guarantees future outcomes.

## Expected schema

The app normalizes both standard files and GLO-style files into this schema:

```csv
date,first_prize,last_2_digits,front_3_1,front_3_2,last_3_1,last_3_2,source
2024-01-17,123456,09,111,222,333,444,official_glo
```

Rules:

- `date` should be a valid draw date.
- `first_prize` should be 6 digits.
- `last_2_digits` should be 2 digits.
- `front_3_1`, `front_3_2`, `last_3_1`, `last_3_2` should be 3 digits.
- Leading zeros are preserved, for example `06`, `009`, and `095`.
- GLO imports set `source` to `official_glo`.

## Troubleshooting import errors

- If the app says a required column is missing, switch the import mode. Use `Standard CSV/Excel schema` for files already using the app schema, and `GLO-style official file import` for official GLO-style exports.
- If Thai column names are not recognized, check that the file has a real header row and is saved as CSV/Excel, not a PDF or screenshot.
- If dates become missing, convert the date column to a normal date format in Excel and upload again.
- If leading zeros disappear before upload, format prize columns as text in Excel before saving.
- If Trust Score is low, do not rely on Prediction Score; clean the data issues first.

## ตัวอย่างไฟล์

ดู `data/sample_thai_lottery.csv`

`data/sample_thai_lottery.csv` is sample data only. It is intentionally small and is meant for checking that the app runs. For serious backtesting, upload a larger official historical file and inspect Data Quality plus Data Trust Score first.

## Screenshots

Add release screenshots with these filenames:

- `screenshots/dashboard.png` - app loaded with sample data, showing title, disclaimer, sidebar settings, and the default dashboard state.
- `screenshots/data-quality.png` - Data Quality tab showing row counts, Trust Score, Calibration Report, and row-level issue table.
- `screenshots/backtest.png` - Backtest tab showing Model Tournament, No Edge warnings, Statistical Significance, and Random Baseline.
- `screenshots/export.png` - Export tab showing the Excel download button and report description.

Use sample or public data only. Do not include private data in screenshots.

After adding screenshots, include them near the top of this README:

```md
![Dashboard](screenshots/dashboard.png)
![Data Quality](screenshots/data-quality.png)
![Backtest](screenshots/backtest.png)
![Export](screenshots/export.png)
```

## Real GLO data validation checklist

Use this before building the optional API fetcher.

1. Download a real historical CSV/Excel file from the official Thai GLO/Open Data source.
2. Save it locally, optionally under `data/real_samples/`. Do not commit real/private downloaded files.
3. Run `streamlit run app.py`.
4. Select `GLO-style official file import` in the sidebar.
5. Upload the real GLO file.
6. Verify the normalized preview:
   - `source` is `official_glo`
   - `date` is parsed correctly
   - `first_prize` stays 6 digits
   - `last_2_digits` stays 2 digits
   - 3-digit prize fields preserve leading zeros such as `009` and `095`
7. Verify Data Quality:
   - missing dates
   - duplicate draw dates
   - invalid `last_2_digits`
   - row-level issue report
8. Verify Calibration Report:
   - imported row count
   - date range
   - missing draw periods
   - invalid prize formats
9. Verify Data Trust Score:
   - official GLO files should usually score higher than manual/sample files
   - low trust warning appears when data is incomplete or malformed
10. Export Excel and confirm these sheets exist:
   - `Raw Data`
   - `Data Quality`
   - `Data Quality Issues`
   - `Data Trust Score`
   - `Calibration Report`
   - `Model Tournament`
   - `Random Baseline Summary`
   - `Statistical Significance`
   - `Disclaimer`

Issues to watch for:

- Thai column names not recognized by the alias map.
- Date columns exported as Thai/Buddhist calendar years or text.
- Leading zeros stripped by Excel before upload.
- Multiple rows per draw date that require reshaping before import.
- Gaps caused by missing draws in the downloaded file rather than real missing periods.
- Low sample size causing weak backtest and wide confidence intervals.

## หลักการ Backtest

Rolling Backtest:

- งวดที่ N ใช้เฉพาะข้อมูลก่อนงวด N เท่านั้น
- โมเดลเลือกเลขตามจำนวนที่กำหนด เช่น 5 เลข
- ถ้าเลขจริงอยู่ในชุดที่เลือก = hit
- เทียบกับ Random Baseline ทุกครั้ง

## Model Tournament ใน V1

- Random
- Hot Frequency
- Cold Frequency
- Gap Overdue
- Recent Trend
- Digit-Level
- Hybrid

## สิ่งที่ยังไม่ได้ทำใน V1

ดูรายละเอียดใน `TODO_FOR_CODEX.md`

## Common errors and fixes

- `ModuleNotFoundError`: activate the virtual environment and run `pip install -r requirements.txt`.
- Upload succeeds but rows are missing dates: check the date column format in the spreadsheet and upload again.
- Leading zeros disappeared: format prize columns as text before saving CSV/Excel.
- GLO columns are not recognized: choose `GLO-style official file import` and make sure the file has a real header row.
- Trust Score is low: clean missing dates, invalid prize values, duplicate draw dates, and source labels before using analysis outputs.
- Excel export fails: close any already-open `lottery_backtest_report.xlsx` file and try again.

## Limitations

- The app does not predict guaranteed winning numbers.
- Backtest performance does not guarantee future outcomes.
- V1 does not include live GLO API fetching.
- V1 does not include React, database persistence, Lao lottery support, or 1M Monte Carlo simulation.
- Missing draw period detection is gap-based and may need an official draw calendar for final verification.
- Statistical significance depends heavily on sample size and data quality.

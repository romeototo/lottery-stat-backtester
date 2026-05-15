# Lottery Stat Backtester

Local Streamlit app for Thai lottery historical-data validation, statistical backtesting, random-baseline comparison, and Excel reporting.

โปรแกรมวิเคราะห์สถิติหวยไทยแบบรันในเครื่อง เน้นตรวจคุณภาพข้อมูล ทดสอบย้อนหลัง และส่งออกรายงาน Excel

> Disclaimer: หวยเป็นเหตุการณ์สุ่ม ไม่มีวิธีใดรับประกันผลลัพธ์ได้ โปรแกรมนี้ใช้เพื่อการศึกษาเชิงสถิติ การทดสอบโมเดล และการคุมความเสี่ยงเท่านั้น

## Badges

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-V1%20Release%20Candidate-orange)

## GitHub project description

Thai lottery statistical backtester with GLO-style file import, data quality checks, trust scoring, random-baseline comparison, and Excel export.

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

- `screenshots/dashboard.png` - first screen with sample data loaded.
- `screenshots/data-quality.png` - Data Quality tab with Trust Score.
- `screenshots/backtest.png` - Backtest tab with No Edge warnings and Random Baseline.
- `screenshots/export.png` - Export tab with Excel download.

Use sample or public data only. Do not include private data in screenshots.

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

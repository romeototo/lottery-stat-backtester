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

## ✨ Key Features (เป้าหมายของ V1)

- 📁 **Upload CSV / Excel**: รองรับไฟล์ข้อมูลจาก GLO
- 🛡️ **Data Quality Check**: ตรวจสอบคุณภาพข้อมูลแบบ Row-level
- 📊 **Statistical Analysis**: Frequency Analysis, Gap Analysis, และ Digit-Level Analysis
- 🔄 **Rolling Backtest**: ระบบทดสอบย้อนหลัง (ป้องกัน Look-ahead bias)
- 🤖 **Model Tournament**: เปรียบเทียบโมเดลทางสถิติกับ Random Baseline
- 💰 **Risk Calculator**: คำนวณงบประมาณและโอกาสขาดทุน (Expected Loss)
- 📑 **Excel Export**: ส่งออกรายงานสถิติแบบครบถ้วน

> *Note: V1 focuses on Thai lottery data only. Lao lottery support is planned for future releases.*

## 🚀 Getting Started (วิธีติดตั้งและใช้งาน)

```bash
# 1. Clone or navigate to the project directory
cd lottery-stat-backtester

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the environment
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal. The app loads `data/sample_thai_lottery.csv` automatically if no file is uploaded.

> ⚠️ **Reminder:** หวยเป็นเหตุการณ์สุ่ม ไม่มีวิธีใดรับประกันผลลัพธ์ได้ ฟังก์ชัน Backtest และ Prediction Score มีไว้เพื่อการศึกษาและประเมินความเสี่ยงเท่านั้น

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

## 📸 Screenshots

*(Screenshots will be added here in the next release)*
<!-- 
![Dashboard](screenshots/dashboard.png)
![Data Quality](screenshots/data-quality.png)
![Backtest](screenshots/backtest.png)
![Export](screenshots/export.png) 
-->

## 🧠 Backtest Methodology (หลักการ Backtest)

**Rolling Backtest:**
- งวดที่ N จะถูกทดสอบโดยใช้เฉพาะข้อมูลประวัติศาสตร์ **ก่อนหน้า** งวด N เท่านั้น (ป้องกัน Look-ahead bias)
- โมเดลจะเลือกตัวเลขตามจำนวนที่กำหนด (เช่น 5 เลข)
- หากเลขที่ออกจริงอยู่ในชุดที่โมเดลเลือก จะนับเป็น **Hit**
- ผลลัพธ์จะถูกนำไปเปรียบเทียบกับ **Random Baseline** เสมอ เพื่อตรวจสอบว่าโมเดลมี Edge หรือมีความน่าจะเป็นที่เหนือกว่าการสุ่มหรือไม่

### 🏆 Model Tournament ใน V1
โมเดลที่เปิดให้ทดสอบในเวอร์ชันนี้ประกอบด้วย:
- **Random** (Baseline สำหรับเปรียบเทียบ)
- **Hot Frequency** (เลขที่ออกบ่อย)
- **Cold Frequency** (เลขที่ออกน้อย/เลขดับ)
- **Gap Overdue** (เลขที่ทิ้งช่วงนาน)
- **Recent Trend** (แนวโน้มระยะสั้น)
- **Digit-Level** (สถิติรายหลัก)
- **Hybrid** (โมเดลผสมผสาน)

## 🗺️ Roadmap (สิ่งที่ยังไม่ได้ทำใน V1)

ดูรายละเอียดฟีเจอร์ในอนาคตได้ในไฟล์ [`TODO_FOR_CODEX.md`](TODO_FOR_CODEX.md)

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

# Changelog

> Disclaimer: หวยเป็นเหตุการณ์สุ่ม ไม่มีวิธีใดรับประกันผลลัพธ์ได้ โปรแกรมนี้ใช้เพื่อการศึกษาเชิงสถิติ การทดสอบโมเดล และการคุมความเสี่ยงเท่านั้น

## V1 Release Polish

- Added GitHub-ready project description and badges.
- Added `.gitignore` for Python, Streamlit, virtualenvs, caches, local sample files, and generated reports.
- Added MIT license.
- Added screenshot placeholder instructions under `screenshots/`.
- Clarified sample data status and release limitations.
- Removed generated local Streamlit logs from the working tree.

## Phase 6 - V1 Stabilization

- Added V1 release checklist.
- Improved Streamlit labels and tab explanations.
- Added clearer No Edge warnings for models that do not beat random baseline p95.
- De-emphasized Prediction Score when Trust Score is low.
- Expanded README with quick start, screenshots placeholder, sample data, common errors, and limitations.
- Added release stability tests.

## Phase 5 - Real Data Validation

- Added real sample workflow in `data/real_samples/`.
- Hardened GLO-style CSV/Excel importer.
- Preserved leading zeros across prize fields.
- Added calibration report and export sheets.
- Added synthetic GLO CSV/Excel tests.

## Phase 4 - Trust Scoring

- Added GLO importer module.
- Added Data Trust Score and High/Medium/Low labels.
- Added low-trust warning logic.
- Added Data Trust Score Excel sheet.

## Phase 3 - Statistical Reports and Charts

- Added row-level Data Quality issue report.
- Added Random Baseline summary and model comparison against random p95.
- Added binomial p-values and confidence intervals.
- Added Streamlit charts and Excel chart sheet.

## Phase 2 - Foundation Fixes

- Fixed `invalid_last_2_digits` counting.
- Preserved leading zeros.
- Replaced deprecated Streamlit `use_container_width` usage.
- Added foundation tests.

## Phase 1 - Base App Verification

- Extracted project.
- Installed dependencies.
- Ran Streamlit app successfully.
- Confirmed no startup-breaking errors before larger changes.

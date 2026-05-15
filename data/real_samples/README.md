# Real GLO Sample Files

Place downloaded Thai Government Lottery Office (GLO) Open Data CSV or Excel files in this folder when you want to test real historical data locally.

Do not commit private or machine-specific files here. The app can import files from any upload location through Streamlit, so this folder is only a convenient local staging area.

Recommended workflow:

1. Download a CSV or Excel file from the official GLO/Open Data source.
2. Save it in this folder, for example `glo-results-2020-2026.xlsx`.
3. Run the app with `streamlit run app.py`.
4. In the sidebar, choose `GLO-style official file import`.
5. Upload the downloaded file and inspect the normalized preview, calibration report, and trust score before using any analysis tabs.

Reminder: หวยเป็นเหตุการณ์สุ่ม ไม่มีวิธีใดรับประกันผลลัพธ์ได้ โปรแกรมนี้ใช้เพื่อการศึกษาเชิงสถิติ การทดสอบโมเดล และการคุมความเสี่ยงเท่านั้น

# TODO for Codex / Antigravity

เอกสารนี้คือสิ่งที่ควรทำต่อหลังจาก V1 ใช้งานได้

## Priority 1 — ต้องทำก่อน

### 1. ต่อข้อมูลจริงจาก GLO API
- เพิ่ม fetcher สำหรับสำนักงานสลากกินแบ่งรัฐบาล
- ดึงข้อมูลตามวันที่ออกรางวัล
- Validate กับ schema:
  - date
  - first_prize
  - last_2_digits
  - front_3_1
  - front_3_2
  - last_3_1
  - last_3_2
  - source

### 2. เพิ่ม Data Quality แบบเข้มขึ้น
- ตรวจวันหวยไทย: ต้องเป็นวันที่ 1 / 16 หรือวันที่เลื่อนจริง
- ตรวจเลข leading zero เช่น 06 ต้องไม่กลายเป็น 6
- ตรวจ duplicate ตาม date
- ตรวจ missing period
- เพิ่ม report ว่าข้อมูลเชื่อถือได้แค่ไหน

### 3. ทำ Backtest ให้เร็วขึ้น
- ใช้ vectorization เพิ่ม
- เก็บผล intermediate
- เพิ่ม progress bar เวลา backtest ยาว

### 4. เพิ่ม Random Baseline หลายรอบ
ตอนนี้ baseline เป็นแบบ deterministic/simple random ต่อรอบ
ควรเพิ่ม:
- random_runs = 1,000 หรือ 10,000
- ค่าเฉลี่ย hit rate
- percentile 5/50/95
- z-score ว่าโมเดลชนะสุ่มจริงไหม

## Priority 2 — เพิ่มความน่าเชื่อถือ

### 5. Statistical Significance
เพิ่ม:
- binomial test
- confidence interval ของ hit rate
- p-value ว่าโมเดลชนะ random จริงไหม

### 6. Walk-Forward Validation
Train 5 ปี → Test 1 ปี แล้วเลื่อนไปเรื่อย ๆ

ตัวอย่าง:
- Train 2559–2563 → Test 2564
- Train 2560–2564 → Test 2565

### 7. Overfitting Detector
เตือนเมื่อ:
- train hit rate สูงผิดปกติ
- test hit rate ต่ำกว่า random
- โมเดลดีเฉพาะช่วงเดียว

### 8. Monte Carlo 1,000,000 ครั้ง
ทำเป็น option เพราะใช้เวลานาน
ควรมี:
- pure random simulation
- weighted simulation from model score
- compare distribution

## Priority 3 — ฟีเจอร์ใช้งานจริง

### 9. Budget / Bankroll Rules
เพิ่ม:
- งบต่อเดือน
- งบต่องวด
- max loss
- stop-loss
- ห้ามไล่ทุน
- expected loss per month

### 10. Export Report ดีขึ้น
เพิ่ม Excel sheets:
- Raw Data
- Data Quality
- Frequency
- Gap
- Digit Analysis
- Backtest Details
- Model Tournament
- Random Baseline
- Budget Risk
- Prediction Summary

### 11. Chart UI
เพิ่มกราฟ:
- frequency bar chart
- gap bar chart
- model hit rate comparison
- cumulative profit/loss curve
- random baseline distribution

## Priority 4 — React Version

หลังจาก logic เสถียรแล้ว ค่อยแยกเป็น:

```text
backend/
  FastAPI
frontend/
  React + Chart.js
```

API ที่ควรมี:
- POST /upload
- GET /data-quality
- GET /frequency
- GET /gap
- POST /backtest
- POST /prediction
- POST /export-excel

## Priority 5 — หวยลาว

เพิ่มหวยลาวทีหลัง เพราะต้องจัดการแหล่งข้อมูลให้ดี

ต้องมี:
- source_url
- fetched_at
- trust_level
- data_validation
- warning ถ้าไม่ใช่แหล่งทางการ

## Warning ที่ต้องโชว์ในโปรแกรมทุกหน้า

หวยเป็นเหตุการณ์สุ่ม ไม่มีวิธีใดรับประกันผลลัพธ์ได้
ผล Backtest ไม่ได้รับประกันผลลัพธ์ในอนาคต
โปรแกรมนี้ใช้เพื่อการศึกษาและการคุมความเสี่ยงเท่านั้น

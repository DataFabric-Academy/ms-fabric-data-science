# FreshMart Labs — Microsoft Fabric Data Science

ชุดปฏิบัติการสำหรับ **นักวิเคราะห์ข้อมูลที่อยากเข้าใจวงจรงานวิทยาศาสตร์ข้อมูล**  
กรณีศึกษา: **FreshMart Customer Churn** — สำรวจข้อมูล เตรียมฟีเจอร์ ฝึกโมเดลด้วย MLflow แล้วเขียนผลลงตาราง Gold สำหรับแคมเปญรักษาลูกค้า

| เอกสารช่วยเรียน | ลิงก์ |
| --- | --- |
| Docs ทฤษฎี | [../docs/README.md](../docs/README.md) |
| อภิธานศัพท์ | [../docs/glossary.md](../docs/glossary.md) |
| มาตรฐานภาษาไทย | [../docs/writing-style-th.md](../docs/writing-style-th.md) |

## เส้นทางผู้เรียน

1. ลงทะเบียน [Fabric Trial](https://aka.ms/fabrictrial) ด้วยบัญชีของตนเอง
2. `git clone` repository นี้
3. สร้าง workspace ของตนเองบน Fabric (แนะนำชื่อ **`labs`**) — **อย่าเชิญใครเข้า**
4. สร้าง Lakehouse **`lh_freshmart`** แล้วอัปโหลด CSV จาก `labs/data/` ตาม [Lab 0](instructions/00-lakehouse-setup.md)
5. Import notebook จาก `labs/notebooks/` แล้วแนบ Default Lakehouse = **`lh_freshmart`**
6. ทำตามคู่มือใน `labs/instructions/` — รันทีละขั้น ดูผล แล้วไปต่อ

## Workspace ของผู้เรียน

แต่ละคนใช้ Trial และ workspace ของตนเอง ไม่มี workspace ร่วม และไม่มีคำเชิญเข้า workspace ของผู้อื่น

| รายการ | ค่า |
| --- | --- |
| Capacity | Fabric Trial ของตนเอง (หรือ Capacity ที่รองรับ Fabric) |
| Workspace | สร้างเอง แนะนำชื่อ `labs` |
| Lakehouse | สร้างเอง ชื่อ `lh_freshmart` (เปิด Lakehouse schemas) |
| ข้อมูลเริ่มต้น | อัปโหลด `labs/data/*.csv` ไปที่ `Files/raw/` แล้วรันเซลล์สร้างตาราง Bronze ใน Lab 0 |

ถ้ามี lakehouse เก่าที่ยังใช้ชื่อตารางแบบเดิม (เช่น `bronze_transactions`) ดู [instructions/instructor-migrate-schemas.md](instructions/instructor-migrate-schemas.md)

## ลำดับแล็บ

| Lab | คู่มือ | Notebook | ผลลัพธ์ที่ควรได้ |
| --- | --- | --- | --- |
| 0 | [00-lakehouse-setup.md](instructions/00-lakehouse-setup.md) | `00-environment-verification.ipynb` | สร้าง workspace ของตนเอง + `lh_freshmart` แล้วผ่านจุดตรวจอัตโนมัติ |
| 1 | [01-explore-data.md](instructions/01-explore-data.md) | `01-explore-data.ipynb` | สำรวจของเสียและพฤติกรรมลูกค้าที่เลิกซื้อ (Churn) |
| 2 | [02-preprocess-data-wrangler.md](instructions/02-preprocess-data-wrangler.md) | `02-preprocess-data-wrangler.ipynb` | ใช้ Data Wrangler และได้ `silver.customer_features` พร้อมไฟล์ params |
| 3 | [03-train-track-mlflow.md](instructions/03-train-track-mlflow.md) | `03-train-track-mlflow.ipynb` | มี Experiment และโมเดล `freshmart-churn-model` |
| 4 | [04-batch-predict.md](instructions/04-batch-predict.md) | `04-batch-predict.ipynb` | ได้ตาราง `gold.freshmart_predictions` สำหรับแคมเปญ |

Checklist รันบนหน้าจอ Lab 0–2: [run-checklist-lab0-2.md](instructions/run-checklist-lab0-2.md)

## ข้อมูลที่ใช้

อยู่ที่ `Files/raw/` ของ Lakehouse และสำเนาใน `labs/data/`

- `freshmart_transactions.csv` — 3,000 แถว (ยอดขายและของเสีย)
- `freshmart_customers.csv` — 1,500 แถว (สมาชิกและสถานะ Churn)
- `freshmart_scoring_batch.csv` — 200 แถว (ชุดทำนาย — ไม่มีคอลัมน์ Churn)

## หลักการออกแบบ

- ขั้นตอนเป็นลำดับเลข รันโค้ดแล้วเห็นผล — ไม่บังคับจำทฤษฎีก่อนลงมือ
- ใช้ Data Wrangler แล้วกด **Add code to notebook** ได้จริง (ส่วน A ของ Lab 2)
- เรื่องราวธุรกิจต่อเนื่องจนถึงแคมเปญรักษาลูกค้า (Lab 4)
- จุดตรวจใช้ตัวเลขจริงจากชุดข้อมูล (3,000 / 1,500 / 200, Age ว่าง 37, Churn ประมาณ 19.3%)
- Notebook มีทางเลือกสำรอง (fallback) อ่าน CSV เมื่อตารางหรือ Spark ยังไม่พร้อม — ดู [glossary](../docs/glossary.md#fallback)

## ทดสอบก่อนขึ้นห้องเรียน (ผู้สอน)

```powershell
pip install -r labs/requirements-test.txt
pytest labs/tests -v
python labs/scripts/run_local_pipeline.py
```

เกณฑ์ผ่านขั้นต่ำ: `pytest` ผ่าน สคริปต์พิมพ์ `LOCAL PIPELINE OK` คะแนน AUC ของ Random Forest ประมาณ 0.86 สูงกว่า Decision Tree ประมาณ 0.77 และไฟล์ Gold ท้องถิ่นมี 200 แถว  
(AUC คือคะแนนแยกกลุ่ม churn — ดู [glossary](../docs/glossary.md#auc-area-under-the-roc-curve))

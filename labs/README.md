# FreshMart Labs — Microsoft Fabric Data Science

ชุดปฏิบัติการสำหรับ **นักวิเคราะห์ข้อมูลที่อยากเข้าใจวงจรงานวิทยาศาสตร์ข้อมูล**  
กรณีศึกษา: **FreshMart Customer Churn** — สำรวจข้อมูล เตรียมฟีเจอร์ ฝึกโมเดลด้วย MLflow แล้วเขียนผลลงตาราง Gold สำหรับแคมเปญรักษาลูกค้า

| เอกสารช่วยเรียน | ลิงก์ |
| --- | --- |
| Docs ทฤษฎี | [../docs/README.md](../docs/README.md) |
| อภิธานศัพท์ | [../docs/glossary.md](../docs/glossary.md) |
| มาตรฐานภาษาไทย | [../docs/writing-style-th.md](../docs/writing-style-th.md) |

## เส้นทางผู้เรียน

1. `git clone` repository นี้
2. เปิด workspace **`labs`** บน Fabric
3. Import notebook จาก `labs/notebooks/`
4. แนบ Default Lakehouse = **`lh_freshmart`**
5. ทำตามคู่มือใน `labs/instructions/` — รันทีละขั้น ดูผล แล้วไปต่อ

## Workspace ห้องเรียน

| รายการ | ค่า |
| --- | --- |
| Workspace | `labs` |
| Lakehouse | `lh_freshmart` |
| Portal | [เปิด workspace labs](https://app.fabric.microsoft.com/groups/56c1925e-a9e9-44ec-9834-b64b6b07a4ad) |

ผู้สอนเตรียมไว้แล้ว: ไฟล์ `Files/raw/*.csv` และตาราง Bronze (`bronze.transactions`, `bronze.customers`)

ถ้า workspace ยังใช้ชื่อตารางแบบเดิม (เช่น `bronze_transactions`) ดู [instructions/instructor-migrate-schemas.md](instructions/instructor-migrate-schemas.md)

## ลำดับแล็บ

| Lab | คู่มือ | Notebook | ผลลัพธ์ที่ควรได้ |
| --- | --- | --- | --- |
| 0 | [00-lakehouse-setup.md](instructions/00-lakehouse-setup.md) | `00-environment-verification.ipynb` | เปิด `labs` และ `lh_freshmart` ได้ และผ่านจุดตรวจอัตโนมัติ |
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

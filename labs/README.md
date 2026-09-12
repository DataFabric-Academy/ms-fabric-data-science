# FreshMart Labs — Microsoft Fabric Data Science

ชุดปฏิบัติการสำหรับ **Analyst ที่อยากเข้าใจ Data Science**  
กรณีศึกษา: **FreshMart Customer Churn** — สำรวจข้อมูล เตรียมฟีเจอร์ ฝึกโมเดลด้วย MLflow แล้วเขียนผลลงตาราง Gold สำหรับแคมเปญรักษาลูกค้า

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

Instructor provision ไว้แล้ว: `Files/raw/*.csv` และตาราง Bronze

## ลำดับแล็บ

| Lab | คู่มือ | Notebook | ผลลัพธ์ |
| --- | --- | --- | --- |
| 0 | [00-lakehouse-setup.md](instructions/00-lakehouse-setup.md) | `00-environment-verification.ipynb` | เปิด `labs` + `lh_freshmart` + จุดตรวจผ่าน |
| 1 | [01-explore-data.md](instructions/01-explore-data.md) | `01-explore-data.ipynb` | EDA ของเสีย + Churn |
| 2 | [02-preprocess-data-wrangler.md](instructions/02-preprocess-data-wrangler.md) | `02-preprocess-data-wrangler.ipynb` | Wrangler + `silver_customer_features` + params |
| 3 | [03-train-track-mlflow.md](instructions/03-train-track-mlflow.md) | `03-train-track-mlflow.ipynb` | Experiment + `freshmart-churn-model` |
| 4 | [04-batch-predict.md](instructions/04-batch-predict.md) | `04-batch-predict.ipynb` | `gold_freshmart_predictions` |

Checklist รัน UI Lab 0–2: [run-checklist-lab0-2.md](instructions/run-checklist-lab0-2.md)

## ข้อมูลที่ใช้

อยู่ที่ `Files/raw/` ของ Lakehouse และสำเนาใน `labs/data/`

- `freshmart_transactions.csv` — 3,000 แถว (ยอดขาย/ของเสีย)
- `freshmart_customers.csv` — 1,500 แถว (สมาชิก + Churn)
- `freshmart_scoring_batch.csv` — 200 แถว (ชุดทำนาย ไม่มี Churn)

## หลักการออกแบบ

- ขั้นตอนเป็นลำดับเลข + รันโค้ด + เห็นผล — ไม่บังคับจำทฤษฎี
- ใช้ Data Wrangler แล้ว **Add code to notebook** ได้จริง (ส่วน A ของ Lab 2)
- เรื่องราวธุรกิจต่อเนื่องจนถึงแคมเปญรักษาลูกค้า (Lab 4)
- จุดตรวจใช้ตัวเลขจริงจากชุดข้อมูล (3,000 / 1,500 / 200, Age ว่าง 37, Churn ~19.3%)
- Notebook มี fallback อ่าน CSV เมื่อตาราง/Spark ยังไม่พร้อม

## ทดสอบก่อนขึ้นห้องเรียน (instructor)

```powershell
pip install -r labs/requirements-test.txt
pytest labs/tests -v
python labs/scripts/run_local_pipeline.py
```

จุดผ่านขั้นต่ำ: `pytest` ผ่าน, สคริปต์พิมพ์ `LOCAL PIPELINE OK`, RF AUC ≈ 0.86 > DT ≈ 0.77, ไฟล์ Gold ท้องถิ่นมี 200 แถว

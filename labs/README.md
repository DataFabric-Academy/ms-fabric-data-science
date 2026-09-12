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

> [!IMPORTANT]
> **กติกาสำคัญสำหรับการใช้งานห้องปฏิบัติการ (Single-User Workspace Rule):**  
> แต่ละท่านต้องใช้ **Fabric Trial และ Workspace ส่วนตัวของตนเอง** (แนะนำให้ตั้งชื่อว่า `labs`)  
> **ห้ามเชิญเพื่อนร่วมคลาสหรือผู้สอนเข้า Workspace โดยเด็ดขาด** เพื่อป้องกันปัญหา Spark Session ชนกัน และป้องกันการแย่งโควตา Capacity ของกันและกัน

## แผนผังลำดับการลงมือปฏิบัติ (Lab Pipeline)

```mermaid
flowchart TD
    subgraph Lab0["Lab 0: เตรียมสภาพแวดล้อม"]
        L0["สร้าง lh_freshmart (เปิด Schemas)<br/>อัปโหลด CSV 3 ไฟล์สู่ Files/raw/<br/>สร้างตาราง bronze.transactions & customers"]
    end

    subgraph Lab1["Lab 1: สำรวจข้อมูล (EDA)"]
        L1["วิเคราะห์ของเสีย & Churn Rate (~19.3%)<br/>ตรวจพบ Age ว่าง 37 รายการ<br/>พล็อตกราฟ Correlation & Distribution"]
    end

    subgraph Lab2["Lab 2: เตรียมฟีเจอร์ด้วย Data Wrangler"]
        L2["คลิกทำความสะอาดผ่าน UI แล้ว Add Code<br/>บันทึก feature_params.json ป้องกัน Data Leakage<br/>สร้างตาราง silver.customer_features"]
    end

    subgraph Lab3["Lab 3: ฝึกและติดตามโมเดลด้วย MLflow"]
        L3["Experiment: freshmart-churn<br/>Run 1: Decision Tree (AUC ≈ 0.77)<br/>Run 2: Random Forest (AUC ≈ 0.86 ⭐)<br/>ลงทะเบียน Champion สู่ Model Registry"]
    end

    subgraph Lab4["Lab 4: ทำนายผลเป็นชุดสู่ Gold"]
        L4["โหลด Scoring Batch 200 รายการ<br/>รันฟังก์ชัน PREDICT บน Spark<br/>เขียนผลลง gold.freshmart_predictions<br/>พร้อมส่งต่อแดชบอร์ด Power BI"]
    end

    Lab0 --> Lab1 --> Lab2 --> Lab3 --> Lab4

    style Lab0 fill:#f9fbe7,stroke:#827717
    style Lab1 fill:#e0f2f1,stroke:#004d40
    style Lab2 fill:#e1f5fe,stroke:#01579b
    style Lab3 fill:#f3e5f5,stroke:#4a148c
    style Lab4 fill:#fff8e1,stroke:#ff6f00
```

## ลำดับแล็บและผลลัพธ์ที่คาดหวัง

| Lab | คู่มือปฏิบัติ | สมุดโค้ด (Notebook) | ผลลัพธ์ที่ส่งมอบ (Key Deliverable) |
| :---: | :--- | :--- | :--- |
| **0** | [00-lakehouse-setup.md](instructions/00-lakehouse-setup.md) | `00-environment-verification.ipynb` | Workspace ส่วนตัว + `lh_freshmart` พร้อมตาราง Bronze ผ่านการทดสอบ |
| **1** | [01-explore-data.md](instructions/01-explore-data.md) | `01-explore-data.ipynb` | รายงานสถิติและกราฟพฤติกรรม Churn ของลูกค้า FreshMart |
| **2** | [02-preprocess-data-wrangler.md](instructions/02-preprocess-data-wrangler.md) | `02-preprocess-data-wrangler.ipynb` | ตาราง `silver.customer_features` และไฟล์ `feature_params.json` |
| **3** | [03-train-track-mlflow.md](instructions/03-train-track-mlflow.md) | `03-train-track-mlflow.ipynb` | Experiment เปรียบเทียบสองโมเดล และ Champion `freshmart-churn-model` |
| **4** | [04-batch-predict.md](instructions/04-batch-predict.md) | `04-batch-predict.ipynb` | ตาราง Delta `gold.freshmart_predictions` สำหรับทีมการตลาด |


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

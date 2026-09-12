# FreshMart Labs — Microsoft Fabric Data Science

ชุดปฏิบัติการสำหรับ **นักวิเคราะห์ข้อมูลที่อยากเข้าใจวงจรงานวิทยาศาสตร์ข้อมูล**  
กรณีศึกษา: **FreshMart Customer Churn** — สำรวจข้อมูล เตรียมฟีเจอร์ ฝึกโมเดลด้วย MLflow แล้วเขียนผลลงตาราง Gold สำหรับแคมเปญรักษาลูกค้า

| เอกสารช่วยเรียน | ลิงก์ |
| --- | --- |
| Docs ทฤษฎี | [../docs/README.md](../docs/README.md) |
| อภิธานศัพท์ | [../docs/glossary.md](../docs/glossary.md) |
| มาตรฐานภาษาไทย | [../docs/writing-style-th.md](../docs/writing-style-th.md) |
| AutoML (ทางเลือก) | [../docs/09-automl.md](../docs/09-automl.md) · [Demo ผู้สอน](instructions/instructor-automl-demo.md) |

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
    subgraph Lab0 ["Lab 0: เตรียมสภาพแวดล้อม"]
        L0["<b>Lab 0: ตั้งค่าสภาพแวดล้อม</b><br/>• สร้าง Lakehouse lh_freshmart (เปิด Schemas)<br/>• อัปโหลด CSV สู่ Files/raw/<br/>• สร้างตาราง Delta ใน schema bronze"]
    end

    subgraph Lab1 ["Lab 1: สำรวจข้อมูล (EDA)"]
        L1["<b>Lab 1: สำรวจข้อมูลเบื้องต้น</b><br/>• วิเคราะห์ยอดขายและอัตรา Churn (~19.3%)<br/>• ตรวจพบค่าว่าง Age 37 ค่า<br/>• ตรวจสอบสหสัมพันธ์ ป้องกัน Data Leakage"]
    end

    subgraph Lab2 ["Lab 2: เตรียมฟีเจอร์ด้วย Data Wrangler"]
        L2["<b>Lab 2: วิศวกรรมฟีเจอร์</b><br/>• ใช้ Data Wrangler แบบ Interactive<br/>• บันทึก feature_params.json ป้องกันข้อมูลรั่วไหล<br/>• เขียนตาราง silver.customer_features"]
    end

    subgraph Lab3 ["Lab 3: ฝึกและติดตามโมเดลด้วย MLflow"]
        L3["<b>Lab 3: การทดลองและคัดเลือกโมเดล</b><br/>• ทดลอง Decision Tree (AUC ≈ 0.77)<br/>• ทดลอง Random Forest (AUC ≈ 0.86 ⭐)<br/>• ลงทะเบียน Champion สู่ Model Registry"]
    end

    subgraph Lab4 ["Lab 4: ทำนายผลเป็นชุดสู่ Gold"]
        L4["<b>Lab 4: ทำนายผลเป็นชุด (Batch Scoring)</b><br/>• ทำนายลูกค้าใหม่ 200 รายด้วยฟังก์ชัน PREDICT<br/>• เขียนคะแนนความเสี่ยงลง gold.freshmart_predictions<br/>• เชื่อมต่อรายงาน Power BI ด้วย Direct Lake"]
    end

    Lab0 --> Lab1 --> Lab2 --> Lab3 --> Lab4

    classDef stage fill:#f8fafc,stroke:#475569,stroke-width:2px,color:#0f172a;
    classDef node0 fill:#ffffff,stroke:#65a30d,stroke-width:2px,color:#1a2e05;
    classDef node1 fill:#f0fdfa,stroke:#0d9488,stroke-width:2px,color:#134e4a;
    classDef node2 fill:#f0fdf4,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef node3 fill:#eff6ff,stroke:#2563eb,stroke-width:2px,color:#1e3a8a;
    classDef node4 fill:#fffbeb,stroke:#d97706,stroke-width:2px,color:#78350f;

    class Lab0,Lab1,Lab2,Lab3,Lab4 stage;
    class L0 node0;
    class L1 node1;
    class L2 node2;
    class L3 node3;
    class L4 node4;
```

## ลำดับแล็บและผลลัพธ์ที่คาดหวัง

| Lab | คู่มือปฏิบัติ | สมุดโค้ด (Notebook) | ผลลัพธ์ที่ส่งมอบ (Key Deliverable) |
| :---: | :--- | :--- | :--- |
| **0** | [00-lakehouse-setup.md](instructions/00-lakehouse-setup.md) | `00-environment-verification.ipynb` | Workspace ส่วนตัว + `lh_freshmart` พร้อมตาราง Bronze ผ่านการทดสอบ |
| **1** | [01-explore-data.md](instructions/01-explore-data.md) | `01-explore-data.ipynb` | รายงานสถิติและกราฟพฤติกรรม Churn ของลูกค้า FreshMart |
| **2** | [02-preprocess-data-wrangler.md](instructions/02-preprocess-data-wrangler.md) | `02-preprocess-data-wrangler.ipynb` | ตาราง `silver.customer_features` และไฟล์ `feature_params.json` |
| **3** | [03-train-track-mlflow.md](instructions/03-train-track-mlflow.md) | `03-train-track-mlflow.ipynb` | Experiment เปรียบเทียบสองโมเดล และ Champion `freshmart-churn-model` |
| **4** | [04-batch-predict.md](instructions/04-batch-predict.md) | `04-batch-predict.ipynb` | ตาราง Delta `gold.freshmart_predictions` สำหรับทีมการตลาด |

## สำหรับผู้สอน (ทางเลือก หลัง Lab 3)

สาธิต AutoML บน workspace ของผู้สอนเท่านั้น ผู้เรียนดู ไม่รันตามทั้งคลาส และห้ามทับ `freshmart-churn-model`

| เอกสาร | ใช้เมื่อ |
| :--- | :--- |
| ทฤษฎี [09-automl.md](../docs/09-automl.md) | อธิบายว่า AutoML ทำอะไรให้ และอะไรยังเป็นหน้าที่คน |
| คู่มือ [instructor-automl-demo.md](instructions/instructor-automl-demo.md) | เดินตัวช่วย Quick Prototype 8–12 นาที ก่อนเข้า Lab 4 |


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

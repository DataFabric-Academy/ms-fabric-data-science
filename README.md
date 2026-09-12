# Microsoft Fabric Data Science — FreshMart Labs

![Status](https://img.shields.io/badge/status-active-2ea44f)
![License](https://img.shields.io/github/license/DataFabric-Academy/ms-fabric-data-science)
![Release](https://img.shields.io/github/v/release/DataFabric-Academy/ms-fabric-data-science?display_name=tag)
![Microsoft Fabric](https://img.shields.io/badge/platform-Microsoft%20Fabric-742774)

Repository ชุดปฏิบัติการวิทยาศาสตร์ข้อมูลบน Microsoft Fabric ผ่านกรณีศึกษา **FreshMart Customer Churn** (ภารกิจกู้วิกฤตยอดขาย ทำนายลูกค้าที่จะเลิกซื้อ เพื่อส่งแคมเปญรักษาลูกค้าได้ทันเวลา)  
- **กลุ่มเป้าหมาย:** นักวิเคราะห์ข้อมูล (Data Analyst) และผู้สนใจที่ต้องการเข้าใจวงจรงานวิทยาศาสตร์ข้อมูลบน Fabric ครบวงจร  
- **หลักสูตรอ้างอิง:** [Implement a data science and machine learning solution for AI in Microsoft Fabric](https://learn.microsoft.com/training/paths/implement-data-science-machine-learning-fabric/) (พร้อมเนื้อหาสไลด์ภาษาไทยฉบับ Instructor Edition)

```mermaid
flowchart LR
    subgraph S1["1. ข้อมูลดิบ"]
        CSV["CSV Transactions & Customers<br/>(Files/raw/)"]
    end

    subgraph S2["2. OneLake & Medallion"]
        B["Bronze<br/>(bronze.customers / transactions)"]
        S["Silver<br/>(silver.customer_features)"]
        G["Gold<br/>(gold.freshmart_predictions)"]
        CSV --> B
        B -->|Lab 2: Data Wrangler| S
    end

    subgraph S3["3. ฝึกและติดตามโมเดล"]
        EXP["Lab 3: MLflow Experiment<br/>(Decision Tree vs Random Forest)"]
        REG["Model Registry<br/>(freshmart-churn-model: Champion)"]
        S -->|Train / Test Split| EXP
        EXP -->|เลือกโมเดลที่ดีที่สุด| REG
    end

    subgraph S4["4. นำไปใช้จริงในธุรกิจ"]
        PRED["Lab 4: Batch Scoring (PREDICT)"]
        PBI["Power BI Report<br/>(Direct Lake: ชี้เป้าลูกค้าเสี่ยง)"]
        REG --> PRED
        S -.->|Scoring Batch| PRED
        PRED --> G
        G --> PBI
    end

    classDef stage fill:#f8f9fa,stroke:#495057,stroke-width:1px;
    classDef highlight fill:#e3f2fd,stroke:#1976d2,stroke-width:2px;
    class S1,S2,S3,S4 stage;
    class REG,G,PBI highlight;
```

## โครงการ (Project)

| รายการ | รายละเอียด |
| --- | --- |
| **License** | [MIT](LICENSE) |
| **Status** | **Active** — พร้อมใช้งานทั้งการเรียนรู้ด้วยตนเองและประกอบการอบรม |
| **Releases** | [Latest release](https://github.com/DataFabric-Academy/ms-fabric-data-science/releases/latest) · [All tags](https://github.com/DataFabric-Academy/ms-fabric-data-science/tags) |
| **Topics** | Microsoft Fabric, MLflow, PySpark, Medallion Architecture, Customer Churn, Power BI Direct Lake |

| เริ่มต้นศึกษา | รายละเอียด | ลิงก์ |
| --- | --- | --- |
| **Docs ทฤษฎีและแนวคิด** | ปูพื้นฐานสถาปัตยกรรม Fabric, วงจร Data Science, และเครื่องมือ | [docs/README.md](docs/README.md) |
| **อภิธานศัพท์ (Glossary)** | รวบรวมคำศัพท์เทคนิคพร้อมคำอธิบายภาษาไทยที่เข้าใจง่าย | [docs/glossary.md](docs/glossary.md) |
| **Labs ลงมือปฏิบัติจริง** | คู่มือและ Notebook ตั้งแต่ Lab 0 ถึง Lab 4 | [labs/README.md](labs/README.md) |

> [!NOTE]
> **เส้นทางผู้เรียน:** ศึกษาเอกสารความรู้ใน [docs](docs/README.md) ตามลำดับโมดูล จากนั้นเปิดใช้งาน Fabric Trial ของตนเอง สร้าง workspace (แนะนำชื่อ `labs`) — **โดยไม่ต้องเชิญผู้อื่นเข้า** — แล้ว `git clone` repository นี้เพื่อนำเข้า Notebook ใน `labs/notebooks/` และแนบ Lakehouse `lh_freshmart` ที่สร้างขึ้น

## ตรวจสอบความพร้อมของแล็บ (Local Verification)

สามารถทดสอบ pipeline ทั้งหมดบนเครื่องของคุณได้ทันทีโดยไม่ต้องต่อ Fabric:

```powershell
pip install -r labs/requirements-test.txt
pytest labs/tests -v
python labs/scripts/run_local_pipeline.py
```

เมื่อการทดสอบผ่านเรียบร้อย ให้เริ่มทำตามคู่มือใน `labs/instructions/` บน Microsoft Fabric ได้ทันที


# Microsoft Fabric Data Science — FreshMart Labs

![Status](https://img.shields.io/badge/status-active-2ea44f)
![License](https://img.shields.io/github/license/DataFabric-Academy/ms-fabric-data-science)
![Release](https://img.shields.io/github/v/release/DataFabric-Academy/ms-fabric-data-science?display_name=tag)
![Microsoft Fabric](https://img.shields.io/badge/platform-Microsoft%20Fabric-742774)

Repository ชุดปฏิบัติการวิทยาศาสตร์ข้อมูลบน Microsoft Fabric ผ่านกรณีศึกษา **FreshMart Customer Churn** (ภารกิจกู้วิกฤตยอดขาย ทำนายลูกค้าที่จะเลิกซื้อ เพื่อส่งแคมเปญรักษาลูกค้าได้ทันเวลา)  
- **กลุ่มเป้าหมาย:** นักวิเคราะห์ข้อมูล (Data Analyst) และผู้สนใจที่ต้องการเข้าใจวงจรงานวิทยาศาสตร์ข้อมูลบน Fabric ครบวงจร  
- **หลักสูตรอ้างอิง:** [Implement a data science and machine learning solution for AI in Microsoft Fabric](https://learn.microsoft.com/training/paths/implement-data-science-machine-learning-fabric/) (พร้อมเนื้อหาสไลด์ภาษาไทยฉบับ Instructor Edition)

```mermaid
flowchart TD
    subgraph S1 ["1. แหล่งข้อมูลดิบ (Landing Zone)"]
        CSV["📄 <b>ไฟล์ข้อมูลดิบ (Files/raw/)</b><br/>freshmart_transactions.csv (3,000 แถว) & customers.csv (1,500 แถว)"]
    end

    subgraph S2 ["2. OneLake & Medallion Architecture (Lakehouse)"]
        B["🥉 <b>Bronze Schema</b><br/>ตาราง Delta ข้อมูลดิบ bronze.transactions & customers (Lab 0)"]
        S["🥈 <b>Silver Schema</b><br/>ตารางฟีเจอร์ silver.customer_features (Lab 2: Data Wrangler)"]
        B -->|ทำความสะอาด & สเกลฟีเจอร์| S
    end

    subgraph S3 ["3. การเรียนรู้ของเครื่อง (Data Science & MLflow)"]
        EXP["🧪 <b>MLflow Experiment: freshmart-churn</b><br/>เปรียบเทียบ Decision Tree (AUC ≈ 0.77) vs Random Forest (AUC ≈ 0.86 ⭐)"]
        REG["🏆 <b>Model Registry: freshmart-churn-model</b><br/>ลงทะเบียนเวอร์ชัน Champion พร้อม Model Signature (Lab 3)"]
        EXP -->|คัดเลือกโมเดลที่ดีที่สุด| REG
    end

    subgraph S4 ["4. ปฏิบัติการทางธุรกิจ (Serving & Power BI)"]
        PRED["⚡ <b>ฟังก์ชัน PREDICT (ประมวลผลบน Spark)</b><br/>ทำนายลูกค้าชุดใหม่ 200 รายจาก freshmart_scoring_batch.csv (Lab 4)"]
        G["🥇 <b>Gold Schema</b><br/>ตารางผลลัพธ์ gold.freshmart_predictions"]
        PBI["📊 <b>Power BI Dashboard (Direct Lake)</b><br/>ชี้เป้าลูกค้าเสี่ยง Churn ส่งต่อทีมการตลาดออกโปรโมชั่นรักษาลูกค้า"]
        PRED --> G
        G --> PBI
    end

    CSV --> B
    S -->|แบ่งข้อมูล Train / Test| EXP
    REG -->|โหลดโมเดล Champion| PRED
    S -.->|พารามิเตอร์ฟีเจอร์| PRED

    classDef stage fill:#f8fafc,stroke:#475569,stroke-width:2px,color:#0f172a;
    classDef raw fill:#ffffff,stroke:#64748b,stroke-width:1.5px,color:#0f172a;
    classDef silver fill:#f0fdf4,stroke:#16a34a,stroke-width:1.5px,color:#14532d;
    classDef ml fill:#eff6ff,stroke:#2563eb,stroke-width:1.5px,color:#1e3a8a;
    classDef champion fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#78350f;
    classDef gold fill:#fffbeb,stroke:#b45309,stroke-width:2px,color:#78350f;
    classDef pbi fill:#faf5ff,stroke:#9333ea,stroke-width:2px,color:#581c87;

    class S1,S2,S3,S4 stage;
    class CSV,B raw;
    class S silver;
    class EXP ml;
    class REG champion;
    class PRED,G gold;
    class PBI pbi;
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


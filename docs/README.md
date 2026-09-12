# Docs ความรู้ Data Science บน Microsoft Fabric

เอกสารชุดนี้สรุปความรู้ตามหลักสูตร **Implement a data science and machine learning solution for AI in Microsoft Fabric** จาก [Microsoft Learn](https://learn.microsoft.com/training/paths/implement-data-science-machine-learning-fabric/) และสไลด์ Instructor Edition

| แหล่งอ้างอิง | ไฟล์ / ลิงก์ |
| --- | --- |
| Microsoft Learn Learning Path | [Implement data science & machine learning for AI in Fabric](https://learn.microsoft.com/training/paths/implement-data-science-machine-learning-fabric/) |
| สไลด์ไทย / ENU | `Source/` — รายชื่อไฟล์ใน [resources.md](resources.md) |
| แล็บมือบน | [labs/README.md](../labs/README.md) |
| อภิธานศัพท์ | [glossary.md](glossary.md) |
| มาตรฐานภาษาไทย | [writing-style-th.md](writing-style-th.md) |

กรณีศึกษาหลัก: **FreshMart** — พยากรณ์ความต้องการสินค้า และทำนายลูกค้าที่จะเลิกซื้อ บน Lakehouse ที่จัดชั้นข้อมูลเป็น Bronze (ดิบ) แล้ว Silver (พร้อมวิเคราะห์) และ Gold (พร้อมใช้ธุรกิจ)

## เส้นทางอ่านเอกสาร

| # | เอกสาร | สไลด์ | โมดูล Learn | แล็บ |
| --- | --- | --- | --- | --- |
| 0 | [ภาพรวมหลักสูตร](00-overview.md) | M00 | — | — |
| 1 | [สถาปัตยกรรม Fabric และ OneLake](01-fabric-architecture.md) | M01 | Introduction to end-to-end analytics | Lab 0 |
| 2 | [กระบวนการ Data Science](02-data-science-process.md) | M02 | Get started with data science | Lab 0 |
| 3 | [สำรวจข้อมูลด้วย Notebook](03-explore-data-eda.md) | M03 | Explore data with notebooks | Lab 1 |
| 4 | [เตรียมข้อมูลด้วย Data Wrangler](04-data-wrangler.md) | M04 | Preprocess with Data Wrangler | Lab 2 |
| 5 | [ฝึกและติดตามโมเดลด้วย MLflow](05-mlflow-training.md) | M05 | Train and track with MLflow | Lab 3 |
| 6 | [สร้างคำทำนายแบบชุดด้วย PREDICT](06-batch-predict.md) | M06 | Generate batch predictions | Lab 4 |
| 7 | [Copilot, Semantic Link, Responsible AI](07-modern-ai.md) | M07 | (ขยายจาก Learn + Fabric docs) | — |
| 8 | [สรุปและแผน 30 วัน](08-wrap-up-roadmap.md) | M08 | — | — |
| — | [แหล่งอ้างอิง](resources.md) | — | ครบชุด | — |

## กลุ่มเป้าหมาย

- นักวิเคราะห์ข้อมูล (Data Analyst) ที่อยากเข้าใจวงจรงานวิทยาศาสตร์ข้อมูล
- วิศวกรข้อมูล (Data Engineer) ที่จะส่งต่อข้อมูลสู่การเรียนรู้ของเครื่อง
- นักวิทยาศาสตร์ข้อมูล (Data Scientist) ที่จะนำโมเดลไปใช้จริงบน Fabric

## ข้อกำหนดเบื้องต้น

- คุ้นเคยตารางข้อมูล การเชื่อมตาราง และตัวชี้วัดธุรกิจ
- มี Fabric Capacity (F2 ขึ้นไป) หรือ Fabric Trial
- พื้นฐาน Python / pandas / scikit-learn ระดับเริ่มต้น

## วิธีใช้คู่กับแล็บ

1. อ่าน docs ของโมดูลนั้นให้จบ
2. เปิดคู่มือใน `labs/instructions/`
3. รัน notebook ใน `labs/notebooks/` บน workspace `labs` / lakehouse `lh_freshmart`
4. ทบทวนคำถามท้ายบท หรือเปิด [glossary.md](glossary.md) เมื่อเจอศัพท์ใหม่

เมื่อพร้อมลงมือทำจริง เริ่มที่ [labs/README.md](../labs/README.md)

# M01 — สถาปัตยกรรม Microsoft Fabric และ OneLake

อ้างอิง: Microsoft Learn — [Introduction to end-to-end analytics using Microsoft Fabric](https://learn.microsoft.com/training/modules/introduction-end-analytics-use-microsoft-fabric/) · สไลด์ M01

หลังอ่านบทนี้ คุณจะอธิบายได้ว่าทำไมองค์กรใช้ Fabric และ OneLake แทนการคัดลอกข้อมูลหลายชั้น และชั้น Bronze / Silver / Gold ใช้กับงานวิทยาศาสตร์ข้อมูลอย่างไร  
ศัพท์ที่เกี่ยวข้อง: [Lakehouse](glossary.md#lakehouse) · [OneLake](glossary.md#onelake) · [Medallion](glossary.md#medallion-bronze--silver--gold)

## ทำไมต้องแพลตฟอร์มเดียว

สถาปัตยกรรมข้อมูลแบบเดิมมักเจอ:

- ข้อมูลแยกไซโล — แต่ละทีมคัดลอกข้อมูลคนละสำเนา
- เครื่องมือกระจัดกระจาย — นำเข้าข้อมูล ที่เก็บดิบ คลังวิเคราะห์ รายงาน และโมเดล อยู่คนละระบบ
- ส่งงานช้า — วิศวกรข้อมูลส่งไฟล์ให้นักวิทยาศาสตร์ข้อมูล แล้วนักวิเคราะห์รอรีเฟรชอีกชั้น

**Microsoft Fabric** เป็นแพลตฟอร์มวิเคราะห์ข้อมูลแบบครบวงจรบนคลาวด์ (SaaS) เก็บข้อมูลศูนย์กลางที่ **OneLake** แล้วให้หลายเครื่องมือประมวลผลอ่าน**สำเนาเดียวกัน**ได้ โดยไม่ต้องคัดลอกซ้ำ ๆ

## องค์ประกอบสำคัญ

### OneLake

- คล้าย “OneDrive สำหรับข้อมูลองค์กร”
- เก็บไฟล์และตารางเปิด (โดยเฉพาะรูปแบบ **Delta Lake**)
- เครื่องมืออย่าง Spark, คำสั่ง SQL แบบ T-SQL และ Power BI อ่านชุดข้อมูลเดียวกันได้

### กลุ่มงาน (workload) ที่เกี่ยวกับวิทยาศาสตร์ข้อมูล

| กลุ่มงาน | บทบาท |
| --- | --- |
| Data Factory | นำเข้าและจัดลำดับงาน (pipeline, Dataflow) |
| Data Engineering | Spark, Lakehouse, notebook ประมวลผลขนาดใหญ่ |
| Data Science | Notebook, การทดลอง, โมเดล, PREDICT, Data Wrangler |
| Data Warehouse | วิเคราะห์ด้วย SQL เชิงสัมพันธ์ |
| Real-Time Intelligence | ข้อมูลสตรีมและการสอบถามแบบใกล้เวลาจริง |
| Power BI | รายงาน และการอ่านตารางตรงจาก OneLake ([Direct Lake](glossary.md#direct-lake)) |

### บทบาททีมบน Workspace เดียวกัน (ภาพองค์กร)

ในองค์กรจริงหลายบทบาทร่วมงานบน workspace เดียวได้ — **ในแล็บคอร์สนี้แต่ละคนใช้ workspace ของตนเอง ไม่เชิญใครเข้า**

| บทบาท | รับผิดชอบหลัก |
| --- | --- |
| วิศวกรข้อมูล (Data Engineer) | Pipeline, คุณภาพข้อมูลชั้น Bronze/Silver, โครงตาราง |
| นักวิทยาศาสตร์ข้อมูล (Data Scientist) | สำรวจข้อมูล, สร้างฟีเจอร์, ทดลองโมเดล, สร้างคำทำนาย |
| นักวิเคราะห์ข้อมูล (Data Analyst) | โมเดลความหมายทางธุรกิจ, รายงาน, ตัวชี้วัดจากตาราง Gold และผลทำนาย |
| สถาปนิก / ผู้ดูแล | Capacity, ธรรมาภิบาล, สิทธิ์ |

## ชั้นข้อมูล Bronze / Silver / Gold สำหรับงานวิทยาศาสตร์ข้อมูล

| ชั้น | ความหมายใน FreshMart |
| --- | --- |
| **Bronze** | ข้อมูลดิบใกล้แหล่ง เช่น `bronze.customers`, `bronze.transactions` |
| **Silver** | ทำความสะอาดและสร้างฟีเจอร์ เช่น `silver.customer_features` |
| **Gold** | ผลลัพธ์พร้อมใช้ธุรกิจ เช่น `gold.freshmart_predictions` |

หลักการ: โมเดลอ่านจาก Silver (ฟีเจอร์ที่นิยามชัด) แล้วเขียนคะแนนไป Gold เพื่อให้รายงานธุรกิจใช้ — ไม่ฝึกโมเดลตรงจากไฟล์ดิบโดยไม่มีสัญญาข้อมูล

## ความเข้าใจผิดที่พบบ่อย

| ความเข้าใจผิด | ความจริง |
| --- | --- |
| Fabric เป็นแค่เปลี่ยนชื่อ Synapse หรือ Power BI | เป็นแพลตฟอร์มรวมกลุ่มงานหลายอย่างบน OneLake |
| ต้องมีคลัสเตอร์ Spark ของตัวเองตลอดเวลา | Spark ถูกจัดการใน Fabric ตาม session หรืองานที่รัน |
| งานวิทยาศาสตร์ข้อมูลต้องย้ายข้อมูลออกไป Azure Machine Learning เสมอ | ฝึก ติดตาม และทำนายเป็นชุดได้ใน Fabric ด้วย MLflow และ PREDICT |
| Lakehouse กับ Warehouse ใช้แทนกันได้ทุกงาน | Lakehouse เหมาะ Spark และการเรียนรู้ของเครื่อง; Warehouse เหมาะงาน SQL เชิงสัมพันธ์เข้มข้น |

## คำถามทบทวน

1. ประโยชน์หลักของ Fabric ในโครงการองค์กรคืออะไร — ใช้ตอบจากหัวข้อ “ทำไมต้องแพลตฟอร์มเดียว”  
2. Spark, T-SQL และ Power BI เข้าถึงข้อมูลบน OneLake อย่างไร — คิดถึงแนวอ่านสำเนาเดียว  
3. ถ้าต้องนำเข้าข้อมูลจากระบบ ERP ภายนอกเข้า Lakehouse ควรเริ่มที่กลุ่มงานใด — ดูตาราง workload  

## เชื่อมแล็บ

- [Lab 0 — ตั้งค่า Lakehouse](../labs/instructions/00-lakehouse-setup.md)

## ต่อไป

อ่านต่อ: [02 — กระบวนการ Data Science](02-data-science-process.md)

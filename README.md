# Microsoft Fabric Data Science — FreshMart Labs

Repository ชุดปฏิบัติการวิทยาศาสตร์ข้อมูลบน Microsoft Fabric ใช้กรณีศึกษา **FreshMart Customer Churn** (ทำนายลูกค้าที่จะเลิกซื้อ)  
กลุ่มเป้าหมาย: **นักวิเคราะห์ข้อมูลที่อยากเข้าใจวงจรงานวิทยาศาสตร์ข้อมูล**  
หลักสูตรอ้างอิง: [Implement a data science and machine learning solution for AI in Microsoft Fabric](https://learn.microsoft.com/training/paths/implement-data-science-machine-learning-fabric/) (พร้อมสไลด์ Instructor)

| เริ่มที่ | ลิงก์ |
| --- | --- |
| Docs ความรู้ (ทฤษฎี + อภิธานศัพท์) | [docs/README.md](docs/README.md) |
| อภิธานศัพท์ | [docs/glossary.md](docs/glossary.md) |
| Labs มือบน | [labs/README.md](labs/README.md) |

เส้นทางผู้เรียน: อ่าน [docs](docs/README.md) ตามโมดูล จากนั้นลงทะเบียน Fabric Trial ของตนเอง สร้าง workspace ของตนเอง (แนะนำชื่อ `labs`) — **ไม่เชิญใครเข้า** — แล้ว `git clone` repository นี้ นำเข้า notebook จาก `labs/notebooks/` และแนบ lakehouse `lh_freshmart` ที่สร้างเอง

## ตรวจว่าแล็บใช้งานได้จริง

```powershell
pip install -r labs/requirements-test.txt
pytest labs/tests -v
python labs/scripts/run_local_pipeline.py
```

จากนั้นทำตามคู่มือใน `labs/instructions/` บน Fabric Trial หรือ Capacity

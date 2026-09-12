# Microsoft Fabric Data Science — FreshMart Labs

![Status](https://img.shields.io/badge/status-active-2ea44f)
![License](https://img.shields.io/github/license/DataFabric-Academy/ms-fabric-data-science)
![Release](https://img.shields.io/github/v/release/DataFabric-Academy/ms-fabric-data-science?display_name=tag)
![Microsoft Fabric](https://img.shields.io/badge/platform-Microsoft%20Fabric-742774)

Repository ชุดปฏิบัติการวิทยาศาสตร์ข้อมูลบน Microsoft Fabric ใช้กรณีศึกษา **FreshMart Customer Churn** (ทำนายลูกค้าที่จะเลิกซื้อ)  
กลุ่มเป้าหมาย: **นักวิเคราะห์ข้อมูลที่อยากเข้าใจวงจรงานวิทยาศาสตร์ข้อมูล**  
หลักสูตรอ้างอิง: [Implement a data science and machine learning solution for AI in Microsoft Fabric](https://learn.microsoft.com/training/paths/implement-data-science-machine-learning-fabric/) (พร้อมสไลด์ Instructor)

## โครงการ (Project)

| รายการ | รายละเอียด |
| --- | --- |
| **License** | [MIT](LICENSE) |
| **Status** | **Active** — ใช้ในห้องเรียนและเรียนรู้ด้วยตนเองได้ |
| **Releases** | [Latest release](https://github.com/DataFabric-Academy/ms-fabric-data-science/releases/latest) · [All tags](https://github.com/DataFabric-Academy/ms-fabric-data-science/tags) |
| **Topics** | Microsoft Fabric, MLflow, PySpark, Medallion, Churn classification |

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

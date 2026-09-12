# Microsoft Fabric Data Science — FreshMart Labs

repository ชุดปฏิบัติการ Data Science บน Microsoft Fabric ใช้กรณีศึกษา **FreshMart Customer Churn**  
กลุ่มเป้าหมาย: **Analyst ที่อยากเข้าใจ Data Science**

เริ่มที่ [labs/README.md](labs/README.md)

ผู้เรียน: **`git clone` → Import notebook จาก `labs/notebooks/` → แนบ `lh_freshmart`** ใน workspace **`labs`**

## ตรวจว่าแล็บใช้งานได้จริง

```powershell
pip install -r labs/requirements-test.txt
pytest labs/tests -v
python labs/scripts/run_local_pipeline.py
```

จากนั้นทำตามคู่มือใน `labs/instructions/` บน Fabric Trial / Capacity

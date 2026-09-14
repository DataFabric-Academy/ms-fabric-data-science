# Lab 4: การทำนายเป็นชุดสู่ตาราง Gold สำหรับแคมเปญ

ในแล็บนี้คุณจะใช้โมเดลที่ลงทะเบียนแล้วทำนายสมาชิกชุดใหม่ 200 คน แล้วเขียนผลลงตาราง Gold พร้อมความเร่งด่วนสำหรับทีมการตลาด

แล็บนี้ใช้เวลาประมาณ **20–30** นาที  
ศัพท์ที่เกี่ยวข้อง: [PREDICT](../../docs/glossary.md#predict) · [ลายเซ็นโมเดล](../../docs/glossary.md#ลายเซ็นโมเดล-model-signature) · [feature_params.json](../../docs/glossary.md#feature_paramsjson) · [fallback](../../docs/glossary.md#fallback)

## สิ่งที่ต้องมี

- โมเดล `freshmart-churn-model` Version 1
- `Files/params/feature_params.json` จาก Lab 2
- กด **Import** > **Notebook** (ไม่ต้อง **+ New item**) เลือก `labs/notebooks/04-batch-predict.ipynb` แล้วตั้งชื่อ `04_FreshMart_Batch_Scoring`
- แนบ `lh_freshmart`

## กฎทองหนึ่งข้อ

**ห้ามคำนวณสเกลใหม่จากชุด 200 คน** — ต้องใช้ median/min/max จากชุดฝึกใน `feature_params.json`  
ชุดนี้ล็อกทั้งโครงคอลัมน์และสเกลฟีเจอร์ให้ตรงกับโมเดลที่ลงทะเบียนไว้

## ตรวจชุดทำนายใน Lakehouse

1. เปิด `lh_freshmart` แล้วไปที่ `Files/raw/freshmart_scoring_batch.csv`
2. พรีวิว: **200 แถว และไม่มีคอลัมน์ `Churn`**
3. รหัสลูกค้าขึ้นต้น `CUST_05xxx` ไม่ซ้อนกับชุดฝึก `CUST_01xxx`

ไฟล์ scoring พร้อมใช้เหมือนงานจริงของทีม CRM

## จัดฟีเจอร์ให้ตรงลายเซ็นโมเดล

รันเซลล์ที่เรียก `load_feature_params` แล้ว `transform_customers(..., require_target=False)`

**สิ่งที่ควรเห็น**

- ได้ 14 ฟีเจอร์ตามลำดับเดียวกับโมเดล
- มีคอลัมน์ `Gender_Other` แม้ชุด scoring มีแค่ F/M (เติม 0)
- ไม่มีคอลัมน์ `Churn`

## ใช้โมเดลทำนาย (PREDICT)

```python
from synapse.ml.predict import MLFlowTransformer

model = MLFlowTransformer(
    inputCols=list(params.feature_columns),
    outputCol="Churn_Prediction",
    modelName="freshmart-churn-model",
    modelVersion=1,
)
df_scored = model.transform(spark_features)
```

ส่ง **เฉพาะ** คอลัมน์ฟีเจอร์ อย่าส่ง `CustomerID`

ถ้า `synapse.ml.predict` ไม่พร้อม notebook จะใช้ทางเลือกสำรอง `mlflow.pyfunc.load_model`  
ถ้ารันบนเครื่องท้องถิ่นจะฝึก Random Forest ชั่วคราวเพื่อตรวจ pipeline — ไม่ใช่ผลส่งงานในห้องเรียน

**สิ่งที่ควรเห็น:** ได้คอลัมน์ `Churn_Prediction` ค่า 0 หรือ 1 และมีทั้งสองคลาส

## เขียนตาราง Gold + ความเร่งด่วนแคมเปญ

เพิ่มคอลัมน์ที่นักวิเคราะห์ส่งมอบงานต่อทีมการตลาดได้ทันที:

- `Scored_Timestamp`
- `Action_Priority`
  - ค่า `1` หมายถึง `High - Send Retention Voucher`
  - ค่า `0` หมายถึง `Normal - Standard Engagement`

เขียนตาราง Delta ชื่อ `gold.freshmart_predictions` แบบ overwrite

**สิ่งที่ควรเห็น:** หลัง Refresh **Tables** มีตาราง Gold **200** แถว  
ชุดทดสอบท้องถิ่นประมาณ **36 High** / **164 Normal** (บน Fabric อาจขยับเล็กน้อยถ้าชนิดข้อมูลไม่ตรง)

## สรุปผลด้วย SQL / Power BI

จาก SQL analytics endpoint:

```sql
SELECT Action_Priority, COUNT(*) AS CustomerCount
FROM gold.freshmart_predictions
GROUP BY Action_Priority;
```

จากนั้นกด **New report** เพื่อเปิดรายงาน Direct Lake ได้ทันที — ไม่ต้องคัดลอกข้อมูลออกจาก OneLake

## ผ่านแล็บเมื่อ

- [ ] Scoring batch 200 แถวถูกใช้แล้ว
- [ ] ใช้ params ชุดฝึก ไม่ scale เอง
- [ ] PREDICT หรือทางเลือกสำรองสำเร็จ
- [ ] มีตาราง Gold และสรุปสองกลุ่มความเร่งด่วน
- [ ] `Lab 4 verification passed`

## ทดสอบท้องถิ่นครบวงจร

```powershell
pytest labs/tests -v
python labs/scripts/run_local_pipeline.py
```

ตรวจ `labs/data/.local/gold_freshmart_predictions.csv` ว่ามี 200 แถวและมีทั้ง High / Normal

## แก้ปัญหาบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
| --- | --- | --- |
| Type mismatch / missing column | ลำดับฟีเจอร์ไม่ตรงลายเซ็น | ใช้ `params.feature_columns` จาก Lab 2 |
| ทำนายเอียงคลาสเดียว | scale จากชุด scoring | ลบการคำนวณ min/max ใน Notebook Lab 4 |
| หาโมเดลไม่เจอ | ชื่อหรือ version ผิด | ตรวจ Model item = `freshmart-churn-model` v1 |

## ล้างทรัพยากร (ทางเลือก)

จบคอร์สแล้วลบได้จาก **Workspace settings** แล้ว **Remove this workspace** — เป็น workspace ของคุณคนเดียว ไม่กระทบผู้เรียนคนอื่น

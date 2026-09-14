# แบบฝึกหัด 4: ทำนายเป็นชุดสู่ชั้น Gold

- ประมาณ **20–30** นาที

ในแบบฝึกหัดนี้ คุณจะเรียนรู้วิธี:

- โหลด Data asset `scoring-batch` แล้วจัดฟีเจอร์ให้ตรงลายเซ็นจากแบบฝึกหัด 2
- โหลด Champion จาก Automated ML แล้วทำนาย 200 ราย
- เขียนชั้น Gold แล้วลงทะเบียนเป็น Data asset สำหรับทีมการตลาด

ศัพท์: [ลายเซ็นโมเดล](../../docs/glossary.md#ลายเซ็นโมเดล-model-signature) · [feature_params.json](../../docs/glossary.md#feature_paramsjson)

อ้างอิง: [Guidelines for deploying MLflow models](https://learn.microsoft.com/azure/machine-learning/how-to-deploy-mlflow-models) — แทร็กนี้โหลดโมเดลมาทำนายใน notebook ไม่ได้ Deploy endpoint

## สิ่งที่ต้องมีก่อนเริ่ม

- โมเดล `freshmart-churn-model` จากแบบฝึกหัด 3 (Automated ML)
- Data asset `scoring-batch` จากแบบฝึกหัด 0 และ `feature_params.json` จากแบบฝึกหัด 2
- เปิด `labs-azureml/notebooks/04-batch-predict.ipynb`

> [!WARNING]
> **ห้ามสร้าง Batch Endpoint หรือ Compute cluster**  
> **ห้ามคำนวณ min/max ใหม่จากชุด 200 คน**

## งานที่ 1: ตรวจชุดทำนายจาก Data asset

1. ซ้ายมือเลือก **Data** แล้วเปิด `scoring-batch`
2. ดูแท็บ **Preview** ตามตาราง
3. รันเซลล์โหลดใน notebook — อ่าน Data asset ก่อน ถ้าไม่มีค่อยอ่าน CSV

| รายการ | ค่าที่ต้องเห็น |
| :--- | :--- |
| Data asset | `scoring-batch` |
| จำนวนแถว | **200** |
| คอลัมน์ `Churn` | **ไม่มี** |
| รหัสลูกค้า | ขึ้นต้น `CUST_05xxx` ไม่ซ้อนกับชุดฝึก |

## งานที่ 2: จัดฟีเจอร์ให้ตรงลายเซ็น

1. รันเซลล์โหลด `feature_params.json`
2. รัน `transform_customers(..., require_target=False)`

**เมื่องานนี้เสร็จ คุณควรเห็น**

- ได้ 14 ฟีเจอร์ตามลำดับเดียวกับโมเดล
- มีคอลัมน์ `Gender_Other` แม้ชุด scoring มีแค่ F/M (เติม 0)
- ไม่มีคอลัมน์ `Churn`

## งานที่ 3: ทำนายด้วย Champion จาก AutoML

1. รันเซลล์โหลดโมเดล

```python
import mlflow

model = mlflow.pyfunc.load_model("models:/freshmart-churn-model/1")
preds = model.predict(model_matrix(feature_frame, params))
```

ส่งเฉพาะคอลัมน์ฟีเจอร์ — อย่าส่ง `CustomerID`

ถ้าโหลดจาก registry ไม่ได้ notebook จะมีทางเลือกสำรองเพื่อตรวจ pipeline — ไม่ใช่ผลส่งงานในห้องเรียน

**เมื่องานนี้เสร็จ คุณควรเห็น:** คอลัมน์ `Churn_Prediction` เป็น 0 หรือ 1 และมีทั้งสองคลาส

## งานที่ 4: เขียนชั้น Gold

1. รันเซลล์เพิ่มคอลัมน์ความเร่งด่วนแล้วบันทึกไฟล์

| คอลัมน์ | ความหมาย |
| :--- | :--- |
| `Scored_Timestamp` | เวลาที่ทำนาย |
| `Action_Priority` ค่าทำนาย `1` | `High - Send Retention Voucher` |
| `Action_Priority` ค่าทำนาย `0` | `Normal - Standard Engagement` |

ไฟล์ผลลัพธ์: `data/gold/freshmart_predictions.parquet` (ถ้า parquet ไม่ได้จะได้ `.csv`)

จากนั้นลงทะเบียน Data asset:

1. ซ้ายมือเลือก **Data** > **Create** > **Data asset** (ถ้า notebook ยังไม่ได้ลงทะเบียนให้)
2. กรอกตามตาราง

| ช่อง | ค่าที่ใส่ |
| :--- | :--- |
| **Name** | `gold-freshmart-predictions` |
| **Type** | **Tabular** |
| ไฟล์ | `freshmart_predictions.csv` จากชั้น Gold |

**เมื่องานนี้เสร็จ คุณควรเห็น:** 200 แถว มีทั้ง High และ Normal (ชุดอ้างอิงท้องถิ่นประมาณ 36 / 164) หน้า **Data** มี `gold-freshmart-predictions` และ `Lab 4 verification passed`

เปิด asset นี้จาก **Data** เพื่อส่งต่อทีมการตลาด หรือดาวน์โหลดไป Excel / Power BI ได้

## ผ่านแบบฝึกหัดเมื่อ

- [ ] ใช้ Data asset `scoring-batch` และ params จากชุดฝึก
- [ ] โหลด `freshmart-churn-model` จาก Automated ML สำเร็จ
- [ ] หน้า **Data** มี `gold-freshmart-predictions`
- [ ] `Lab 4 verification passed`

## แก้ปัญหาบ่อย

| อาการ | สิ่งที่ทำต่อ |
| :--- | :--- |
| missing column / type mismatch | ใช้ `params.feature_columns` จากแบบฝึกหัด 2 |
| ทำนายเอียงคลาสเดียว | ลบการคำนวณ min/max ใน notebook นี้ |
| หาโมเดลไม่เจอ | กลับไปแบบฝึกหัด 3 ลงทะเบียน `freshmart-churn-model` บน compute instance |

## ล้างทรัพยากรหลังจบคอร์ส

1. ไป **Compute** แล้วเลือก **Stop** หรือ **Delete** compute instance ของคุณ
2. ถ้าคุณสร้าง resource group เองและไม่มีของอย่างอื่นอยู่ ให้ลบจาก [Azure portal](https://portal.azure.com)  
   ดู [Clean up resources](https://learn.microsoft.com/azure/machine-learning/quickstart-create-resources#clean-up-resources)

อย่าลบ resource group ที่ผู้สอนใช้ร่วมกับคลาส

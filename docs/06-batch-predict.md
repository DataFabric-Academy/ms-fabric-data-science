# M06 — สร้างคำทำนายแบบชุดด้วยฟังก์ชัน PREDICT

อ้างอิง: Microsoft Learn — [Generate batch predictions](https://learn.microsoft.com/training/modules/generate-batch-predictions-fabric/) · สไลด์ M06 · [Model scoring with PREDICT](https://learn.microsoft.com/fabric/data-science/model-scoring-predict)

หลังอ่านบทนี้ คุณจะเลือกได้ว่าควรทำนายเป็นชุดหรือแบบทันที และเรียก PREDICT ให้ตรงลายเซ็นโมเดลได้อย่างไร  
ศัพท์ที่เกี่ยวข้อง: [PREDICT](glossary.md#predict) · [ลายเซ็นโมเดล](glossary.md#ลายเซ็นโมเดล-model-signature) · [การทำนายเป็นชุด](glossary.md#การทำนายเป็นชุด-batch-scoring)

## จากห้องทดลองสู่ปฏิบัติการ

โมเดลมีมูลค่าเมื่อถูกเรียกซ้ำบนข้อมูลใหม่ตามจังหวะธุรกิจ:

| โจทย์ | จังหวะการทำนาย | ผลลัพธ์ธุรกิจ |
| --- | --- | --- |
| พยากรณ์ความต้องการ | รายวันหรือรายสัปดาห์ | แผนผลิต / สต็อก |
| ลูกค้าเลิกซื้อ | รายวันหรือหลังแคมเปญ | รายชื่อลูกค้าเสี่ยง + สิทธิประโยชน์ |

## ทำนายเป็นชุด กับ ทำนายแบบทันที

| | ทำนายเป็นชุด (batch scoring) | ทำนายแบบทันที (real-time) |
| --- | --- | --- |
| เวลารอที่ยอมรับได้ | นาทีถึงชั่วโมง | มิลลิวินาทีถึงวินาที |
| ปริมาณ | ชุดใหญ่บน Spark | คำขอทีละรายการหรือชุดเล็ก |
| บน Fabric ในหลักสูตรนี้ | **ฟังก์ชัน PREDICT + Lakehouse** | จุดปลายทางโมเดลแบบออนไลน์ (นอกขอบเขตแล็บหลัก) |

เลือกตามจังหวะการตัดสินใจของธุรกิจ — ไม่เลือกตามเทคโนโลยีที่ใหม่กว่า

## ข้อกำหนดของ PREDICT

จากเอกสารทางการ:

- โมเดลต้องอยู่ในรูปแบบ **MLflow** และมี**ลายเซ็นโครงสร้างข้อมูล (signature)** — บอกว่าอินพุต/เอาต์พุตชื่ออะไร ชนิดอะไร
- ไม่รองรับอินพุตหรือเอาต์พุตแบบเทนเซอร์หลายชุดซับซ้อนบางแบบ
- รองรับไลบรารีโมเดลหลายตระกูล เช่น scikit-learn, LightGBM, XGBoost, CatBoost, Spark, TensorFlow, PyTorch, ONNX, Prophet ฯลฯ

## ลายเซ็นโมเดล (model signature)

สัญญาโครงสร้างอินพุตและเอาต์พุต เก็บในไฟล์คำอธิบายโมเดลของ MLflow

| แบบ | ใช้เมื่อ |
| --- | --- |
| **แบบคอลัมน์ (column-based)** | ตารางธุรกิจ / โมเดลตาราง (FreshMart) |
| **แบบเทนเซอร์** | การเรียนรู้เชิงลึกที่อินพุตเป็นเทนเซอร์ |

ถ้าคอลัมน์ตอนทำนายไม่ตรงลายเซ็น การทำนายจะล้มหรือให้ผลผิดโดยไม่ทันสังเกต — ตรวจการจับคู่คอลัมน์ให้ตรงกับตอนฝึก

## PREDICT บน Spark ทำงานอย่างไร

คลาส `synapse.ml.predict.MLFlowTransformer` โหลดโมเดลจากที่ลงทะเบียน แล้วกระจายการคำนวณคำทำนายบน Spark

พารามิเตอร์หลัก:

- `inputCols` — คอลัมน์ฟีเจอร์
- `outputCol` — ชื่อคอลัมน์เก็บคำทำนาย
- `modelName` / `modelVersion` — ชี้โมเดลและเวอร์ชันที่เลือกใช้

### เรียกใช้ได้ 3 ช่องทาง

1. **Transformer API** — `model.transform(df)` (เรียกผ่านอ็อบเจกต์ในโค้ด)
2. **Spark SQL** — `SELECT PREDICT('ชื่อโมเดล/เวอร์ชัน', ...)`
3. **ฟังก์ชันที่ผู้ใช้กำหนดใน PySpark** — `model.to_udf()`

หรือใช้ตัวช่วยจากหน้า ML Model โดยเลือก **Apply this version** (มีทั้งตัวช่วยทีละขั้น และคัดลอกแม่แบบโค้ด)

### ตัวอย่าง Transformer API

```python
from synapse.ml.predict import MLFlowTransformer

model = MLFlowTransformer(
    inputCols=feature_cols,
    outputCol="prediction",
    modelName="freshmart-churn-model",
    modelVersion=1,
)

scored = model.transform(scoring_spark_df)
scored.write.format("delta").mode("overwrite").saveAsTable("gold.freshmart_predictions")
```

## จากคะแนนสู่การตัดสินใจ

หลังเขียนตารางชั้น Gold:

- Power BI โหมด **Direct Lake** อ่านตารางทำนายจาก OneLake โดยไม่คัดลอกซ้ำ
- ตั้งเวลารัน notebook หรือ pipeline ให้ทำนายตามรอบ
- กำกับดูแลหลังขึ้นระบบ: ใครอนุมัติเวอร์ชันใหม่, ติดตามคุณภาพโมเดลเมื่อข้อมูลเปลี่ยน, แผนฝึกใหม่

## Lab 4

- คู่มือ: [04-batch-predict.md](../labs/instructions/04-batch-predict.md)
- Notebook: `labs/notebooks/04-batch-predict.ipynb`

เป้าหมาย: ทำนายชุด `freshmart_scoring_batch` (200 แถว) แล้วเขียนผลลงตาราง `gold.freshmart_predictions`

## คำถามทบทวน

1. ลายเซ็นอินพุตและเอาต์พุตของโมเดลเก็บอยู่ที่ใด — ดูหัวข้อลายเซ็นโมเดล  
2. การทำนายเป็นชุดต่างจากการทำนายแบบทันทีอย่างไรในมุมธุรกิจ — ดูตารางเปรียบเทียบด้านบน  
3. ทำไม PREDICT จึงบังคับให้มีลายเซ็นโมเดล — เพื่อจับคู่คอลัมน์และชนิดข้อมูลให้ตรง  

## ต่อไป

อ่านต่อ: [07 — เครื่องมือสมัยใหม่และธรรมาภิบาล](07-modern-ai.md)

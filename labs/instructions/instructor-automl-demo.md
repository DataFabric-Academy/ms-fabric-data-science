# Demo ผู้สอน: AutoML บน FreshMart (ทางเลือก)

เอกสารทฤษฎีคู่กัน: [09-automl.md](../../docs/09-automl.md)

สาธิตบน **workspace ของผู้สอนเท่านั้น** หลังผู้เรียนจบ Lab 3 และก่อนเข้า Lab 4  
ผู้เรียนดูหน้าจอ ไม่ต้องรันตามทั้งคลาส และ**ห้ามเชิญผู้เรียนเข้า workspace ผู้สอน**

> **รอบ 6 ชั่วโมง:** ตัด Demo นี้ออกจากกำหนดการหลัก ตาม [instructor-6h-runbook.md](../../docs/instructor-6h-runbook.md)  
> ใช้ได้เฉพาะช่วงกันพลาดบ่าย (หลัง 14:40) และต้องรันล่วงหน้าแล้ว — อย่าให้ทั้งคลาสรอตัวช่วยสร้างสมุดโค้ด

ใช้เวลาประมาณ **8–12 นาที** (ตัวช่วยสร้างสมุดโค้ดประมาณ 4 นาที + เดิน Experiment อีก 4–8 นาที)  
ถ้าเวลาห้องเหลือไม่ถึง 8 นาที ให้ใช้เส้นทาง “รันล่วงหน้า” ด้านล่าง

ศัพท์ที่ใช้: [AutoML](../../docs/glossary.md#automl-automated-machine-learning) · [FLAML](../../docs/glossary.md#flaml) · [AUC](../../docs/glossary.md#auc-area-under-the-roc-curve) · [โมเดลที่เลือกใช้](../../docs/glossary.md#โมเดลที่เลือกใช้-champion) · [ลายเซ็นโมเดล](../../docs/glossary.md#ลายเซ็นโมเดล-model-signature) · [Capacity](../../docs/glossary.md#capacity)

## จุดประสงค์ในห้อง

ผู้เรียนเห็นว่า Fabric มีตัวช่วยสร้างการทดลอง AutoML จากตาราง Silver ได้  
แล้วยังตอบได้ว่าทำไมโมเดลที่เลือกใช้ของแล็บนี้ยังเป็น `freshmart-churn-model` จาก Lab 3 ไม่ใช่ผลจากตัวช่วย

ประโยคปิดที่ต้องพูด:

> AutoML หาโมเดลเส้นฐานให้เร็ว แต่คุณยังต้องเลือกเมตริก กันข้อมูลรั่วไหล และตัดสินใจเองว่าจะขึ้นโมเดลไหนเข้าแคมเปญ

## สิ่งที่ต้องมีก่อนเปิดจอ

- ตาราง `silver.customer_features` จาก Lab 2 บน Lakehouse `lh_freshmart` ของผู้สอน
- Experiment `freshmart-churn-prediction` และโมเดล `freshmart-churn-model` จาก Lab 3
- สลับโหมดการทำงาน (Experience Switcher) ไป **Data Science**
- โควตา Fabric Trial ของผู้สอนยังเหลือพอรัน Spark สั้น ๆ

อย่ารอให้ทั้งคลาสรัน Lab 3 บน workspace เดียวกัน

## กติกาที่ห้ามทำระหว่าง Demo

- ห้ามตั้งชื่อโมเดลผลลัพธ์ว่า `freshmart-churn-model` — Lab 4 เรียกชื่อนี้
- ห้ามเลือกโหมด **Best Fit** บน Trial
- ห้ามให้ทั้งคลาสกดรันตัวช่วยพร้อมกัน
- ห้ามสัญญาว่าคะแนน AUC จาก AutoML จะสูงกว่า Random Forest ทุกครั้ง — งบเวลาสั้นผลไม่คงที่

ชื่อที่แนะนำสำหรับของที่ตัวช่วยสร้าง:

| รายการ | ชื่อ |
| :--- | :--- |
| Notebook | `demo_FreshMart_AutoML` |
| Experiment | `freshmart-churn-automl-demo` |
| ML Model | `freshmart-churn-automl-demo` |

## เส้นทาง A — สาธิตสดด้วยตัวช่วย (8–12 นาที)

### นาที 0–1: โยงจาก Lab 3

เปิด Experiment `freshmart-churn-prediction` ชี้สองรันที่ผู้เรียนเพิ่งเทียบ:

- Decision Tree ได้ `test_roc_auc` ประมาณ **0.77**
- Random Forest ได้ประมาณ **0.86** และเป็นโมเดลที่เลือกใช้

พูดสั้น ๆ ว่าขั้นถัดไปคือ “ถ้าองค์กรอยากให้ระบบค้นอัลกอริทึมให้ ในงบเวลาจำกัด Fabric มี AutoML”

### นาที 1–4: เดินตัวช่วย

1. จาก Experiment, ML Model, หรือ Notebook ให้เปิดตัวช่วย **AutoML** (ป้ายบนหน้าจออาจเขียน **Automated ML** หรือ **AutoML**)
2. แหล่งข้อมูล: Lakehouse `lh_freshmart` แล้วเลือกตาราง `silver.customer_features`  
   ถ้าไม่เห็นตาราง ให้ Refresh Lakehouse แล้วยืนยันว่า Lab 2 เขียนตารางแล้ว
3. ประเภทงาน: **Binary Classification**
4. โหมด: **Quick Prototype** เท่านั้น
5. คอลัมน์เป้า (prediction column): `Churn`
6. คอลัมน์อินพุต: เอา `CustomerID` ออกถ้าตัวช่วยติ๊กมาให้ — รหัสลูกค้าไม่ใช่ฟีเจอร์
7. **Auto featurize**: ปิด  
   Lab 2 เตรียมฟีเจอร์ไว้แล้ว การให้ระบบสร้างคอลัมน์เพิ่มจะทำให้โครงไม่ตรง 14 ฟีเจอร์ของแล็บ
8. วิธีรัน: เลือก **Train Multiple Models Simultaneously** ได้ เพราะชุดนี้ประมาณ 1,500 แถวใส่ pandas ได้  
   ถ้าโควตาตึง ให้เลือกฝึกทีละโมเดลบน Spark แทน แล้วบอกห้องทันทีว่าโหมด Spark **ยังไม่ลงลายเซ็น** ที่ PREDICT ต้องการ
9. ตั้งชื่อ Notebook / Experiment / Model ตามตารางด้านบน
10. ตรวจตัวอย่างโค้ดที่ระบบจะสร้าง แล้วสร้างสมุดโค้ด

เอกสารขั้นตอนทางการ: [Use the low-code AutoML interface](https://learn.microsoft.com/fabric/data-science/low-code-automl)

### นาที 4–8: รันแล้วเดินผล

1. รันสมุดโค้ดที่ระบบสร้างจนจบ — Quick Prototype ชุดเล็กมักจบในไม่กี่นาที
2. เปิด Experiment `freshmart-churn-automl-demo`
3. ชี้ให้เห็นว่าระบบสร้างหลายรัน และแต่ละรันมีพารามิเตอร์กับเมตริกเหมือน Lab 3
4. เปิดรายการ **ML Model** ชื่อ `freshmart-churn-automl-demo` — แยกจาก `freshmart-churn-model`
5. ถ้ามีคะแนนบนชุดตรวจสอบ ให้เทียบกับ AUC ประมาณ 0.86 ของ Random Forest โดยไม่ตัดสินว่าอันไหนต้องชนะ

**สิ่งที่ควรเห็น:** workspace ผู้สอนมี Experiment และ Model ชื่อ `freshmart-churn-automl-demo` โดย `freshmart-churn-model` Version 1 ยังอยู่ครบ

### นาที 8–12: คำถามปิด แล้วส่งต่อ Lab 4

ถามห้องอย่างน้อยหนึ่งข้อ:

- ถ้า AutoML ได้ AUC สูงกว่า Random Forest จะขึ้นเป็นโมเดลแคมเปญเลยไหม
- ทำไมยังต้องดู Precision / Recall และสัญญา 14 ฟีเจอร์จาก Lab 2
- ถ้าเลือกโหมด Spark แล้วกด PREDICT ใน Lab 4 จะขาดอะไร

จากนั้นให้ผู้เรียนเปิด [04-batch-predict.md](04-batch-predict.md) ใช้โมเดลจาก Lab 3 ตามเดิม

## เส้นทาง B — รันล่วงหน้า (เมื่อเวลาห้องน้อยกว่า 8 นาที)

ทำบน workspace ผู้สอน **ก่อนคาบ**:

1. เดินตัวช่วยตามเส้นทาง A จนได้สมุดโค้ด
2. รันสมุดโค้ดให้จบ
3. ตรวจว่า Experiment `freshmart-churn-automl-demo` มีรันแล้ว

ตอนสอนสด เดินแค่การตั้งค่าตัวช่วย 1–2 หน้า แล้วกระโดดไป Experiment ที่รันเสร็จแล้ว  
ยังต้องพูดกติกาห้ามทับ `freshmart-churn-model` และข้อจำกัดลายเซ็นของโหมด Spark

## งานเสริมหลังคาบ (ไม่บังคับ)

ให้เฉพาะคนที่ Lab 3 ผ่านแล้ว และ **อย่าให้ลงทะเบียนทับ Champion**  
วางใน notebook ใหม่ที่แนบ `lh_freshmart` งบเวลาประมาณ 60 วินาที

```python
import mlflow
from flaml import AutoML

mlflow.set_experiment("freshmart-churn-automl-demo")

settings = {
    "time_budget": 60,
    "metric": "roc_auc",
    "task": "classification",
    "seed": 42,
    "force_cancel": True,
}

automl = AutoML()
with mlflow.start_run(run_name="flaml-stretch"):
    automl.fit(X_train, y_train, **settings)
    print("Best config:", automl.best_config)
    print("Best validation AUC:", 1 - automl.best_loss)
```

ใช้ `X_train` / `y_train` ชุดเดียวกับ Lab 3 (14 ฟีเจอร์, `stratify=y`, `random_state=42`)  
อย่าเปิด `use_spark=True` บน Trial ของผู้เรียน

## ถ้าติดระหว่าง Demo

| อาการ | ทำต่ออย่างไร |
| :--- | :--- |
| ไม่เห็นตาราง `silver.customer_features` | Refresh Lakehouse แล้วตรวจว่า Lab 2 เขียนตารางใน schema `silver` แล้ว |
| ตัวช่วยไม่ขึ้นจาก Experiment | เปิดจาก Notebook หรือรายการ ML Model ในโหมด **Data Science** |
| Spark session นานหรือโควตาหมด | หยุดสมุดโค้ด แล้วใช้เส้นทาง B จากรันที่ทำไว้ก่อนคาบ |
| ผู้เรียนถามว่าจะใช้โมเดลนี้ใน Lab 4 ได้ไหม | ตอบว่าใช้ `freshmart-churn-model` จาก Lab 3 เท่านั้น โหมด Spark ของ AutoML อาจไม่มีลายเซ็นสำหรับ PREDICT |
| AUC ของ AutoML ต่ำกว่า Random Forest | บอกว่าปกติเมื่องบเวลาสั้น จุดสอนคือวงจรและ Experiment ไม่ใช่การชนะคะแนน |

## ผ่าน Demo เมื่อ (ผู้สอน)

- [ ] ผู้เรียนเห็นตัวช่วยตั้ง Binary Classification + Quick Prototype บน `silver.customer_features`
- [ ] มี Experiment / Model แยกชื่อ `freshmart-churn-automl-demo`
- [ ] `freshmart-churn-model` จาก Lab 3 ไม่ถูกทับ
- [ ] ห้องได้ยินประโยคปิดเรื่องเมตริก ข้อมูลรั่วไหล และการขึ้น Champion
- [ ] ส่งต่อ Lab 4 โดยไม่เปลี่ยนโมเดลที่เรียก PREDICT

# งานเสริม: ทดลองใน notebook ด้วย MLflow

- ประมาณ **25–35** นาที  
- **ไม่บังคับ** — ทำได้หลังแบบฝึกหัด 3 (Automated ML) ผ่านแล้วเท่านั้น

ในงานนี้ คุณจะเรียนรู้วิธี:

- ฝึก Decision Tree และ Random Forest เองใน notebook
- บันทึกพารามิเตอร์และเมตริกลง MLflow
- เทียบคะแนนกับ Champion จาก AutoML โดยไม่ทับชื่อโมเดลของแบบฝึกหัด 3

อ้างอิง Learn: [Track model training in Jupyter notebooks with MLflow](https://learn.microsoft.com/training/modules/track-model-training-jupyter-notebooks-mlflow/)

> [!IMPORTANT]
> โมเดลที่แบบฝึกหัด 4 เรียกคือ `freshmart-churn-model` จาก **Automated ML**  
> งานเสริมนี้ให้ลงทะเบียนเป็น `freshmart-churn-manual` เท่านั้น

## สิ่งที่ต้องมีก่อนเริ่ม

- แบบฝึกหัด 3 ผ่านแล้ว และมี `freshmart-churn-model`
- เปิด `labs-azureml/notebooks/03-train-track-mlflow.ipynb`
- รันบน compute instance ของ Azure ML

## งานที่ 1: แยกชุดฝึก / ทดสอบ

1. รันเซลล์โหลด Silver และฟังก์ชันฟีเจอร์
2. ตรวจค่าตามตาราง

| รายการ | ค่า |
| :--- | :--- |
| สัดส่วน | Train 80% / Test 20% |
| `random_state` | `42` |
| `stratify` | `y` |
| ชุดฝึก / ชุดทดสอบ | **1,200** / **300** แถว |
| จำนวนฟีเจอร์ | **14** — อย่าใส่ `CustomerID` หรือ `Churn` ใน X |

## งานที่ 2: สร้าง experiment คนละชื่อจาก AutoML

1. รันเซลล์ตั้ง experiment

```python
import mlflow
mlflow.set_experiment("freshmart-churn-manual")
```

**เมื่องานนี้เสร็จ คุณควรเห็น:** Tracking URI ชี้ไป workspace ของ Azure ML

## งานที่ 3: ฝึกโมเดลเส้นฐานและโมเดลรวมต้นไม้

1. รันเซลล์ Decision Tree (`max_depth=5`, `random_state=42`)
2. รันเซลล์ Random Forest (`n_estimators=100`, `max_depth=8`, `random_state=42`)

**เมื่องานนี้เสร็จ คุณควรเห็น (seed 42):** Random Forest ได้ `test_roc_auc` ประมาณ **0.86** สูงกว่า Decision Tree ประมาณ **0.77**

## งานที่ 4: เทียบบน studio แล้วลงทะเบียนคนละชื่อ

1. ซ้ายมือเลือก **Jobs** แล้วเปิด `freshmart-churn-manual`
2. เทียบสองรันที่ `test_roc_auc`
3. ถ้าจะลงทะเบียน ให้ใช้ชื่อ `freshmart-churn-manual` เท่านั้น

**เมื่องานนี้เสร็จ คุณควรเห็น:** `Lab 3 verification passed` และ `freshmart-churn-model` จาก AutoML ยังอยู่

## ผ่านงานเสริมเมื่อ

- [ ] มีอย่างน้อย 2 รันใน experiment `freshmart-churn-manual`
- [ ] Random Forest ได้ AUC สูงกว่า Decision Tree
- [ ] ไม่ทับ `freshmart-churn-model`

## ต่อไป

กลับไป [แบบฝึกหัด 4](04-batch-predict.md) ใช้ Champion จาก Automated ML

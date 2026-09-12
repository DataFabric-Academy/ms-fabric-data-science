# Lab 3: ฝึกโมเดลและติดตามด้วย MLflow

ในแล็บนี้คุณจะฝึกโมเดลทำนาย Churn ของ FreshMart สองตัว เทียบคะแนนด้วย MLflow แล้วบันทึกโมเดลที่ดีที่สุด

แล็บนี้ใช้เวลาประมาณ **25–35** นาที  
ศัพท์ที่ใช้ในแล็บนี้อธิบายไว้ที่ [อภิธานศัพท์](../../docs/glossary.md) โดยเฉพาะ [MLflow](../../docs/glossary.md#mlflow) · [AUC](../../docs/glossary.md#auc-area-under-the-roc-curve) · [โมเดลเส้นฐาน](../../docs/glossary.md#โมเดลเส้นฐาน-baseline) · [โมเดลที่เลือกใช้](../../docs/glossary.md#โมเดลที่เลือกใช้-champion) · [stratify](../../docs/glossary.md#stratify)

ชุดนี้ทำนาย **Churn 0/1** (จำแนกประเภท) ซึ่งใกล้งานนักวิเคราะห์ร้านค้าจริง

## สิ่งที่ต้องมี

- ตาราง `silver.customer_features` และ `Files/params/feature_params.json` จาก Lab 2
- Import `labs/notebooks/03-train-track-mlflow.ipynb` แล้วตั้งชื่อ `03_FreshMart_Model_Training_MLflow`
- แนบ `lh_freshmart`

## แยกชุดฝึก / ทดสอบ

Notebook โหลด Silver แล้วแยกฟีเจอร์กับป้ายกำกับ:

```text
Train 80% / Test 20%
random_state=42
stratify=y
```

`random_state=42` ทำให้การสุ่มซ้ำได้ผลเดิมทั้งคลาส  
`stratify=y` ทำให้สัดส่วน Churn ในชุดฝึกและชุดทดสอบใกล้เคียงกัน

**สิ่งที่ควรเห็น:** ชุดฝึก **1,200** แถว ชุดทดสอบ **300** แถว ฟีเจอร์ **14** คอลัมน์  
อย่าใส่ `CustomerID` หรือ `Churn` ลงใน X

## สร้าง Experiment

```python
import mlflow
experiment_name = "freshmart-churn-prediction"
mlflow.set_experiment(experiment_name)
```

Fabric สร้างรายการประเภท **Experiment** ใน Workspace ให้อัตโนมัติ — เป็นสมุดรวมผลการทดลอง

## ฝึกโมเดลเส้นฐาน — Decision Tree

รันเซลล์ `Run_01_DecisionTree_Baseline`:

```python
from sklearn.tree import DecisionTreeClassifier

with mlflow.start_run():
    mlflow.autolog()
    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X_train, y_train)
```

พารามิเตอร์ เมตริก และ artifact ถูกบันทึกอัตโนมัติ

## ฝึกโมเดลที่เลือกใช้ — Random Forest

รันเซลล์ `Run_02_RandomForest_Champion`:

```python
from sklearn.ensemble import RandomForestClassifier

with mlflow.start_run():
    mlflow.autolog()
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X_train, y_train)
```

**สิ่งที่ควรเห็นจากชุดนี้ (seed 42):** Random Forest ได้ `test_roc_auc` ประมาณ **0.86** สูงกว่า Decision Tree ประมาณ **0.77**  
(AUC วัดความสามารถแยกคนมีแนวโน้ม Churn กับคนที่อยู่ต่อ — ใกล้ 1 ดีกว่า)

ถ้า Random Forest แพ้: ตรวจว่าฟีเจอร์หลุดคอลัมน์หรือถูก scale ซ้ำ

## สำรวจ Experiment บนหน้าจอ Fabric

1. กลับไปที่ Workspace
2. เปิด **Experiment** ชื่อ `freshmart-churn-prediction`  
   > ถ้ายังไม่เห็นรัน ให้ Refresh หน้า
3. ติ๊กทั้งสองรัน เทียบ `test_roc_auc` และ `test_f1_score`
4. เปิด Artifacts ของรัน Random Forest — ต้องเห็น `confusion_matrix.png` และโฟลเดอร์ `model/`

ปรับกราฟเปรียบเทียบได้: เปลี่ยน visualization เป็น bar หรือเปลี่ยนแกนเป็นชื่อ estimator

## บันทึกโมเดลที่ชนะ

เซลล์สุดท้ายค้นหารันที่ AUC สูงสุดแล้วลงทะเบียน:

```python
mlflow.register_model(f"runs:/{champion_run_id}/model", "freshmart-churn-model")
```

หรือจากหน้า Experiment: **Save as ML model** แล้วสร้างโมเดลใหม่ชื่อ `freshmart-churn-model`

**สิ่งที่ควรเห็น:** Workspace มี **Model** ชื่อ `freshmart-churn-model` Version 1  
โครงคอลัมน์ต้องตรง 14 ฟีเจอร์ของ Lab 2

## บันทึก notebook และจบ session

1. ตั้งชื่อ **03_FreshMart_Model_Training_MLflow**
2. **Stop session**

## ผ่านแล็บเมื่อ

- [ ] มีอย่างน้อย 2 รันใน Experiment
- [ ] Random Forest ได้ AUC สูงกว่า Decision Tree
- [ ] โมเดลลงทะเบียนแล้ว
- [ ] `Lab 3 verification passed`

## ทดสอบท้องถิ่น

```powershell
pytest labs/tests/test_churn_model.py -v
python labs/scripts/run_local_pipeline.py
```

## ต่อไป

ผู้เรียน: ไป [Lab 4 — ทำนายเป็นชุด](04-batch-predict.md) ด้วยโมเดล `freshmart-churn-model`  
ผู้สอน (ทางเลือก): สาธิต AutoML ตาม [instructor-automl-demo.md](instructor-automl-demo.md) ก่อนเข้า Lab 4 — ห้ามทับชื่อโมเดลของแล็บนี้

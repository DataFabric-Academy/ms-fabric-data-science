# Lab 3: ฝึกโมเดลและติดตามด้วย MLflow

ในแล็บนี้คุณจะฝึกโมเดลทำนาย Churn ของ FreshMart สองตัว เทียบคะแนนด้วย MLflow แล้วบันทึกโมเดลที่ดีที่สุด

แล็บนี้ใช้เวลาประมาณ **25–35** นาที

## สิ่งที่ต้องมี

- ตาราง `silver_customer_features` และ `Files/params/feature_params.json` จาก Lab 2
- Import `labs/notebooks/03-train-track-mlflow.ipynb` → ชื่อ `03_FreshMart_Model_Training_MLflow`
- แนบ `lh_freshmart`

## คำสั้น ๆ ที่ใช้ในแล็บ

| คำ | ความหมาย |
| --- | --- |
| Experiment | สมุดบันทึกการทดลองใน Workspace |
| Run | หนึ่งครั้งที่ฝึกโมเดล |
| AUC | คะแนนแยกคนมีแนวโน้ม Churn กับคนที่อยู่ต่อ (ใกล้ 1 ดีกว่า) |
| Register model | เก็บโมเดลชนะไว้ชื่อ `freshmart-churn-model` |

ชุดนี้ทำนาย **Churn 0/1** (classification) ซึ่งใกล้งาน Analyst ร้านค้าจริง

## แยกชุดฝึก / ทดสอบ

Notebook โหลด Silver แล้วแยกฟีเจอร์กับป้ายกำกับ:

```text
Train 80% / Test 20%
random_state=42
stratify=y
```

**จุดตรวจ:** Train **1,200** แถว, Test **300** แถว, ฟีเจอร์ **14** คอลัมน์  
อย่าใส่ `CustomerID` หรือ `Churn` ลงใน X

## สร้าง Experiment

```python
import mlflow
experiment_name = "freshmart-churn-prediction"
mlflow.set_experiment(experiment_name)
```

Fabric สร้าง item ประเภท **Experiment** ใน Workspace ให้อัตโนมัติ

## ฝึก Baseline — Decision Tree

รันเซลล์ `Run_01_DecisionTree_Baseline`:

```python
from sklearn.tree import DecisionTreeClassifier

with mlflow.start_run():
    mlflow.autolog()
    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X_train, y_train)
```

พารามิเตอร์ เมตริก และ artifact ถูกบันทึกอัตโนมัติ

## ฝึก Champion — Random Forest

รันเซลล์ `Run_02_RandomForest_Champion`:

```python
from sklearn.ensemble import RandomForestClassifier

with mlflow.start_run():
    mlflow.autolog()
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X_train, y_train)
```

**จุดตรวจจากชุดนี้ (seed 42):** Random Forest `test_roc_auc` ≈ **0.86** สูงกว่า Decision Tree ≈ **0.77**

ถ้า RF แพ้: ตรวจว่าฟีเจอร์หลุดคอลัมน์หรือถูก scale ซ้ำ

## สำรวจ Experiment บน UI

1. กลับไปที่ Workspace
2. เปิด **Experiment** ชื่อ `freshmart-churn-prediction`  
   > Tip: ถ้ายังไม่เห็นรัน ให้ Refresh หน้า
3. ติ๊กทั้งสองรัน เทียบ `test_roc_auc` และ `test_f1_score`
4. เปิด Artifacts ของรัน RF — ต้องเห็น `confusion_matrix.png` และโฟลเดอร์ `model/`

ปรับกราฟเปรียบเทียบได้: เปลี่ยน visualization เป็น bar / เปลี่ยนแกนเป็นชื่อ estimator

## บันทึกโมเดลชนะ

เซลล์สุดท้ายค้นหารันที่ AUC สูงสุดแล้วลงทะเบียน:

```python
mlflow.register_model(f"runs:/{champion_run_id}/model", "freshmart-churn-model")
```

หรือจาก UI ของ Experiment: **Save as ML model** → สร้างโมเดลใหม่ชื่อ `freshmart-churn-model`

**จุดตรวจ:** Workspace มี **Model** ชื่อ `freshmart-churn-model` Version 1  
Schema ต้องตรง 14 ฟีเจอร์ของ Lab 2

## บันทึก notebook และจบ session

1. ตั้งชื่อ **03_FreshMart_Model_Training_MLflow**
2. **Stop session**

## ผ่านแล็บเมื่อ

- [ ] มีอย่างน้อย 2 รันใน Experiment
- [ ] RF ชนะ DT ตาม AUC
- [ ] โมเดลลงทะเบียนแล้ว
- [ ] `Lab 3 verification passed`

## ทดสอบท้องถิ่น

```powershell
pytest labs/tests/test_churn_model.py -v
python labs/scripts/run_local_pipeline.py
```

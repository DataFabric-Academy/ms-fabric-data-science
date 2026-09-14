# แบบฝึกหัด 3: หาโมเดลจำแนก Churn ที่ดีที่สุดด้วย Automated ML

- ประมาณ **25–40** นาที (จ็อบเตรียมประมาณ 5–10 นาที แล้วลองโมเดลต่ออีกไม่กี่นาที)

ในแบบฝึกหัดนี้ คุณจะเรียนรู้วิธี:

- เลือก Data asset ชั้น Silver สำหรับงานจำแนกประเภท
- ตั้งค่าและส่งงาน Automated ML
- เปรียบเทียบโมเดลจากเมตริกหลัก แล้วลงทะเบียนตัวที่เลือกใช้

นี่คือ**เส้นหลัก**ของแทร็ก Azure ML — ไม่ใช่ demo ของผู้สอน  
อ้างอิง Learn: [Find the best classification model with Automated Machine Learning](https://learn.microsoft.com/training/modules/find-best-classification-model-automated-machine-learning/) · [Tutorial: no-code AutoML](https://learn.microsoft.com/azure/machine-learning/tutorial-first-experiment-automated-ml) · [Set up no-code Automated ML](https://learn.microsoft.com/azure/machine-learning/how-to-use-automated-ml-for-ml-models)

## สิ่งที่ต้องมีก่อนเริ่ม

- แบบฝึกหัด 2 ผ่านแล้ว และหน้า **Data** มี `silver-customer-features`
- compute instance ของคุณสถานะ **Running**

> [!WARNING]
> **ห้ามเลือก Deploy** เป็น web service หรือ Online endpoint  
> ใช้ compute instance ที่มีอยู่ หรือ **Serverless** — อย่าสร้าง cluster ขนาดใหญ่  
> ชุดนี้มีแค่ 1,500 แถว ไม่ต้องเปิด deep learning และไม่ต้องเปิด Explain best model

## สถานการณ์

ทีม FreshMart อยากได้โมเดลเส้นฐานเร็ว ๆ จากชั้น Silver โดยไม่ไล่ลองอัลกอริทึมทีละตัว  
คุณใช้ Automated ML หาโมเดลจำแนก `Churn` ที่เหมาะกับเมตริก **AUC** แล้วค่อยตัดสินใจขึ้นเป็น Champion

## งานที่ 1: เปิดตัวช่วย Automated ML

1. ลงชื่อเข้าใช้ [Azure Machine Learning studio](https://ml.azure.com) แล้วเลือก workspace ของคุณ
2. ซ้ายมือในส่วน **Authoring** เลือก **Automated ML**
3. เลือก **New Automated ML job**
4. ที่ **Training method** เลือก **Train automatically** แล้วเลือก **Start configuring job**

**เมื่องานนี้เสร็จ คุณควรเห็น:** แท็บ **Basic settings** ของตัวช่วยส่งงาน

## งานที่ 2: ตั้งชื่อ experiment

1. ที่ **Basic settings** เลือก **Create new**
2. กรอกค่าตามตาราง แล้วเลือก **Next**

| ช่อง | ค่าที่ใส่ |
| :--- | :--- |
| **Experiment name** | `freshmart-churn-prediction` |
| **Job name** | `automl-freshmart-churn` (หรือชื่อไม่ซ้ำ) |

## งานที่ 3: เลือก Data asset ชั้น Silver

อย่าสร้าง asset ใหม่ถ้ามี `silver-customer-features` จากแบบฝึกหัด 2 แล้ว

1. ที่ **Task type & data** ตั้ง **Select task type** เป็น **Classification**
2. ใต้ **Select data** เลือก **silver-customer-features** จากรายการ
3. เปิดพรีวิวแล้วตรวจตามตาราง
4. ถ้า schema ยังรวม `CustomerID` ให้ปิด **Include** ของคอลัมน์นั้น — รหัสลูกค้าไม่ใช่ฟีเจอร์
5. เลือก **Next**

| รายการ | ค่าที่ต้องเห็น |
| :--- | :--- |
| Data asset | `silver-customer-features` |
| ประเภทงาน | **Classification** |
| คอลัมน์เป้า | `Churn` |
| `CustomerID` | ไม่ใช้เป็นฟีเจอร์ |
| จำนวนแถว | ประมาณ 1,500 |

ถ้ายังไม่มี asset นี้ ให้เลือก **Create** แล้วอัปโหลด `customer_features.csv` จากแบบฝึกหัด 2 เป็นประเภท **Tabular** บน **workspaceblobstore** จากนั้นกลับมาเลือกจากรายการ

**เมื่องานนี้เสร็จ คุณควรเห็น:** ชุดข้อมูลตารางพร้อมคอลัมน์เป้า `Churn` และฟีเจอร์ 14 คอลัมน์

## งานที่ 4: ตั้งค่างานจำแนกประเภท

1. ที่ **Task settings** เลือกคอลัมน์เป้า **Churn**
2. เลือก **View additional configuration settings** แล้วใส่ค่าตามตาราง
3. เลือก **Save**
4. ที่ **Limits** จำกัดงบตามตารางด้านล่าง
5. เลือก **Next**

| ช่อง | ค่าที่ใส่ | เหตุผล |
| :--- | :--- | :--- |
| **Primary metric** | **AUC_weighted** | ชุดนี้ Churn ไม่สมดุล (~19.3%) อย่าใช้ Accuracy เป็นหลัก |
| **Enable deep learning** | ปิด | ชุดเล็ก ไม่จำเป็น |
| **Explain best model** | ปิด | ประหยัดเวลาในห้องเรียน |
| **Max trials** | **5** | พอเห็นหลายอัลกอริทึม |
| **Experiment timeout (minutes)** | **20** | กันจ็อบค้างกินเงิน |
| **Enable early termination** | เปิด | หยุดเมื่อคะแนนไม่ขึ้น |

อ้างอิงเมตริก: [Evaluate automated machine learning experiment results](https://learn.microsoft.com/azure/machine-learning/how-to-understand-automated-ml)

## งานที่ 5: เลือก compute แล้วส่งงาน

1. ที่แท็บ **Compute** เลือกประเภทตามลำดับความปลอดภัยของงบ

| ลำดับ | ประเภท | เมื่อไหร่ใช้ |
| :---: | :--- | :--- |
| 1 | **Compute instance** ของคุณ | แนะนำในห้องเรียนนี้ |
| 2 | **Serverless** | ถ้าตัวช่วยบังคับและมีสิทธิ์เปิด |
| 3 | Compute cluster `automl-demo` โหนดต่ำสุด **0** สูงสุด **1** ขนาด **Standard_DS11_v2** | ใช้เมื่อสองทางแรกใช้ไม่ได้ แล้วลบหลังคาบ |

2. เลือก **Next** แล้วเลือก **Submit training job** (บางหน้าจอเขียน **Finish**)

การเตรียมจ็อบอาจใช้เวลาหลายนาที — อย่ารีบสร้างจ็อบซ้ำ

**เมื่องานนี้เสร็จ คุณควรเห็น:** หน้า **Job** สถานะเป็น Preparing / Running และแท็บ **Models** เริ่มมีแถวเมื่อมีโมเดลจบ

## งานที่ 6: เปรียบเทียบโมเดลแล้วลงทะเบียน Champion

1. เปิดแท็บ **Models** (หรือ **Models + child jobs**)
2. เรียงตามเมตริกหลัก — โมเดลบนสุดคือตัวที่ระบบแนะนำ
3. เปิดอย่างน้อยหนึ่งโมเดล แล้วดูแท็บ **Metrics**
4. เมื่อจ็อบสถานะ **Completed** เลือกโมเดลที่ดีที่สุด แล้วเลือก **Register model** (อย่าเลือก **Deploy**)
5. ตั้งชื่อโมเดลตามตาราง

| ช่อง | ค่าที่ใส่ |
| :--- | :--- |
| **Name** | `freshmart-churn-model` |
| **Version** | 1 (ถ้ายังไม่มีชื่อนี้) |

**เมื่องานนี้เสร็จ คุณควรเห็น**

- Experiment `freshmart-churn-prediction` มีหลายรันย่อย
- เมนู **Models** มี `freshmart-churn-model`
- **ไม่มี** endpoint ถูกสร้าง

ถ้าตัวช่วย studio ใช้ไม่ได้ทั้งคลาส ให้เปิด `03-automl-classification.ipynb` แล้วรันทาง SDK หรือทางสำรอง FLAML ตามเซลล์ในโน้ตบุ๊ก

## ผ่านแบบฝึกหัดเมื่อ

- [ ] เลือก Data asset `silver-customer-features` เป็นแหล่งฝึก
- [ ] ส่งงาน Automated ML ประเภท Classification เป้า `Churn` สำเร็จ
- [ ] ตัด `CustomerID` ออกจากฟีเจอร์
- [ ] เมตริกหลักเป็น **AUC_weighted**
- [ ] ลงทะเบียน `freshmart-churn-model` โดยไม่ Deploy
- [ ] (ถ้าใช้ notebook) เซลล์สุดท้ายพิมพ์ `Lab 3 verification passed`

## ต่อไป

ผู้เรียนทุกคน: ไป [แบบฝึกหัด 4](04-batch-predict.md)  
งานเสริม (ไม่บังคับ): [ทดลองใน notebook ด้วย MLflow](03-train-track-mlflow.md) — ลงทะเบียนคนละชื่อ ห้ามทับ Champion

## แก้ปัญหาบ่อย

| อาการ | สิ่งที่ทำต่อ |
| :--- | :--- |
| ไม่เห็น `silver-customer-features` | กลับไปแบบฝึกหัด 2 งานที่ 4 แล้ว Refresh หน้า **Data** |
| จ็อบค้างที่ Preparing นานเกิน 15 นาที | เปิด notebook ทางสำรอง FLAML — อย่าสร้างจ็อบซ้อน |
| หาปุ่ม Register ไม่เจอ | รอสถานะ **Completed** แล้วเปิดโมเดลจากแท็บ **Models** |
| สร้าง cluster ไม่ได้ | ใช้ compute instance หรือ notebook ทางสำรอง |

## ล้างทรัพยากรเมื่อเลิกใช้

1. ถ้าสร้าง cluster ชั่วคราว ให้ลบหรือตั้งโหนดต่ำสุดเป็น 0
2. ไป **Compute** แล้วเลือก **Stop** ที่ compute instance

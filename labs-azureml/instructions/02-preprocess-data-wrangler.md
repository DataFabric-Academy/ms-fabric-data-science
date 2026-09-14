# แบบฝึกหัด 2: เตรียมฟีเจอร์และ data asset สำหรับ AutoML

- ประมาณ **30** นาที

ในแบบฝึกหัดนี้ คุณจะเรียนรู้วิธี:

- แปลงข้อมูลธุรกรรมให้เห็นผล (เทียบเท่า Data Wrangler)
- ล็อกพารามิเตอร์ฟีเจอร์จากชุดฝึก เพื่อไม่ให้ข้อมูลรั่วไหลตอนทำนาย
- เตรียมไฟล์ Silver ให้แบบฝึกหัด 3 (Automated ML) ใช้เป็น data asset

ศัพท์: [ฟีเจอร์](../../docs/glossary.md#ฟีเจอร์-feature) · [feature_params.json](../../docs/glossary.md#feature_paramsjson)

อ้างอิงแนวคิด Learn: [Preprocess data and configure featurization](https://learn.microsoft.com/training/modules/find-best-classification-model-automated-machine-learning/2-preprocess-data-configure-featurization)

## สิ่งที่ต้องมีก่อนเริ่ม

- แบบฝึกหัด 1 ผ่านแล้ว
- เปิด `labs-azureml/notebooks/02-preprocess-data-wrangler.ipynb`
- มีชั้น `data/bronze` จากแบบฝึกหัด 0

> Azure ML Studio notebook ไม่มี Data Wrangler แบบ Fabric  
> งานที่ 1 ใช้ pandas — ถ้าเปิดใน VS Code จะใช้ส่วนขยาย Data Wrangler แทนได้

## กฎทอง

โมเดลเรียนรู้จาก **min/max ของชุดฝึก 1,500 คน**  
แบบฝึกหัด 4 ทำนายชุดใหม่ 200 คน — **ห้ามคำนวณสเกลใหม่** ต้องใช้ `feature_params.json` จากแบบฝึกหัดนี้

## งานที่ 1: ฝึกแปลงธุรกรรม

1. รันเซลล์โหลดธุรกรรมแล้วสุ่ม 500 แถวเป็นตัวแปร `df`
2. รันเซลล์ที่ทำสามอย่างนี้:

| ขั้น | การกระทำ | ค่า |
| :--- | :--- | :--- |
| จัดข้อความ | `Category` เป็น title case | — |
| กรอง | `StoreType` เท่ากับ | `Express` |
| รวมยอด | ค่าเฉลี่ย `WasteCost` ตาม | `Category` |

**เมื่องานนี้เสร็จ คุณควรเห็น:** ตารางสรุปของเสียตามหมวด และแถว Express เรียง `WasteCost` จากมากไปน้อย

## งานที่ 2: โหลดสมาชิกแล้วรันสัญญาฟีเจอร์

1. รันเซลล์โหลด `bronze/customers`
2. รันเซลล์ที่มี `fit_preprocessor` และ `transform_customers`
3. รันเซลล์ `fit` แล้ว `transform`

**เมื่องานนี้เสร็จ คุณควรเห็น**

| รายการ | ค่า |
| :--- | :--- |
| ขนาดสมาชิกก่อนแปลง | ประมาณ `(1500, 11)` |
| Age ว่างก่อนแปลง | **37** |
| Age median ที่ใช้เติม | **37.0** |
| คอลัมน์ที่ scale แล้ว | อยู่ในช่วงประมาณ `[0, 1]` |
| ค่าว่างในฟีเจอร์ | ไม่มี |

ลำดับคอลัมน์ที่โมเดลและ AutoML ต้องได้ (อย่าใส่ `CustomerID` เป็นฟีเจอร์):

`Age`, `TenureMonths`, `RecencyDays`, `Frequency`, `MonetaryTotal`, `AvgBasketSize`, `ComplaintCount`,  
`MembershipTier_Bronze`, `MembershipTier_Gold`, `MembershipTier_Platinum`, `MembershipTier_Silver`,  
`Gender_F`, `Gender_M`, `Gender_Other`, `Churn`

## งานที่ 3: บันทึก Silver และ params

1. รันเซลล์บันทึกใน notebook

เซลล์จะเขียนอย่างน้อย:

| ไฟล์ | ใช้ต่อที่ |
| :--- | :--- |
| `data/silver/customer_features.parquet` | โหลดใน notebook |
| `data/silver/customer_features.csv` | Data asset `silver-customer-features` |
| `data/params/feature_params.json` | แบบฝึกหัด 4 |

**เมื่องานนี้เสร็จ คุณควรเห็น:** เส้นทางไฟล์ที่บันทึก — ยังต้องลงทะเบียน Data asset ในงานถัดไป

## งานที่ 4: ลงทะเบียน Data asset ชั้น Silver

ต้องมี asset นี้ก่อนเข้าแบบฝึกหัด 3 — Automated ML เลือกจากหน้า **Data** ไม่ได้อ่านไฟล์ใน notebook โดยตรง

1. ซ้ายมือเลือก **Data**
2. เลือก **Create** > **Data asset**
3. กรอกค่าตามตาราง แล้วเลือก **Create**
4. เปิด asset แล้วดูแท็บ **Preview** ให้มีประมาณ 1,500 แถว

| ช่อง | ค่าที่ใส่ |
| :--- | :--- |
| **Name** | `silver-customer-features` |
| **Type** | **Tabular** |
| **Data source** | **From local files** หรือไฟล์ `data/silver/customer_features.csv` ใน datastore |
| **Datastore** | **workspaceblobstore** |
| ไฟล์ | `customer_features.csv` ที่ notebook เพิ่งบันทึก |

ถ้าเซลล์ notebook พิมพ์ `Registered data asset silver-customer-features` แล้ว ให้เปิดหน้า **Data** ยืนยันว่ามีชื่อนี้ — ไม่ต้องสร้างซ้ำ เว้นแต่ Preview ว่าง

**เมื่องานนี้เสร็จ คุณควรเห็น:** หน้า **Data** มี `silver-customer-features` และ `Lab 2 verification passed`

## ผ่านแบบฝึกหัดเมื่อ

- [ ] ได้แปลงธุรกรรมอย่างน้อยหนึ่งครั้ง
- [ ] มี Silver 1,500 แถว และ `feature_params.json`
- [ ] หน้า **Data** มี `silver-customer-features`
- [ ] `Lab 2 verification passed`

## ล้างทรัพยากรเมื่อเลิกใช้

ถ้าจบคาบแล้ว ไป **Compute** แล้วเลือก **Stop**

# Lab 2: เตรียมข้อมูลด้วย Data Wrangler และบันทึกฟีเจอร์

ในแล็บนี้คุณจะใช้ Data Wrangler กับข้อมูล FreshMart จริง ๆ (สร้างโค้ดกลับเข้า notebook) จากนั้นรันสัญญาฟีเจอร์ที่ล็อก params สำหรับ Lab 3–4

แล็บนี้ใช้เวลาประมาณ **30** นาที

## สิ่งที่ต้องมี

- Lab 1 ผ่านแล้ว
- Import `labs/notebooks/02-preprocess-data-wrangler.ipynb` → ชื่อ `02_FreshMart_Data_Preparation`
- แนบ `lh_freshmart`

## สองส่วนในแล็บนี้ (ชัด ๆ)

| ส่วน | ทำอะไร | ได้โค้ดจากไหน |
| --- | --- | --- |
| **A — Data Wrangler** | จัดข้อความ / กรอง / รวมยอด ของเสียตามหมวด | กด **Add code to notebook** |
| **B — ฟีเจอร์สมาชิก** | เติม Age, one-hot, scale แล้วบันทึก Silver + params | รันเซลล์ที่เตรียมให้ (จำเป็นต่อ Lab 4) |

> ใช้ **ธุรกรรม** ฝึก Wrangler และ **สมาชิก** เตรียมฟีเจอร์ ML — เป็นธุรกิจเดียวกันทั้งสาย

---

## ส่วน A: Data Wrangler กับธุรกรรม

### โหลดข้อมูล

รันเซลล์โหลดธุรกรรมให้ได้ตัวแปร `df` (หรือวางโค้ด):

```python
df = spark.read.table("bronze_transactions").toPandas()
df = df.sample(n=500, random_state=1).reset_index(drop=True)
df.head(4)
```

สุ่ม 500 แถวให้ Wrangler ตอบสนองเร็วขึ้น

### เปิด Data Wrangler

1. รอให้เซลล์รันจบ (kernel ว่าง)
2. แท็บ **Home** → dropdown **Data Wrangler** → เลือก `df`  
   หรือใต้เอาต์พุตตาราง กด **Open in Data Wrangler**
3. ดู **Summary** ด้านขวา — เลือกคอลัมน์ `WasteCost` ดูการกระจาย

### จัดรูปแบบข้อความ Category

1. เลือกคอลัมน์ `Category`
2. **Operations** → **Format** → **Capitalize first character**  
   เปิด **Capitalize all words** แล้ว **Apply**
3. (ถ้ามีจุดหรือตัวพิมพ์ไม่สม่ำเสมอ) ลอง **Find and replace** ตามที่เห็นใน Summary

### กรองและเรียง

1. **Operations** → **Sort and filter** → **Filter**
   - Target column: `StoreType`
   - Operation: Equal to
   - Value: `Express`
   - Action: Keep matching rows → **Apply**
2. เลือก `WasteCost` ดู Summary อีกครั้ง — Express มักของเสียสูงกว่า
3. **Sort values** ตาม `WasteCost` Descending → **Apply**  
   เห็นรายการของเสียสูงสุดของ Express ได้ทันที

ถ้าอยากย้อน: เปิด **Cleaning steps** แล้วลบขั้น Sort ได้

### รวมยอดตามหมวด แล้วใส่โค้ดกลับ notebook

1. ลบขั้น Filter/Sort ถ้าต้องการใช้ทั้งตัวอย่าง 500 แถว หรือเริ่ม Wrangler ใหม่จาก `df` เดิม
2. **Operations** → **Group by and aggregate**
   - Group by: `Category`
   - Aggregation: `WasteCost` → **Mean** (หรือ Sum)
3. **Apply** แล้วกด **Add code to notebook** (หรือ Copy code)
4. ใน notebook รวมเป็นฟังก์ชันสั้น ๆ แล้วรัน เช่น:

```python
def summarize_waste(df):
    # โค้ดจาก Data Wrangler — ปรับชื่อฟังก์ชันให้สื่อความหมาย
    df = df.groupby(["Category"]).agg(WasteCost_mean=("WasteCost", "mean")).reset_index()
    return df

print(summarize_waste(df))
```

**อินไซต์:** คุณเพิ่งสร้างโค้ด preprocessing จาก UI โดยไม่ต้องเขียน pandas จากศูนย์

ออกจาก Wrangler เมื่อพร้อมเข้าส่วน B

---

## ส่วน B: เตรียมฟีเจอร์สมาชิกสำหรับโมเดล (ส่งงาน Lab 3–4)

โมเดลใน Lab 3 เรียนรู้จากค่าที่ **ปรับสเกลด้วย min/max ของชุดฝึก 1,500 คน**  
ถ้า Lab 4 ไปคำนวณ min/max ใหม่จากชุดทำนาย 200 คน ผลทำนายจะเพี้ยน

สัญญาที่ใช้ทั้ง Lab 2–4 อยู่ในเซลล์ `fit_preprocessor` / `transform_customers` ของ notebook

### โหลดสมาชิก

```python
df_cust = spark.read.table("bronze_customers").toPandas()
print(df_cust.shape)
print("Age missing:", df_cust["Age"].isna().sum())
```

**จุดตรวจ:** `(1500, 11)` และ Age ว่าง **37** แถว

### (ทางเลือก) ลอง Wrangler กับ df_cust

เปิด Data Wrangler เลือก `df_cust` แล้วลอง:

1. `Age` → **Fill missing values** → Median → Apply
2. **One-hot encode** `MembershipTier` / `Gender`
3. **Scale min/max** คอลัมน์เงิน/ความถี่

ดูภาพแล้วปิดได้ — **สำหรับส่งงาน Lab 3–4 ให้รันเซลล์สัญญาฟีเจอร์ด้านล่าง** เพื่อให้ได้ `feature_params.json` ชุดเดียวกันทั้งคลาส

### รันสัญญาฟีเจอร์ที่เตรียมให้

รันเซลล์ที่มี `fit_preprocessor` และ `transform_customers`

**จุดตรวจ**

- Age median = **37.0**
- ได้คอลัมน์ตามลำดับนี้ (เป็น Model Signature ใน Lab 3):

`CustomerID`, `Age`, `TenureMonths`, `RecencyDays`, `Frequency`, `MonetaryTotal`, `AvgBasketSize`, `ComplaintCount`,  
`MembershipTier_Bronze`, `MembershipTier_Gold`, `MembershipTier_Platinum`, `MembershipTier_Silver`,  
`Gender_F`, `Gender_M`, `Gender_Other`, `Churn`

- คอลัมน์ที่ scale แล้วอยู่ในช่วงประมาณ `[0, 1]`
- ไม่มี NaN ในฟีเจอร์

### บันทึก Silver + params

เซลล์บันทึกจะเขียน:

- ตาราง `silver_customer_features`
- `Files/params/feature_params.json`

**จุดตรวจ:** Refresh **Tables** แล้วเห็น `silver_customer_features` และเซลล์สุดท้ายพิมพ์ `Lab 2 verification passed`

## บันทึก notebook และจบ session

1. ตั้งชื่อ **02_FreshMart_Data_Preparation**
2. **Stop session**

## ผ่านแล็บเมื่อ

- [ ] ได้ใช้ Data Wrangler กับธุรกรรม และ **Add code to notebook** อย่างน้อยหนึ่งครั้ง
- [ ] มี `silver_customer_features` 1,500 แถว
- [ ] มี `feature_params.json` จากชุดฝึก
- [ ] `Lab 2 verification passed`

## ทดสอบท้องถิ่น

```powershell
pytest labs/tests/test_feature_pipeline.py -v
```

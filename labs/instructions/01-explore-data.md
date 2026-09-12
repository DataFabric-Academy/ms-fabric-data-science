# Lab 1: สำรวจข้อมูล FreshMart ด้วย Notebook

ในแล็บนี้คุณจะโหลดข้อมูล FreshMart สำรวจคุณภาพ สร้างกราฟ และหาความสัมพันธ์ — จบด้วยภาพพฤติกรรมสมาชิกที่ Churn

แล็บนี้ใช้เวลาประมาณ **30** นาที

## สิ่งที่ต้องมี

- Lab 0 ผ่านแล้ว
- Import `labs/notebooks/01-explore-data.ipynb` → ชื่อ `01_FreshMart_Exploratory_Data_Analysis`
- แนบ Default Lakehouse = `lh_freshmart`

## เรื่องราวสั้น ๆ

คุณเป็น **Analyst ของ FreshMart** ทีมอยากรู้ก่อนสร้างโมเดลว่า:

1. ข้อมูลขาดตรงไหน?
2. ของเสียสูงสุดอยู่หมวด/ประเภทสาขาไหน?
3. สมาชิกที่ Churn ต่างจากคนที่อยู่ต่ออย่างไร?

ไม่ต้องจำสูตรสถิติ — รันทีละเซลล์ แล้วจดข้อสังเกตสั้น ๆ

## โหลดข้อมูลธุรกรรม

รันเซลล์โหลด (หรือวางโค้ดนี้ถ้าสร้าง notebook เอง):

```python
df = spark.read.table("bronze.transactions").toPandas()
print(df.shape)
df.head()
```

**จุดตรวจ:** shape = `(3000, 14)`

คอลัมน์สำคัญ: `UnitsSold`, `DiscountRate`, `WasteUnits`, `WasteCost`, `StoreType`, `Category`

> Notebook ที่ให้มามี fallback อ่าน `Files/raw/freshmart_transactions.csv` ถ้าตารางยังไม่พร้อม

## ตรวจโครงสร้างและค่าว่าง

```python
print("Number of rows:", df.shape[0])
print("Number of columns:", df.shape[1])
print("\nData types:")
print(df.dtypes)

missing_values = df.isnull().sum()
print("\nMissing values per column:")
print(missing_values[missing_values > 0])
```

**ต้องเห็น:** `DiscountRate` ว่าง **89 แถว (~3%)** — ส่งต่อไป Lab 2  
คอลัมน์อื่นไม่ควรว่างจำนวนมาก

## สถิติเชิงพรรณนา

```python
df[["UnitsSold", "UnitPrice", "DiscountRate", "SalesAmount", "WasteUnits", "WasteCost"]].describe()
```

สังเกต `WasteUnits`: ส่วนใหญ่ 0–2 หน่วย แต่มีหางยาว (เบ้ขวา) — ของเสียกระจุกที่บางวัน/บางสาขา

## พล็อตการกระจาย

รันเซลล์ histogram ใน notebook (UnitsSold / WasteUnits) หรือวาง:

```python
import matplotlib.pyplot as plt
import seaborn as sns

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.histplot(df["UnitsSold"], bins=15, kde=True, ax=axes[0])
axes[0].set_title("Units Sold")
sns.histplot(df["WasteUnits"], bins=10, kde=True, ax=axes[1])
axes[1].set_title("Waste Units (right-skewed)")
plt.tight_layout()
plt.show()
```

จากนั้น box plot ตามประเภทสาขา:

```python
plt.figure(figsize=(10, 5))
sns.boxplot(data=df, x="StoreType", y="WasteUnits")
plt.title("Waste Units by Store Type")
plt.show()
```

**อินไซต์ที่ควรได้:** ค่าเฉลี่ย `WasteUnits` ของ **Express (~0.50)** สูงกว่า Hypermarket (~0.12) — พื้นที่จัดเก็บจำกัด ของเสียช่วงสุดสัปดาห์สูงกว่า

## Correlation

```python
numeric_cols = ["UnitsSold", "UnitPrice", "DiscountRate", "SalesAmount", "WasteUnits", "WasteCost", "IsWeekend"]
print(df[numeric_cols].corr(numeric_only=True).round(2))

plt.figure(figsize=(9, 7))
sns.heatmap(df[numeric_cols].corr(numeric_only=True), annot=True, vmin=-1, vmax=1, cmap="vlag")
plt.title("FreshMart Feature Correlation")
plt.show()
```

**ค่าจากชุดที่ publish (ปัด 2 ตำแหน่ง)**

| คู่ | ค่า | ความหมายธุรกิจ |
| --- | --- | --- |
| DiscountRate ↔ UnitsSold | ≈ **+0.38** | ลดราคาแล้วขายได้มากขึ้น |
| DiscountRate ↔ WasteUnits | ≈ **-0.12** | สินค้าที่ลดราคามักเหลือทิ้งน้อยลง |
| UnitsSold ↔ SalesAmount | สูงมาก | ตามนิยามยอดเงิน |

## สำรวจสมาชิกและ Churn

```python
df_cust = spark.read.table("bronze.customers").toPandas()
print("Number of customers:", df_cust.shape[0])
print(df_cust["Churn"].value_counts(normalize=True))
print("Age missing:", df_cust["Age"].isna().sum())
```

**ต้องเห็น**

| รายการ | ค่าจริง |
| --- | --- |
| สมาชิก | 1,500 |
| Churn = 1 | 290 คน (**19.3%**) |
| Age ว่าง | **37 แถว (2.47%)** |
| MembershipTier | Bronze, Silver, Gold, Platinum |

รัน scatter ใน notebook: `RecencyDays` vs `ComplaintCount` แยกสีตาม Churn

**อินไซต์:** กลุ่มที่ขาดซื้อนานและร้องเรียนบ่อยกระจุกที่ `Churn = 1`

## บันทึก notebook และจบ session

1. ตั้งชื่อ notebook เป็น **01_FreshMart_Exploratory_Data_Analysis** (หรือชื่อที่แนะนำด้านบน)
2. เมนู notebook → **Stop session** เมื่อจบ

## ผ่านแล็บเมื่อ

- [ ] เซลล์สุดท้ายพิมพ์ `Lab 1 verification passed`
- [ ] จด 3 ข้อส่ง Lab 2: เติม Age · แปลงหมวดหมู่เป็นตัวเลข · ปรับสเกลเงิน/ความถี่
- [ ] ใช้ตัวเลขจากชุดข้อมูลจริง ไม่เดาจากสไลด์

## ทดสอบท้องถิ่น (ถ้ายังไม่เปิด Fabric)

```powershell
pytest labs/tests/test_data_contract.py -v
```

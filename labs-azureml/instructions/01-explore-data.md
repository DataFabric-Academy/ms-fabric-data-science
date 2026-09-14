# แบบฝึกหัด 1: สำรวจข้อมูล FreshMart

- ประมาณ **30** นาที  
- รันบน Azure Machine Learning compute instance

ในแบบฝึกหัดนี้ คุณจะเรียนรู้วิธี:

- โหลด Data asset ชั้น Bronze แล้วตรวจคุณภาพข้อมูล
- อ่านสถิติและกราฟเพื่อหาแบบแผนก่อนสร้างโมเดล
- จดสิ่งที่ต้องแก้ก่อนส่งเข้า Automated ML

ศัพท์: [การสำรวจข้อมูลเบื้องต้น](../../docs/glossary.md#การสำรวจข้อมูลเบื้องต้น-exploratory-data-analysis) · [Churn](../../docs/glossary.md#churn)

## สิ่งที่ต้องมีก่อนเริ่ม

- แบบฝึกหัด 0 ผ่านแล้ว และหน้า **Data** มี `bronze-transactions` กับ `bronze-customers`
- เปิด `labs-azureml/notebooks/01-explore-data.ipynb`
- เคอร์เนล **Python 3.10 - SDK v2** บน compute instance ของคุณ

## สถานการณ์

คุณเป็นนักวิเคราะห์ของ FreshMart ทีมต้องการรู้ก่อนฝึกโมเดลว่าข้อมูลขาดตรงไหน ของเสียสูงที่สาขาแบบใด และสมาชิกที่เลิกซื้อต่างจากคนที่อยู่ต่ออย่างไร

## งานที่ 1: โหลดธุรกรรมจาก Data asset

1. (ตรวจเร็ว) ซ้ายมือเลือก **Data** แล้วเปิด `bronze-transactions` ดูแท็บ **Preview**
2. รันเซลล์นิยาม `load_table_or_csv` — ฟังก์ชันอ่าน Data asset ก่อน ถ้าไม่มีค่อยอ่านไฟล์
3. รันเซลล์โหลดธุรกรรม

```python
df = load_table_or_csv("bronze/transactions", "freshmart_transactions.csv")
print(df.shape)
df.head()
```

**เมื่องานนี้เสร็จ คุณควรเห็น:** `shape` ประมาณ `(3000, 14)`

คอลัมน์สำคัญ: `UnitsSold`, `DiscountRate`, `WasteUnits`, `WasteCost`, `StoreType`, `Category`

## งานที่ 2: ตรวจค่าว่าง

1. รันเซลล์คุณภาพข้อมูลใน notebook

**เมื่องานนี้เสร็จ คุณควรเห็น:** `DiscountRate` ว่าง **89 แถว (ประมาณ 3%)**  
คอลัมน์อื่นไม่ควรว่างจำนวนมาก — จดไว้ส่งแบบฝึกหัด 2

## งานที่ 3: อ่านการกระจายและกราฟ

1. รันเซลล์ `describe()` ของคอลัมน์ตัวเลข
2. รัน histogram ของ `UnitsSold` และ `WasteUnits`
3. รัน box plot `WasteUnits` ตาม `StoreType`

**เมื่องานนี้เสร็จ คุณควรเห็น**

- `WasteUnits` เบ้ขวา
- ค่าเฉลี่ยของเสีย **Express (ประมาณ 0.50)** สูงกว่า Hypermarket (ประมาณ 0.12)

## งานที่ 4: ดูความสัมพันธ์

1. รันเซลล์ heatmap ใน notebook

| คู่ | ค่า (ปัด 2 ตำแหน่ง) | ความหมาย |
| :--- | :--- | :--- |
| DiscountRate กับ UnitsSold | ประมาณ **+0.38** | ลดราคาแล้วขายได้มากขึ้น |
| DiscountRate กับ WasteUnits | ประมาณ **-0.12** | สินค้าที่ลดราคามักเหลือทิ้งน้อยลง |

## งานที่ 5: สำรวจ Churn ของสมาชิก

1. รันเซลล์โหลด `bronze/customers` (Data asset `bronze-customers`)
2. รัน scatter `RecencyDays` กับ `ComplaintCount` แยกสีตาม `Churn`

| รายการ | ค่าที่ต้องเห็น |
| :--- | :--- |
| สมาชิก | 1,500 |
| Churn = 1 | 290 คน (**19.3%**) |
| Age ว่าง | **37** แถว |
| MembershipTier | Bronze, Silver, Gold, Platinum |

**เมื่องานนี้เสร็จ คุณควรเห็น:** กลุ่มที่ขาดซื้อนานและร้องเรียนบ่อยกระจุกที่ `Churn = 1` และเซลล์สุดท้ายพิมพ์ `Lab 1 verification passed`

## ผ่านแบบฝึกหัดเมื่อ

- [ ] `Lab 1 verification passed`
- [ ] จด 3 ข้อส่งแบบฝึกหัด 2: เติม Age · แปลงหมวดหมู่เป็นตัวเลข · ปรับสเกลเงินและความถี่

## ล้างทรัพยากรเมื่อเลิกใช้

ถ้าจบคาบแล้ว ไป **Compute** เลือกเครื่องของคุณ แล้วเลือก **Stop**

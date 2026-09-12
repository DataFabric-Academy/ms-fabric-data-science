# Lab 0: เปิด Workspace และยืนยัน Lakehouse FreshMart

ในแล็บนี้คุณจะเปิดที่เก็บข้อมูล FreshMart ที่เตรียมไว้แล้ว ตรวจไฟล์ดิบและตาราง Bronze แล้วนำเข้า notebook จากเครื่องเพื่อยืนยันว่าพร้อมสำรวจข้อมูลใน Lab 1

แล็บนี้ใช้เวลาประมาณ **20** นาที  
ศัพท์ที่เกี่ยวข้อง: [Lakehouse](../../docs/glossary.md#lakehouse) · [จุดตรวจ](../../docs/glossary.md#จุดตรวจ-verification) · [Churn](../../docs/glossary.md#churn)

## สร้าง / เปิด workspace

> ต้องใช้ Fabric Trial, Premium หรือ Fabric capacity — ไม่ใช่ Personal  
> ดู [Fabric trial](https://aka.ms/fabrictrial)

1. เปิด [Microsoft Fabric](https://app.fabric.microsoft.com/home?experience=fabric) แล้วลงชื่อเข้าใช้
2. ซ้ายมือเลือก **Workspaces**
3. เปิด workspace **`labs`** ที่ผู้สอนเชิญไว้แล้ว  
   (ถ้าคอร์สให้สร้างเอง ให้ตั้งชื่อตามที่ผู้สอนกำหนด และเลือก license ที่มี Fabric capacity)
4. มุมล่างซ้ายสลับประสบการณ์เป็น **Data Science** ถ้ายังไม่ใช่

**สิ่งที่ควรเห็น:** ใน workspace มี Lakehouse ชื่อ `lh_freshmart`

> ชุดนี้ใช้ workspace ร่วมเพื่อให้ทุกคนได้ข้อมูล FreshMart ชุดเดียวกัน และเริ่มสำรวจข้อมูลใน Lab 1 ได้ทันที

## ตรวจไฟล์ดิบใน Lakehouse

1. เปิด `lh_freshmart`
2. ซ้ายมือเปิด **Files** แล้วเข้าโฟลเดอร์ `raw`
3. ต้องเห็นครบ 3 ไฟล์:
   - `freshmart_transactions.csv` — ธุรกรรมขายและของเสีย
   - `freshmart_customers.csv` — สมาชิกและสถานะ Churn (เลิกซื้อหรือไม่)
   - `freshmart_scoring_batch.csv` — ชุดทำนายใน Lab 4 (ยังไม่มีคอลัมน์ Churn)
4. เปิดพรีวิว `freshmart_transactions.csv` ได้

**สิ่งที่ควรเห็น:** ใต้ `Files/raw/` มีไฟล์ครบทั้งสามชื่อด้านบน

## ตรวจตาราง Bronze

1. ที่ **Tables** กด **Refresh**
2. ต้องเห็น schema **`bronze`** และตาราง `transactions`, `customers`  
   (ชื่อเต็ม: `bronze.transactions`, `bronze.customers` — ดู [schema.table](../../docs/glossary.md#schematable))

**สิ่งที่ควรเห็น:** จำนวนแถวประมาณ **3,000** (ธุรกรรม) และ **1,500** (สมาชิก)

## ลอง SQL สั้น ๆ (อินไซต์แรก)

1. มุมขวาบนสลับจาก **Lakehouse** เป็น **SQL analytics endpoint**
2. กด **+ New SQL query** แล้วรัน:

```sql
SELECT
    Category,
    COUNT(*) AS TotalTransactions,
    SUM(WasteCost) AS TotalWasteCost
FROM bronze.transactions
GROUP BY Category
ORDER BY TotalWasteCost DESC;
```

**สิ่งที่ควรเห็น:** หมวด **Bakery** ของเสียสูงสุด (ประมาณ 8,043) ตามด้วย Produce — นี่คือภาพธุรกิจ FreshMart ก่อนเข้า Lab 1

ถ้า SQL ยังไม่เจอตาราง: Refresh ที่ Lakehouse รอ 1–2 นาที แล้วลองใหม่

## นำเข้า notebook และรันจุดตรวจ

1. บนเครื่องรัน `git clone` repository คอร์สนี้ (ถ้ายังไม่ได้)
2. ใน Workspace กด **+ New item** แล้วเลือก **Notebook** จากนั้น **Create**
3. ใน Notebook: **File / …** แล้วเลือก **Import notebook / Upload**
4. เลือก `labs/notebooks/00-environment-verification.ipynb` จากเครื่อง
5. ตั้งชื่อ `00_FreshMart_Environment_Verification`
6. ด้านซ้ายแนบ Default Lakehouse = **`lh_freshmart`**
7. รอ Spark พร้อม (รอบแรกอาจ 1–2 นาที) แล้วรันทุกเซลล์ตามลำดับ

**สิ่งที่ควรเห็น:** เซลล์สุดท้ายพิมพ์ `Lab 0 verification passed`

Lab ถัดไปใช้วิธีเดียวกัน: Import จาก `labs/notebooks/` แล้วแนบ `lh_freshmart`

## ผ่านแล็บเมื่อ

- [ ] เปิด workspace `labs` ได้
- [ ] เห็น `lh_freshmart`, ไฟล์ใน `Files/raw/`, และตาราง Bronze
- [ ] SQL แสดง Bakery เป็นหมวดของเสียสูงสุด
- [ ] Notebook รันผ่าน `Lab 0 verification passed`

## แก้ปัญหาบ่อย

| อาการ | วิธีแก้ |
| --- | --- |
| หา workspace ไม่เจอ | ขอสิทธิ์เข้า `labs` จากผู้สอน |
| License เป็น Personal | แจ้งผู้สอนให้สลับ Trial/Capacity |
| Import ไม่ขึ้น | เลือกไฟล์ `.ipynb` จาก `labs/notebooks/` หลัง clone |
| Spark ค้าง Starting | รอ cold start แล้วรันเซลล์เดิมอีกครั้ง |

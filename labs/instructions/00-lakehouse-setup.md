# Lab 0: สร้าง Workspace ของตนเอง และเตรียม Lakehouse FreshMart

ในแล็บนี้คุณจะลงทะเบียน Fabric Trial ของตนเอง สร้าง workspace และ lakehouse ของตนเอง อัปโหลดไฟล์ FreshMart แล้วสร้างตาราง Bronze จากนั้นนำเข้า notebook เพื่อยืนยันว่าพร้อมสำรวจข้อมูลใน Lab 1

แล็บนี้ใช้เวลาประมาณ **30–40** นาที  
ศัพท์ที่เกี่ยวข้อง: [Lakehouse](../../docs/glossary.md#lakehouse) · [Medallion](../../docs/glossary.md#medallion-bronze--silver--gold) · [schema.table](../../docs/glossary.md#schematable) · [จุดตรวจ](../../docs/glossary.md#จุดตรวจ-verification) · [Churn](../../docs/glossary.md#churn)

> **กติกาห้องเรียน:** แต่ละคนใช้ Fabric Trial และ workspace ของตนเอง  
> **อย่าเชิญ** ผู้เรียนคนอื่นหรือผู้สอนเข้า workspace — ไม่มี workspace ร่วมในคอร์สนี้

## ลงทะเบียน Fabric Trial

ต้องใช้ Fabric Trial (หรือ Capacity ที่รองรับ Fabric) — ไม่ใช่ Personal / My workspace ที่ยังเป็น Power BI อย่างเดียว  
ดู [Try Microsoft Fabric for free](https://learn.microsoft.com/fabric/fundamentals/fabric-trial) และทางลัด [aka.ms/fabrictrial](https://aka.ms/fabrictrial)

1. เปิด [Microsoft Fabric](https://app.fabric.microsoft.com/home?experience=fabric) แล้วลงชื่อเข้าใช้ด้วยบัญชีของตนเอง
2. มุมขวาบนเปิด **Account manager** (รูปโปรไฟล์)
3. กด **Start trial** แล้วยอมรับเงื่อนไขเพื่อเปิด Trial 60 วัน  
   (ถ้าเห็น **Trial status** อยู่แล้ว ข้ามขั้นนี้ได้)
4. ถ้าบัญชียังไม่มีสิทธิ์ Power BI ให้เปิด [app.fabric.microsoft.com](https://app.fabric.microsoft.com) เพื่อรับ Fabric (Free) ก่อน แล้วค่อยเริ่ม Trial

**สิ่งที่ควรเห็น:** Account manager แสดงสถานะ Trial และจำนวนวันที่เหลือ

ถ้าไม่เห็นปุ่ม **Start trial**: ผู้ดูแล tenant อาจปิด Trial หรือโควตา Trial ขององค์กรเต็ม — ลองสร้างรายการ Fabric ใน workspace ของตนเองตาม [วิธีที่ 2 ของเอกสาร Trial](https://learn.microsoft.com/fabric/fundamentals/fabric-trial#method-2-trigger-a-fabric-trial-by-trying-to-use-a-fabric-feature) หรือแจ้งผู้สอนให้ช่วยดู tenant setting (ไม่ใช่ขอเข้า workspace ของใคร)

## สร้าง workspace ของตนเอง

1. ซ้ายมือเลือก **Workspaces** แล้วกด **+ New workspace**
2. ตั้งชื่อ **`labs`** (หรือ `labs-<ชื่อย่อ>` ถ้าชื่อซ้ำใน tenant)
3. ที่ **Advanced** เลือกประเภท workspace เป็น **Fabric Trial**
4. กด **Apply**
5. ที่มุมล่างซ้าย ให้สลับโหมดการทำงาน (Experience Switcher) เป็น **Data Science** (หากยังไม่ได้เลือก)

**สิ่งที่ควรเห็น:** เปิดเข้า workspace ที่ว่าง และเป็นเจ้าของคนเดียว — ไม่ต้องรอคำเชิญจากผู้สอน

อ้างอิง: [Create a workspace](https://learn.microsoft.com/fabric/fundamentals/create-workspaces)

## สร้าง Lakehouse และอัปโหลดไฟล์ข้อมูลต้นทาง

1. ใน workspace กด **+ New item** แล้วเลือก **Lakehouse**
2. ตั้งชื่อ **`lh_freshmart`**
3. เหลือช่อง **Lakehouse schemas** เปิดไว้ (ค่าเริ่มต้น) — อย่าปิด
4. กด **Create**

> **ทำไมชื่อ schema สำคัญ:** ในแล็บนี้ชั้น Medallion คือ**ชื่อ schema** ของ lakehouse เดียวกัน  
> ตารางจึงเรียกว่า `bronze.transactions` ไม่ใช่ `bronze_transactions`  
> `bronze` / `silver` / `gold` บอกสัญญาคุณภาพ ไม่ใช่แค่จัดกลุ่มใน Explorer — Lab 0 เขียน Bronze, Lab 2 เขียน Silver, Lab 4 เขียน Gold  
> `Files/raw/` เป็นพื้นที่พักไฟล์นำเข้า (Landing Zone) ยังไม่ใช่ตารางชั้น Bronze จนกว่า notebook จะเขียนเป็น Delta ใน schema `bronze`  
> เลือกเปิด schemas ได้ครั้งเดียวตอนสร้าง lakehouse  
> อธิบายเพิ่ม: [Medallion ใน M01](../../docs/01-fabric-architecture.md#ทำไมชื่อ-schema-สำคัญต่อ-medallion) · [glossary](../../docs/glossary.md#medallion-bronze--silver--gold)
5. เปิด **Files** แล้วสร้างโฟลเดอร์ `raw`
6. อัปโหลด 3 ไฟล์จากเครื่อง (หลัง `git clone` repository นี้ ไฟล์อยู่ที่ `labs/data/`):
   - `freshmart_transactions.csv` — ธุรกรรมขายและของเสีย
   - `freshmart_customers.csv` — สมาชิกและสถานะ Churn (เลิกซื้อหรือไม่)
   - `freshmart_scoring_batch.csv` — ชุดทำนายใน Lab 4 (ยังไม่มีคอลัมน์ Churn)
7. เปิดพรีวิว `freshmart_transactions.csv` ได้

**สิ่งที่ควรเห็น:** ใต้ `Files/raw/` มีไฟล์ครบทั้งสามชื่อด้านบน

อ้างอิง: [Create a lakehouse](https://learn.microsoft.com/fabric/data-engineering/create-lakehouse)

## นำเข้า notebook แล้วสร้างตาราง Bronze

1. ใน Workspace กด **+ New item** แล้วเลือก **Notebook** จากนั้น **Create**
2. ใน Notebook: **File / …** แล้วเลือก **Import notebook / Upload**
3. เลือก `labs/notebooks/00-environment-verification.ipynb` จากเครื่อง
4. ตั้งชื่อ `00_FreshMart_Environment_Verification`
5. ด้านซ้ายแนบ Default Lakehouse = **`lh_freshmart`**
6. รอ Spark พร้อม (รอบแรกอาจ 1–2 นาที) แล้วรันทุกเซลล์ตามลำดับ — เซลล์สร้าง schema `bronze` / `silver` / `gold` และตาราง `bronze.transactions`, `bronze.customers` จากไฟล์ใน `Files/raw/`

**สิ่งที่ควรเห็น:** เซลล์สร้างตารางพิมพ์จำนวนแถวประมาณ **3,000** และ **1,500** จากนั้นเซลล์สุดท้ายพิมพ์ `Lab 0 verification passed`

Lab ถัดไปใช้วิธีเดียวกัน: Import จาก `labs/notebooks/` แล้วแนบ `lh_freshmart`

## ตรวจตาราง Bronze บนหน้า Lakehouse

1. เปิด `lh_freshmart` แล้วที่ **Tables** กด **Refresh**
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

## ผ่านแล็บเมื่อ

- [ ] ลงทะเบียน Fabric Trial ของตนเองแล้ว
- [ ] สร้าง workspace ของตนเอง (แนะนำชื่อ `labs`) โดยไม่เชิญใครเข้า
- [ ] สร้าง `lh_freshmart` แล้วอัปโหลดไฟล์ครบใน `Files/raw/`
- [ ] มีตาราง Bronze และ SQL แสดง Bakery เป็นหมวดของเสียสูงสุด
- [ ] Notebook รันผ่าน `Lab 0 verification passed`

## แก้ปัญหาบ่อย

| อาการ | วิธีแก้ |
| --- | --- |
| ไม่เห็นปุ่ม Start trial | ลองสร้างรายการ Fabric เพื่อกระตุ้น Trial หรือให้ผู้สอนดู tenant setting — **อย่าขอเข้า workspace ของผู้อื่น** |
| สร้าง Lakehouse ไม่ได้ | ตรวจว่า workspace อยู่บน **Fabric Trial** ไม่ใช่ Personal |
| ไม่เจอไฟล์ใน `Files/raw/` | อัปโหลดสามไฟล์จาก `labs/data/` หลัง clone repository |
| Import ไม่ขึ้น | เลือกไฟล์ `.ipynb` จาก `labs/notebooks/` หลัง clone |
| Spark ค้าง Starting | รอ cold start แล้วรันเซลล์เดิมอีกครั้ง |
| SQL ไม่เจอ `bronze.transactions` | รันเซลล์สร้างตารางใน notebook ให้จบ แล้ว Refresh ที่ Lakehouse |

# Checklist รัน Lab 0–2 บน Fabric (ทีละเซลล์)

ใช้คู่กับ workspace **`labs`** และ Lakehouse **`lh_freshmart`**  
Portal: https://app.fabric.microsoft.com/groups/56c1925e-a9e9-44ec-9834-b64b6b07a4ad

อภิธานศัพท์: [../../docs/glossary.md](../../docs/glossary.md)

> ติ๊ก `[x]` เมื่อเห็นผลตาม “ต้องเห็น” — ถ้าไม่ตรง ดูคอลัมน์ “ถ้าติด”  
> รันทีละเซลล์ ให้เห็นผล แล้วค่อยไปต่อ

---

## ก่อน Lab 0 (ทำครั้งเดียว)

- [ ] เปิด workspace **`labs`**
- [ ] เปิด Lakehouse **`lh_freshmart`** แล้ว Refresh `Tables` / `Files`
- [ ] เห็นตาราง `bronze.transactions`, `bronze.customers`
- [ ] บนเครื่อง: `git clone` repository นี้
- [ ] ใน Fabric: สร้าง Notebook แล้ว **Import / Upload** จาก `labs/notebooks/` บนเครื่อง
- [ ] ในแต่ละ Notebook: แนบ Default Lakehouse = **`lh_freshmart`**
- [ ] รอ Spark/kernel พร้อม (รอบแรก 1–2 นาทีได้)

---

## Lab 0 — `00_FreshMart_Environment_Verification`

| # | เซลล์ | ทำอะไร | ต้องเห็น | ถ้าติด |
| --- | --- | --- | --- | --- |
| 0 | markdown | อ่านบทนำ | รู้ว่าแนบ lakehouse แล้ว | — |
| 1 | **รันโค้ด** loader | นิยาม `load_table_or_csv` | ไม่ error | แนบ lakehouse แล้วรันใหม่ |
| 2 | markdown | อ่านหัวข้อโหลด Bronze | — | — |
| 3 | **รันโค้ด** โหลด | อ่าน transactions + customers | `Transactions rows: 3,000` และ `Customers rows: 1,500` | ทางเลือกสำรอง CSV จาก `Files/raw` ได้ |
| 4 | markdown | อ่านจุดตรวจ | — | — |
| 5 | **รันโค้ด** จุดตรวจ | ตรวจจำนวนแถว | **`Lab 0 verification passed`** | อ่าน AssertionError ทั้งบรรทัด |

**ผ่าน Lab 0 เมื่อ:** เซลล์สุดท้ายพิมพ์ `Lab 0 verification passed`

---

## Lab 1 — `01_FreshMart_Exploratory_Data_Analysis`

| # | เซลล์ | ทำอะไร | ต้องเห็น | ถ้าติด |
| --- | --- | --- | --- | --- |
| 0 | markdown | อ่านบทบาทนักวิเคราะห์ | — | — |
| 1 | **รันโค้ด** loader | นิยาม loader | ไม่ error | แนบ lakehouse |
| 2–3 | markdown + **รัน** | โหลดธุรกรรม | shape `(3000, 14)` | กลับไป Lab 0 |
| 4–5 | markdown + **รัน** | คุณภาพข้อมูล | `DiscountRate` ว่างประมาณ 89 แถว (~3%) | — |
| 6–7 | markdown + **รัน** | describe | ตารางสถิติ 6 คอลัมน์ | — |
| 8–9 | markdown + **รัน** | histogram | ของเสีย (Waste) เบ้ขวา | รอ cold start |
| 10 | **รันโค้ด** | box plot ตาม StoreType | Express สูงกว่า Hypermarket โดยประมาณ | — |
| 11–12 | markdown + **รัน** | ความสัมพันธ์ | DiscountRate กับ UnitsSold ≈ +0.38 | — |
| 13–14 | markdown + **รัน** | สำรวจ churn | 1,500 คน, Churn ~19.3%, Age ว่าง 37 | — |
| 15 | **รันโค้ด** จุดตรวจ | assert สุดท้าย | **`Lab 1 verification passed`** | อ่าน error |

**จด 3 ข้อส่ง Lab 2:** เติม Age · แปลงหมวดหมู่ · ปรับสเกลตัวเลขเงินและความถี่

**ผ่าน Lab 1 เมื่อ:** `Lab 1 verification passed`

---

## Lab 2 — `02_FreshMart_Data_Preparation`

### ส่วน A — Data Wrangler (Add code to notebook ได้จริง)

- [ ] รันเซลล์โหลด `df` (sample 500 แถว) ให้จบ และ **kernel ว่าง**
- [ ] แท็บ **Home** เปิด **Data Wrangler** แล้วเลือก `df`
- [ ] Format `Category` / Filter Express / Group by `WasteCost` ตามคู่มือ
- [ ] กด **Add code to notebook** อย่างน้อยหนึ่งครั้ง แล้วรันเซลล์ตัวอย่าง `summarize_waste`

### ส่วน B — ฟีเจอร์สมาชิก (ส่งงาน Lab 3–4)

| # | เซลล์ | ทำอะไร | ต้องเห็น | ถ้าติด |
| --- | --- | --- | --- | --- |
| — | **รันโค้ด** | โหลด `df_cust` | shape `(1500, 11)`, Age ว่าง 37 | — |
| — | **รันโค้ด** | ฟังก์ชัน `fit_preprocessor` | ไม่ error | รันตามลำดับจากบน |
| — | **รันโค้ด** | transform | Age median **37.0**, one-hot ครบ, สเกลประมาณ 0–1 | — |
| — | **รันโค้ด** | บันทึก Silver + params | เห็นข้อความบันทึก | Refresh `Tables` |
| — | **รันโค้ด** | จุดตรวจ | **`Lab 2 verification passed`** | อ่าน error |

**ผ่าน Lab 2 เมื่อ:**

- [ ] ได้ใช้ Wrangler แล้ว Add code กลับ notebook (ส่วน A)
- [ ] `Lab 2 verification passed`
- [ ] เห็น `silver.customer_features` (1,500 แถว)
- [ ] มี `Files/params/feature_params.json`

---

## สรุปหลัง Lab 0–2

| รายการ | ค่าที่ต้องได้ |
| --- | --- |
| bronze.transactions | 3,000 แถว |
| bronze.customers | 1,500 แถว |
| DiscountRate ว่าง | ประมาณ 89 |
| Age ว่าง (ก่อน Lab 2) | 37 |
| อัตรา Churn | ประมาณ 19.3% |
| Age median (params) | 37.0 |
| silver.customer_features | 1,500 แถว |
| feature_params.json | มีใน `Files/params/` |

พร้อมแล้วค่อยเปิด Lab 3 (`03_FreshMart_Model_Training_MLflow`)

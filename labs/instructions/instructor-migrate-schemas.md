# Instructor: Migrate Lakehouse to bronze.* / silver.* / gold.*

เอกสารนี้สำหรับ **instructor เท่านั้น** — ผู้เรียนยังทำ Lab 0–4 ทีละขั้นเหมือนเดิม  
แค่ชื่อตารางเปลี่ยนจาก `bronze_transactions` เป็น `bronze.transactions`

## ทำไมต้องย้าย

Fabric skill (medallion) แนะนำ lakehouse แบบ schema-enabled:

| Schema | ตาราง |
| --- | --- |
| `bronze` | `transactions`, `customers` |
| `silver` | `customer_features` |
| `gold` | `freshmart_predictions` |

`Files/raw/*.csv` **ไม่เปลี่ยน** — landing zone เหมือนเดิม

## UX ผู้เรียนที่คงไว้

| เดิม | ใหม่ | ความรู้สึก |
| --- | --- | --- |
| `spark.read.table("bronze_transactions")` | `spark.read.table("bronze.transactions")` | เปลี่ยนแค่ `_` → `.` |
| SQL `FROM bronze_transactions` | `FROM bronze.transactions` | เหมือนกัน |
| Import notebook + แนบ `lh_freshmart` | เหมือนเดิม | ไม่มีขั้นเพิ่ม |
| จุดตรวจ 3,000 / 1,500 / 200 | เหมือนเดิม | ไม่เปลี่ยน |

Loader ใน notebook ยังลองชื่อเก่าเป็นทางเลือกสำรอง (fallback) ชั่วคราว — คลาสที่ยังไม่ migrate ก็รันได้

## ขั้นตอน migrate (ครั้งเดียวต่อ workspace)

1. เปิด notebook ใน workspace `labs` แนบ `lh_freshmart`
2. วางแล้วรัน:

```python
# คัดลอกจาก labs/scripts/migrate_to_schemas.py หรือ:
for schema in ("bronze", "silver", "gold"):
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {schema}")

pairs = [
    ("bronze.transactions", "bronze_transactions"),
    ("bronze.customers", "bronze_customers"),
    ("silver.customer_features", "silver_customer_features"),
    ("gold.freshmart_predictions", "gold_freshmart_predictions"),
]
for canonical, legacy in pairs:
    if spark.catalog.tableExists(legacy):
        spark.sql(f"CREATE OR REPLACE TABLE {canonical} AS SELECT * FROM {legacy}")
        print(canonical, spark.table(canonical).count())
```

3. Refresh **Tables** ใน Lakehouse — ต้องเห็นโฟลเดอร์/schema `bronze`, `silver`, `gold`
4. (ทางเลือกหลังยืนยันคลาสผ่าน) ลบตาราง flat เก่า:

```python
for legacy in [
    "bronze_transactions",
    "bronze_customers",
    "silver_customer_features",
    "gold_freshmart_predictions",
]:
    spark.sql(f"DROP TABLE IF EXISTS {legacy}")
```

หรือรัน `migrate(spark, drop_legacy=True)` จากสคริปต์

## จุดตรวจหลัง migrate

```sql
SELECT COUNT(*) FROM bronze.transactions;   -- 3000
SELECT COUNT(*) FROM bronze.customers;      -- 1500
```

ถ้ายังมี Silver/Gold จากรอบก่อน:

```sql
SELECT COUNT(*) FROM silver.customer_features;
SELECT COUNT(*) FROM gold.freshmart_predictions;
```

## Rollback

ชื่อใหม่ยังไม่พร้อม → ให้ผู้เรียนใช้ notebook เวอร์ชันนี้ได้ เพราะ loader ลอง flat name เก่าอัตโนมัติ  
หรือสร้างตาราง flat กลับจาก schema:

```sql
CREATE OR REPLACE TABLE bronze_transactions AS SELECT * FROM bronze.transactions;
```

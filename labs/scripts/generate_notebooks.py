"""Generate self-contained Fabric/local Jupyter notebooks for FreshMart labs."""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "labs" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import freshmart_features as features  # noqa: E402

NB_DIR = ROOT / "labs" / "notebooks"


def make_notebook(cells: list[dict]) -> dict:
    """Build a notebook document with Fabric Lakehouse metadata."""
    return {
        "cells": cells,
        "metadata": {
            "language_info": {"name": "python"},
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "microsoft": {
                "host": {
                    "Fabric": {
                        "lakehouse": {"default_lakehouse": "lh_freshmart"}
                    }
                }
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def md_cell(source: str) -> dict:
    """Create a markdown cell."""
    text = source.strip("\n") + "\n"
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code_cell(source: str) -> dict:
    """Create a code cell."""
    text = source.strip("\n") + "\n"
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.splitlines(keepends=True),
    }


LOADER = r'''
from pathlib import Path
import pandas as pd

# Schema-qualified names (preferred). Legacy flat names still tried as fallback.
BRONZE_TRANSACTIONS = "bronze.transactions"
BRONZE_CUSTOMERS = "bronze.customers"
SILVER_CUSTOMER_FEATURES = "silver.customer_features"
GOLD_PREDICTIONS = "gold.freshmart_predictions"

def _first_existing(paths):
    for path in paths:
        candidate = Path(path)
        if candidate.exists() and candidate.is_file():
            return candidate
    return None

def load_csv(file_name: str) -> pd.DataFrame:
    found = _first_existing([
        f"/lakehouse/default/Files/raw/{file_name}",
        f"Files/raw/{file_name}",
        f"../data/{file_name}",
        f"labs/data/{file_name}",
        file_name,
    ])
    if found is None:
        raise FileNotFoundError(f"Cannot find {file_name}. Upload it to Files/raw or place it under labs/data.")
    print(f"Loaded CSV: {found}")
    return pd.read_csv(found)

def _table_candidates(table_name: str) -> list[str]:
    legacy = {
        "bronze.transactions": "bronze_transactions",
        "bronze.customers": "bronze_customers",
        "silver.customer_features": "silver_customer_features",
        "gold.freshmart_predictions": "gold_freshmart_predictions",
    }
    names = [table_name]
    if table_name in legacy:
        names.append(legacy[table_name])
    return names

def load_table_or_csv(table_name: str, file_name: str) -> pd.DataFrame:
    last_error = None
    for candidate in _table_candidates(table_name):
        try:
            frame = spark.read.table(candidate).toPandas()
            print(f"Loaded Spark table {candidate}: {len(frame):,} rows")
            return frame
        except Exception as exc:
            last_error = exc
    print(f"Spark table '{table_name}' unavailable ({last_error}). Falling back to CSV.")
    return load_csv(file_name)
'''.strip()

FEATURE_SOURCE = "\n\n".join(
    [
        inspect.getsource(features.FeatureParams),
        inspect.getsource(features.validate_raw_customers),
        inspect.getsource(features._require_columns),
        inspect.getsource(features._numeric_copy),
        inspect.getsource(features.fit_preprocessor),
        inspect.getsource(features._one_hot_categories),
        inspect.getsource(features._min_max_scale),
        inspect.getsource(features.transform_customers),
        inspect.getsource(features.model_matrix),
        inspect.getsource(features.save_feature_params),
        inspect.getsource(features.load_feature_params),
    ]
)

CONSTANTS = f'''
ID_COLUMN = {features.ID_COLUMN!r}
TARGET_COLUMN = {features.TARGET_COLUMN!r}
CATEGORICAL_COLUMNS = {features.CATEGORICAL_COLUMNS!r}
IMPUTE_MEDIAN_COLUMNS = {features.IMPUTE_MEDIAN_COLUMNS!r}
SCALE_COLUMNS = {features.SCALE_COLUMNS!r}
DUMMY_COLUMNS = {features.DUMMY_COLUMNS!r}
PASSTHROUGH_COLUMNS = {features.PASSTHROUGH_COLUMNS!r}
FEATURE_COLUMNS = {features.FEATURE_COLUMNS!r}
REQUIRED_RAW_COLUMNS = {features.REQUIRED_RAW_COLUMNS!r}
'''.strip()


def write_notebook(name: str, cells: list[dict]) -> None:
    """Serialize a notebook to labs/notebooks."""
    NB_DIR.mkdir(parents=True, exist_ok=True)
    path = NB_DIR / name
    path.write_text(json.dumps(make_notebook(cells), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {path}")


def build() -> None:
    """Generate all published FreshMart notebooks."""
    write_notebook(
        "00-environment-verification.ipynb",
        [
            md_cell(
                """# FreshMart Lab 0: Environment Verification
**Microsoft Fabric Data Science**

เป้าหมาย: ยืนยันว่าพร้อมเข้า Lab 1 — **ไม่ต้องวิเคราะห์ธุรกิจในแล็บนี้**

### ก่อนรัน (เช็ก 30 วินาที)
1. Workspace = `labs`
2. แนบ Default Lakehouse = **`lh_freshmart`** (ซ้ายมือของ notebook)
3. รอ Spark ขึ้น Ready (รอบแรก 1–2 นาทีได้ — **อย่ารันหลายเซลล์ซ้อน**)

### คำศัพท์สั้น ๆ
| คำ | ความหมาย |
| --- | --- |
| Lakehouse | ที่เก็บไฟล์ + ตารางใน OneLake |
| Bronze | ชั้นข้อมูลดิบที่ instructor เตรียมไว้ |
| `bronze.transactions` | ตารางธุรกรรมใน schema `bronze` |

### ถ้าติด — อ่านก่อนถาม TA
| อาการ | ทำอะไร |
| --- | --- |
| `Spark table unavailable` แล้วโหลด CSV | **ปกติ** ถ้ายังเห็นแถวครบ |
| Kernel / Spark Starting ค้าง | รอ แล้วรันเซลล์เดิมอีกครั้งทีละเซลล์ |
| ไม่เจอไฟล์/ตาราง | แจ้ง instructor — อย่าสร้าง lakehouse เอง |
| AssertionError จำนวนแถว | ไม่ผ่าน Lab 0 — อย่าข้ามไป Lab 1 |"""
            ),
            md_cell(
                """### เซลล์ถัดไป: ฟังก์ชันโหลดข้อมูล

โค้ดด้านล่างนิยาม `load_table_or_csv` ให้แล้ว — **รันครั้งเดียวแล้วใช้ต่อทุก Lab**

- พยายามอ่านตาราง Lakehouse ก่อน (`bronze.transactions` ฯลฯ)
- ถ้าไม่มีตาราง จะอ่าน `Files/raw/*.csv` ให้อัตโนมัติ
- ไม่ต้องแก้โค้ดนี้"""
            ),
            code_cell(LOADER),
            md_cell(
                """### โหลด Bronze แล้วดูตัวอย่างแถว

**โค้ดนี้ทำอะไร:** อ่านตารางสมาชิก + ธุรกรรม แล้วพิมพ์จำนวนแถวและ `head(5)`

**ต้องเห็น**
- Transactions ≈ **3,000** แถว
- Customers ≈ **1,500** แถว

ชื่อตารางแบบ `bronze.xxx` = schema.table (มาตรฐาน lakehouse แบบมี schema)"""
            ),
            code_cell(
                """df_tx = load_table_or_csv("bronze.transactions", "freshmart_transactions.csv")
df_cust = load_table_or_csv("bronze.customers", "freshmart_customers.csv")

print(f"Transactions rows: {len(df_tx):,}")
print(f"Customers rows: {len(df_cust):,}")
print("Transaction columns:", list(df_tx.columns))
print("Customer columns:", list(df_cust.columns))
display(df_tx.head(5))
display(df_cust.head(5))"""
            ),
            md_cell(
                """### จุดตรวจอัตโนมัติ

**โค้ดนี้ทำอะไร:** ถ้าจำนวนแถวไม่ตรง จะ `raise AssertionError` และหยุด

- ผ่านแล้วจะพิมพ์ `Lab 0 verification passed`
- ไม่ผ่าน = สภาพแวดล้อมยังไม่พร้อม — **ถาม TA พร้อมคัดลอกข้อความ error ทั้งบรรทัด**"""
            ),
            code_cell(
                """if len(df_tx) != 3000:
    raise AssertionError(
        f"คาดว่าธุรกรรม 3,000 แถว แต่ได้ {len(df_tx):,} — ตรวจ Files/raw หรือตาราง bronze.transactions"
    )
if len(df_cust) != 1500:
    raise AssertionError(
        f"คาดว่าสมาชิก 1,500 แถว แต่ได้ {len(df_cust):,} — ตรวจ Files/raw หรือตาราง bronze.customers"
    )
print("Lab 0 verification passed")"""
            ),
        ],
    )

    write_notebook(
        "01-explore-data.ipynb",
        [
            md_cell(
                """# FreshMart Lab 1: Exploratory Data Analysis
**Microsoft Fabric Data Science**

บทบาท: **Analyst** — สำรวจข้อมูลก่อนสร้างโมเดล  
จด **3 ข้อสังเกตสั้น ๆ** ส่ง Lab 2 (ไม่ต้องจำสูตรสถิติ)

### สิ่งที่แล็บนี้ตอบ
1. ข้อมูลขาดตรงไหน?
2. ของเสียสูงที่ประเภทสาขาไหน?
3. คนที่ Churn พฤติกรรมต่างจากคนอยู่ต่ออย่างไร?

### ถ้าติด — อ่านก่อนถาม TA
| อาการ | ความหมาย |
| --- | --- |
| กราฟไม่ขึ้น | รอเซลล์ก่อนหน้าจบ แล้วรันใหม่ |
| ค่าสหสัมพันธ์ไม่ตรงทศนิยมทุกตัว | ปัด 2 ตำแหน่งใกล้เคียงพอ |
| แนบ lakehouse ยังไม่ได้ | กลับไป Lab 0 |"""
            ),
            md_cell(
                """### เตรียมตัวโหลดข้อมูล

รันเซลล์ถัดไปเพื่อนิยาม `load_table_or_csv` (เหมือน Lab 0) — **อย่าข้าม**"""
            ),
            code_cell(LOADER),
            md_cell(
                """### ขั้นตอนที่ 1: โหลดธุรกรรม

**โค้ดนี้ทำอะไร:** อ่าน `bronze.transactions` แล้วแปลงเป็น Pandas

- `shape` = `(จำนวนแถว, จำนวนคอลัมน์)` → ต้องได้ประมาณ `(3000, 14)`
- `head()` = ดู 5 แถวแรก เพื่อรู้จักคอลัมน์ เช่น `WasteUnits`, `StoreType`"""
            ),
            code_cell(
                """df = load_table_or_csv("bronze.transactions", "freshmart_transactions.csv")
print(f"Pandas DataFrame shape: {df.shape}")
df.head()"""
            ),
            md_cell(
                """### ขั้นตอนที่ 2: คุณภาพข้อมูล (ค่าว่าง)

**ความรู้จำเป็น**
- ค่าว่าง (missing) ทำให้โมเดล/สถิติเพี้ยน — ต้องรู้ก่อนแก้ใน Lab 2
- `isnull().sum()` นับแถวว่างต่อคอลัมน์

**ต้องเห็น:** `DiscountRate` ว่างประมาณ **89 แถว (~3%)**  
คอลัมน์อื่นไม่ควรว่างจำนวนมาก — ถ้าเป็นแบบนั้น แจ้ง TA"""
            ),
            code_cell(
                """print("=== DataFrame Info ===")
df.info()
print("\\n=== Missing Values Count ===")
missing = df.isnull().sum()
print(missing[missing > 0])
print(f"DiscountRate missing rate: {df['DiscountRate'].isna().mean():.2%}")"""
            ),
            md_cell(
                """### ขั้นตอนที่ 3: สถิติเชิงพรรณนา

**โค้ดนี้ทำอะไร:** `describe()` สรุป mean / min / max / เปอร์เซ็นไทล์

ดูคอลัมน์ `WasteUnits`: ค่าส่วนใหญ่ต่ำ แต่มีหางยาว (= เบ้ขวา) — ของเสียกระจุกบางวัน/บางสาขา"""
            ),
            code_cell(
                """df[["UnitsSold", "UnitPrice", "DiscountRate", "SalesAmount", "WasteUnits", "WasteCost"]].describe()"""
            ),
            md_cell(
                """### ขั้นตอนที่ 4: Histogram — เห็นการกระจาย

**ความรู้จำเป็น**
- Histogram = นับความถี่ตามช่วงค่า
- เส้นโค้งบนกราฟช่วยดูรูปแบบการกระจาย

**ต้องเห็น:** `WasteUnits` เบ้ขวา (ค่าสูงมีน้อย)"""
            ),
            code_cell(
                """import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.histplot(df["UnitsSold"], bins=15, kde=True, color="#00D2B4", ax=axes[0])
axes[0].set_title("Distribution of Units Sold")
sns.histplot(df["WasteUnits"], bins=10, kde=True, color="#F43F5E", ax=axes[1])
axes[1].set_title("Distribution of Waste Units (right-skewed)")
plt.tight_layout()
plt.show()"""
            ),
            md_cell(
                """### Box plot ตามประเภทสาขา

**ความรู้จำเป็น:** Box plot เปรียบการกระจายระหว่างกลุ่มได้เร็ว

**อินไซต์ที่คาดหวัง:** Express ของเสียสูงกว่า Hypermarket โดยประมาณ  
(พื้นที่จัดเก็บจำกัด / ของเสียช่วงสุดสัปดาห์)

ไม่ต้องได้ตัวเลขเป๊ะทุกทศนิยม — เห็นแนวโน้มถูกทางพอ"""
            ),
            code_cell(
                """plt.figure(figsize=(10, 5))
sns.boxplot(data=df, x="StoreType", y="WasteUnits", hue="StoreType", palette="Set2", legend=False)
plt.title("Waste Units by Store Type")
plt.show()"""
            ),
            md_cell(
                """### ขั้นตอนที่ 5: Correlation

**ความรู้จำเป็น**
- ค่าใกล้ **+1** = ไปด้วยกัน, ใกล้ **-1** = สวนทาง, ใกล้ **0** = เกือบไม่เกี่ยว
- Heatmap คือตารางสหสัมพันธ์แบบสี

**ค่าอ้างอิงชุดนี้ (ปัด 2 ตำแหน่ง)**
- DiscountRate ↔ UnitsSold ≈ **+0.38** (ลดราคาแล้วขายดีขึ้น)
- DiscountRate ↔ WasteUnits ≈ **-0.12** (ลดราคามักเหลือทิ้งน้อยลง)"""
            ),
            code_cell(
                """numeric_cols = ["UnitsSold", "UnitPrice", "DiscountRate", "SalesAmount", "WasteUnits", "WasteCost", "IsWeekend"]
corr_matrix = df[numeric_cols].corr(numeric_only=True)
print(corr_matrix.round(2))

plt.figure(figsize=(9, 7))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="vlag", vmin=-1, vmax=1, linewidths=0.5)
plt.title("FreshMart Feature Correlation Matrix")
plt.show()"""
            ),
            md_cell(
                """### ขั้นตอนที่ 6: สำรวจ Churn ของสมาชิก

**ความรู้จำเป็น**
- `Churn = 1` = มีแนวโน้มยกเลิก, `0` = อยู่ต่อ
- อัตรา Churn ชุดนี้ ≈ **19.3%** (290 จาก 1,500)
- `Age` ว่าง **37** แถว → Lab 2 จะเติมด้วย median

Scatter ด้านล่าง: คนขาดซื้อนาน (`RecencyDays` สูง) + ร้องเรียนบ่อย มักกระจุกที่ Churn=1"""
            ),
            code_cell(
                """df_cust = load_table_or_csv("bronze.customers", "freshmart_customers.csv")
print(f"Total Customers: {len(df_cust):,}")
print(df_cust["Churn"].value_counts(normalize=True).rename("rate"))
print(f"Age missing: {df_cust['Age'].isna().sum()} ({df_cust['Age'].isna().mean():.2%})")

plt.figure(figsize=(10, 5))
sns.scatterplot(
    data=df_cust,
    x="RecencyDays",
    y="ComplaintCount",
    hue="Churn",
    palette={0: "#00D2B4", 1: "#F43F5E"},
    alpha=0.7,
)
plt.title("Customer Churn Pattern: Recency vs Complaint Count")
plt.show()"""
            ),
            md_cell(
                """### จุดตรวจ Lab 1

ผ่านแล้วพิมพ์ `Lab 1 verification passed`  
ก่อนไป Lab 2 จด 3 ข้อ: **เติม Age · แปลงหมวดหมู่ · ปรับสเกลเงิน/ความถี่**"""
            ),
            code_cell(
                """if len(df) != 3000:
    raise AssertionError(f"คาดว่าธุรกรรม 3,000 แถว แต่ได้ {len(df):,}")
if len(df_cust) != 1500:
    raise AssertionError(f"คาดว่าสมาชิก 1,500 แถว แต่ได้ {len(df_cust):,}")
if df["DiscountRate"].isna().sum() == 0:
    raise AssertionError("ชุดนี้ควรมี DiscountRate ว่าง เพื่อฝึกจัดการค่าว่างใน Lab 2")
if df_cust["Age"].isna().sum() == 0:
    raise AssertionError("ชุดนี้ควรมี Age ว่าง เพื่อฝึกเติมค่าใน Lab 2")
print("Lab 1 verification passed")"""
            ),
        ],
    )

    write_notebook(
        "02-preprocess-data-wrangler.ipynb",
        [
            md_cell(
                """# FreshMart Lab 2: Data Wrangler + Feature Engineering
**Microsoft Fabric Data Science**

เป้าหมาย: (A) ใช้ Data Wrangler สร้างโค้ดได้จริง  (B) เตรียมฟีเจอร์สมาชิกให้ Lab 3–4

### กฎทองที่ต้องจำ (ลดคำถาม Lab 4 ครึ่งหนึ่ง)
โมเดลเรียนรู้จาก **min/max ของชุดฝึก 1,500 คน**  
Lab 4 ทำนายชุดใหม่ 200 คน — **ห้ามคำนวณสเกลใหม่** ต้องใช้ `feature_params.json` จากแล็บนี้

### ถ้าติด — อ่านก่อนถาม TA
| อาการ | ทำอะไร |
| --- | --- |
| Data Wrangler เปิดไม่ได้ | รอเคอร์เนลว่าง (เซลล์ก่อนหน้าต้องจบ) |
| หาแท็บ Data Wrangler ไม่เจอ | แท็บ **Home** หรือปุ่มใต้ตาราง `df` |
| Export โค้ด Wrangler แล้วสับสน | ส่วน A เป็นการฝึก UI — **ส่วน B ต้องรันเซลล์ที่เตรียมให้** เพื่อส่งงาน |"""
            ),
            md_cell(
                """### เตรียมฟังก์ชันโหลด

รันเซลล์ถัดไปก่อนเสมอ"""
            ),
            code_cell("import json\nfrom pathlib import Path\nimport pandas as pd\n\n" + LOADER),
            md_cell(
                """### ส่วน A — โหลดธุรกรรมสำหรับ Data Wrangler

**โค้ดนี้ทำอะไร:** โหลดธุรกรรมแล้วสุ่ม **500 แถว** ให้ UI Wrangler เร็วขึ้น

ตัวแปรสำคัญ: **`df`** ← ต้องมีก่อนเปิด Data Wrangler"""
            ),
            code_cell(
                """df = load_table_or_csv("bronze.transactions", "freshmart_transactions.csv")
df = df.sample(n=500, random_state=1).reset_index(drop=True)
print("Sample for Data Wrangler:", df.shape)
df.head(4)"""
            ),
            md_cell(
                """### ส่วน A — ใช้ Data Wrangler (ทำตามทีละข้อ)

1. รอ kernel ว่าง → แท็บ **Home** → **Data Wrangler** → เลือก **`df`**
2. ดู Summary ของ `WasteCost`
3. **Format** คอลัมน์ `Category` (Capitalize all words) → Apply
4. ลอง **Filter** `StoreType = Express` และ/หรือ **Sort** `WasteCost` Descending
5. ลบขั้น Filter/Sort ได้จาก **Cleaning steps** ถ้าต้องการใช้ทั้งตัวอย่าง
6. **Group by** `Category` + aggregate `WasteCost` (Mean) → **Add code to notebook**

เซลล์ถัดไปเป็นตัวอย่างโครงฟังก์ชัน — ถ้าคุณ Export โค้ดจาก UI มาเอง ให้วางแทนได้"""
            ),
            code_cell(
                """def summarize_waste(frame: pd.DataFrame) -> pd.DataFrame:
    \"\"\"ตัวอย่างหลัง Export จาก Data Wrangler — ปรับให้ตรงโค้ดที่คุณได้จาก UI\"\"\"
    out = frame.groupby(["Category"]).agg(WasteCost_mean=("WasteCost", "mean")).reset_index()
    return out

print(summarize_waste(df))"""
            ),
            md_cell(
                """### ส่วน B — โหลดสมาชิกสำหรับโมเดล

**ทำไมแยกจากส่วน A:** Wrangler ฝึกกับธุรกรรม / โมเดล Churn ใช้ตารางสมาชิก

**ต้องเห็น:** shape ≈ `(1500, 11)` และ Age ว่าง **37** แถว

(ทางเลือก) เปิด Wrangler กับ `df_cust` เพื่อลอง Fill / One-hot / Scale  
**ส่งงาน Lab 3–4 = รันเซลล์สัญญาฟีเจอร์ด้านล่างเท่านั้น**"""
            ),
            code_cell(
                """df_cust = load_table_or_csv("bronze.customers", "freshmart_customers.csv")
print("Customers DataFrame loaded:", df_cust.shape)
print("Age missing:", int(df_cust["Age"].isna().sum()))
df_cust.head(3)"""
            ),
            md_cell(
                """### ส่วน B — สัญญาฟีเจอร์ (ความรู้สั้น ๆ)

เซลล์ถัดไปฝังฟังก์ชัน `fit_preprocessor` / `transform_customers` ให้แล้ว

| ขั้น | ความหมาย |
| --- | --- |
| เติม Age ด้วย median | ชุดนี้ median = **37.0** |
| One-hot | แปลง `MembershipTier` / `Gender` เป็นคอลัมน์ 0/1 |
| Min-max scale | ปรับเงิน/ความถี่ให้อยู่ช่วงประมาณ 0–1 จาก**ชุดฝึก** |

**รันเซลล์ฟังก์ชันก่อน** แล้วค่อยรันเซลล์ `fit` / `transform`"""
            ),
            code_cell(
                "from dataclasses import asdict, dataclass\nfrom typing import Any\nimport logging\n\n"
                "logger = logging.getLogger(__name__)\n\n" + CONSTANTS + "\n\n" + FEATURE_SOURCE
            ),
            md_cell(
                """### fit แล้ว transform

**โค้ดนี้ทำอะไร**
1. `fit_preprocessor` จำ median/min/max จากชุดฝึก
2. `transform_customers` สร้างตารางฟีเจอร์พร้อมใช้

ตรวจ Age median ≈ 37.0 และคอลัมน์ one-hot ครบ"""
            ),
            code_cell(
                """params = fit_preprocessor(df_cust)
df_clean = transform_customers(df_cust, params, require_target=True)
print(f"Cleaned DataFrame Shape: {df_clean.shape}")
print("Feature columns:", params.feature_columns)
print(f"Age median used for imputation: {params.age_median:.1f}")
display(df_clean.head(5))"""
            ),
            md_cell(
                """### บันทึก Silver + params

**โค้ดนี้ทำอะไร**
- เขียน `Files/params/feature_params.json` (Lab 4 ต้องใช้ไฟล์นี้)
- เขียนตาราง `silver.customer_features` ลง Lakehouse

ถ้า Spark เขียนตารางไม่ได้ จะมีไฟล์ท้องถิ่นสำรอง — ในห้องเรียนควรเห็นข้อความ Saved ลง Files/params หรือ Lakehouse"""
            ),
            code_cell(
                r'''params_json = json.dumps(params.to_dict(), indent=2)
local_dir = Path("labs/data/.local")
local_dir.mkdir(parents=True, exist_ok=True)
(local_dir / "feature_params.json").write_text(params_json, encoding="utf-8")

saved_to_files = False
for writer in ("notebookutils", "mssparkutils"):
    try:
        fs = __import__(writer).fs
        fs.mkdirs("Files/params")
        fs.put("Files/params/feature_params.json", params_json, True)
        saved_to_files = True
        print(f"Saved Files/params/feature_params.json via {writer}")
        break
    except Exception as exc:
        print(f"{writer} unavailable: {exc}")

if not saved_to_files:
    print("Saved local feature_params.json only")

try:
    spark.createDataFrame(df_clean).write.format("delta").mode("overwrite").saveAsTable("silver.customer_features")
    print("Saved silver.customer_features to Lakehouse")
except Exception as exc:
    out = local_dir / "silver_customer_features.csv"
    df_clean.to_csv(out, index=False)
    print(f"Spark write unavailable ({exc}). Wrote {out}")'''
            ),
            md_cell(
                """### จุดตรวจ Lab 2

ผ่านแล้วพิมพ์ `Lab 2 verification passed`  
Refresh Tables แล้วควรเห็น `silver.customer_features`"""
            ),
            code_cell(
                """if df_clean["Age"].isna().sum() != 0:
    raise AssertionError("หลังเตรียมฟีเจอร์แล้ว Age ไม่ควรว่าง")
if not set(["MembershipTier_Bronze", "Gender_F"]).issubset(df_clean.columns):
    raise AssertionError("ขาดคอลัมน์ one-hot ที่โมเดลคาดหวัง — รันเซลล์ fit/transform อีกครั้ง")
if df_clean["MonetaryTotal"].max() > 1.000001:
    raise AssertionError("MonetaryTotal ควรอยู่ในช่วงประมาณ 0–1 หลัง scale จากชุดฝึก")
print("Lab 2 verification passed")"""
            ),
        ],
    )

    write_notebook(
        "03-train-track-mlflow.ipynb",
        [
            md_cell(
                """# FreshMart Lab 3: Train and Track Models with MLflow
**Microsoft Fabric Data Science**

เป้าหมาย: ฝึกโมเดล 2 ตัว → เทียบ AUC → ลงทะเบียนตัวชนะเป็น `freshmart-churn-model`

### คำศัพท์ (จำแค่นี้พอ)
| คำ | ความหมาย |
| --- | --- |
| Experiment | สมุดบันทึกการทดลองใน Workspace |
| Run | หนึ่งครั้งที่ฝึกโมเดล |
| AUC | คะแนนแยก Churn กับอยู่ต่อ (ใกล้ 1 ดีกว่า) |
| Signature | รายชื่อคอลัมน์ที่โมเดลคาดหวัง — ต้องตรง Lab 2 |

### ค่าอ้างอิงชุดนี้ (seed 42)
- Decision Tree AUC ≈ **0.77**
- Random Forest AUC ≈ **0.86** (ควรชนะ)

### ถ้าติด — อ่านก่อนถาม TA
| อาการ | ทำอะไร |
| --- | --- |
| หา Experiment ไม่เจอ | Refresh workspace / รันเซลล์ `set_experiment` อีกครั้ง |
| RF แพ้ DT | ตรวจว่า Lab 2 บันทึก Silver + params ครบ |
| MLflow unavailable | ในห้องเรียนไม่ควรเกิดบ่อย — ส่งข้อความ error ให้ TA |"""
            ),
            md_cell("### เตรียม loader + ฟังก์ชันฟีเจอร์ (รันตามลำดับ)"),
            code_cell("import json\nfrom pathlib import Path\nimport pandas as pd\n\n" + LOADER),
            code_cell(
                "from dataclasses import asdict, dataclass\nfrom typing import Any\nimport logging\n\n"
                "logger = logging.getLogger(__name__)\n\n" + CONSTANTS + "\n\n" + FEATURE_SOURCE
            ),
            md_cell(
                """### ขั้นตอนที่ 1: โหลด Silver แล้วแยก Train/Test

**โค้ดนี้ทำอะไร**
1. โหลด `silver.customer_features` (จาก Lab 2)
2. แยก `X` = ฟีเจอร์, `y` = Churn
3. แบ่ง Train 80% / Test 20% แบบ `stratify=y` ให้สัดส่วน Churn สมดุล

**ต้องเห็น:** Train 1,200 · Test 300 · ฟีเจอร์ 14 คอลัมน์  
อย่าใส่ `CustomerID` หรือ `Churn` ใน X"""
            ),
            code_cell(
                r'''df_features = load_table_or_csv("silver.customer_features", ".local/silver_customer_features.csv")
if "MembershipTier_Bronze" not in df_features.columns:
    raw = load_table_or_csv("bronze.customers", "freshmart_customers.csv")
    params = fit_preprocessor(raw)
    df_features = transform_customers(raw, params, require_target=True)
else:
    params_path = _first_existing([
        "Files/params/feature_params.json",
        "/lakehouse/default/Files/params/feature_params.json",
        "labs/data/.local/feature_params.json",
    ])
    if params_path:
        params = load_feature_params(params_path)
    else:
        raw = load_table_or_csv("bronze.customers", "freshmart_customers.csv")
        params = fit_preprocessor(raw)

X = model_matrix(df_features, params)
y = df_features["Churn"].astype(int)
print(f"Features ({len(X.columns)}):", list(X.columns))
print(f"Dataset shape: X={X.shape}, y={y.shape}")

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"Train size: {len(X_train):,}, Test size: {len(X_test):,}")'''
            ),
            md_cell(
                """### ขั้นตอนที่ 2: สร้าง MLflow Experiment

**โค้ดนี้ทำอะไร:** ตั้งชื่อ experiment `freshmart-churn-prediction`  
Fabric จะสร้าง item ประเภท Experiment ใน Workspace ให้อัตโนมัติ — ไปเปิดดูได้หลังฝึกโมเดล"""
            ),
            code_cell(
                r'''mlflow_ready = True
try:
    import mlflow
    import mlflow.sklearn
    from mlflow.models.signature import infer_signature
    experiment_name = "freshmart-churn-prediction"
    mlflow.set_experiment(experiment_name)
    print(f"MLflow Experiment set to: '{experiment_name}'")
except Exception as exc:
    mlflow_ready = False
    infer_signature = None
    print(f"MLflow unavailable ({exc}). Training will still run locally.")'''
            ),
            md_cell(
                """### ขั้นตอนที่ 3: Baseline — Decision Tree

**ความรู้สั้น ๆ:** Decision Tree = ต้นไม้ตัดสินใจ อ่านง่าย แต่แม่นน้อยกว่าโมเดลรวมต้นไม้หลายต้น

**โค้ดนี้ทำอะไร:** ฝึก `DecisionTreeClassifier` แล้วบันทึกเมตริก + โมเดลลง MLflow"""
            ),
            code_cell(
                r'''from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def evaluate(model, name):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    metrics = {
        "test_accuracy": accuracy_score(y_test, y_pred),
        "test_precision": precision_score(y_test, y_pred),
        "test_recall": recall_score(y_test, y_pred),
        "test_f1_score": f1_score(y_test, y_pred),
        "test_roc_auc": roc_auc_score(y_test, y_prob),
    }
    print(f"[{name}] F1={metrics['test_f1_score']:.4f} Recall={metrics['test_recall']:.4f} AUC={metrics['test_roc_auc']:.4f}")
    return metrics

dt_model = DecisionTreeClassifier(max_depth=5, random_state=42)
if mlflow_ready:
    with mlflow.start_run(run_name="Run_01_DecisionTree_Baseline"):
        mlflow.autolog(log_models=False)
        dt_model.fit(X_train, y_train)
        metrics = evaluate(dt_model, "Run 1 Decision Tree")
        for key, value in metrics.items():
            mlflow.log_metric(key, value)
        signature = infer_signature(X_train, dt_model.predict(X_train))
        mlflow.sklearn.log_model(dt_model, "model", signature=signature)
else:
    dt_model.fit(X_train, y_train)
    evaluate(dt_model, "Run 1 Decision Tree")'''
            ),
            md_cell(
                """### ขั้นตอนที่ 4: Champion — Random Forest

**ความรู้สั้น ๆ:** Random Forest = รวม Decision Tree หลายต้น ลด overfitting มักได้ AUC สูงกว่า

เซลล์นี้ยังบันทึก **Confusion Matrix** เป็น artifact ใน Experiment  
(แถวจริง × คอลัมน์ที่โมเดลทาย — ดูว่าทาย Churn ผิดตรงไหน)"""
            ),
            code_cell(
                r'''from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

rf_model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
if mlflow_ready:
    with mlflow.start_run(run_name="Run_02_RandomForest_Champion"):
        mlflow.autolog(log_models=False)
        rf_model.fit(X_train, y_train)
        metrics = evaluate(rf_model, "Run 2 Random Forest")
        for key, value in metrics.items():
            mlflow.log_metric(key, value)
        cm = confusion_matrix(y_test, rf_model.predict(X_test))
        plt.figure(figsize=(5, 4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                    xticklabels=["Stay (0)", "Churn (1)"], yticklabels=["Stay (0)", "Churn (1)"])
        plt.title("FreshMart Churn Confusion Matrix")
        plt.ylabel("Actual")
        plt.xlabel("Predicted")
        plt.tight_layout()
        plt.savefig("confusion_matrix.png")
        plt.show()
        mlflow.log_artifact("confusion_matrix.png")
        signature = infer_signature(X_train, rf_model.predict(X_train))
        mlflow.sklearn.log_model(rf_model, "model", signature=signature)
else:
    rf_model.fit(X_train, y_train)
    evaluate(rf_model, "Run 2 Random Forest")'''
            ),
            md_cell(
                """### ขั้นตอนที่ 5: ลงทะเบียนโมเดลชนะ

**โค้ดนี้ทำอะไร:** เลือก run ที่ AUC สูงสุด แล้ว `register_model` เป็น `freshmart-churn-model`

หลังจากนี้ไป Workspace ควรเห็น item ประเภท **Model**  
Lab 4 จะเรียกโมเดลนี้ด้วยชื่อ + version 1"""
            ),
            code_cell(
                r'''dt_auc = roc_auc_score(y_test, dt_model.predict_proba(X_test)[:, 1])
rf_auc = roc_auc_score(y_test, rf_model.predict_proba(X_test)[:, 1])
if rf_auc <= dt_auc:
    raise AssertionError(
        f"Random Forest (AUC={rf_auc:.4f}) ควรชนะ Decision Tree (AUC={dt_auc:.4f}) — ตรวจลำดับฟีเจอร์/สเกล"
    )
print(f"Champion AUC: {rf_auc:.4f}")

if mlflow_ready:
    exp = mlflow.get_experiment_by_name(experiment_name)
    runs = mlflow.search_runs(exp.experiment_id, order_by=["metrics.test_roc_auc DESC"], max_results=1)
    champion_run_id = runs.iloc[0]["run_id"]
    model_uri = f"runs:/{champion_run_id}/model"
    mv = mlflow.register_model(model_uri, "freshmart-churn-model")
    print(f"Registered {mv.name} version {mv.version}")
else:
    print("Skip registry (local mode). Champion model remains in-memory as rf_model.")
print("Lab 3 verification passed")'''
            ),
        ],
    )

    write_notebook(
        "04-batch-predict.ipynb",
        [
            md_cell(
                """# FreshMart Lab 4: Batch Scoring to Gold
**Microsoft Fabric Data Science**

เป้าหมาย: ทำนายสมาชิกใหม่ 200 คน → ตาราง `gold.freshmart_predictions` พร้อมความเร่งด่วนแคมเปญ

### กฎทอง (ถามบ่อยที่สุด — อ่านก่อนรัน)
**ห้าม** คำนวณ min/max ใหม่จากชุด 200 คน  
**ต้อง** ใช้ `feature_params.json` จาก Lab 2

ถ้า scale ใหม่ → ผลทำนายเพี้ยน / เอียงคลาสเดียว

### ถ้าติด — อ่านก่อนถาม TA
| อาการ | สาเหตุที่พบบ่อย | ทำอะไร |
| --- | --- | --- |
| หาโมเดลไม่เจอ | ยังไม่จบ Lab 3 | กลับไป register `freshmart-churn-model` |
| missing column / type mismatch | ลำดับฟีเจอร์ไม่ตรง | ใช้ params จาก Lab 2 เท่านั้น |
| PREDICT unavailable | สภาพแวดล้อม | เซลล์มี fallback — ดูข้อความใน output |"""
            ),
            md_cell("### เตรียม loader + ฟังก์ชันฟีเจอร์"),
            code_cell("import json\nfrom pathlib import Path\nimport pandas as pd\n\n" + LOADER),
            code_cell(
                "from dataclasses import asdict, dataclass\nfrom typing import Any\nimport logging\n\n"
                "logger = logging.getLogger(__name__)\n\n" + CONSTANTS + "\n\n" + FEATURE_SOURCE
            ),
            md_cell(
                """### ขั้นตอนที่ 1: โหลดชุดทำนาย + params ชุดฝึก

**โค้ดนี้ทำอะไร**
1. อ่าน `Files/raw/freshmart_scoring_batch.csv` (200 แถว **ไม่มี** คอลัมน์ Churn)
2. โหลด `feature_params.json` จาก Lab 2
3. `transform_customers(..., require_target=False)` ให้ได้ 14 ฟีเจอร์ตาม signature

รหัสลูกค้าชุดนี้ขึ้นต้น `CUST_05xxx` ไม่ซ้อนกับชุดฝึก"""
            ),
            code_cell(
                r'''try:
    df_scoring_raw = (
        spark.read.format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .load("Files/raw/freshmart_scoring_batch.csv")
        .toPandas()
    )
    print("Loaded scoring batch from Files/raw")
except Exception as exc:
    print(f"Spark Files path unavailable ({exc})")
    df_scoring_raw = load_csv("freshmart_scoring_batch.csv")

print(f"Scoring Batch count: {len(df_scoring_raw):,}")
assert "Churn" not in df_scoring_raw.columns
display(df_scoring_raw.head())

params_path = _first_existing([
    "Files/params/feature_params.json",
    "/lakehouse/default/Files/params/feature_params.json",
    "labs/data/.local/feature_params.json",
])
if params_path:
    params = load_feature_params(params_path)
    print(f"Loaded feature params from {params_path}")
else:
    print("feature_params.json not found; fitting from bronze.customers")
    params = fit_preprocessor(load_table_or_csv("bronze.customers", "freshmart_customers.csv"))

spark_features = transform_customers(df_scoring_raw, params, require_target=False)
print("Aligned columns:", list(spark_features.columns))
print(spark_features.head())'''
            ),
            md_cell(
                """### ขั้นตอนที่ 2: PREDICT

**ความรู้สั้น ๆ:** `MLFlowTransformer` = ให้ Spark เรียกโมเดลที่ลงทะเบียนไว้ทีละแถว/แบตช์

ส่งเฉพาะคอลัมน์ฟีเจอร์ — **อย่าส่ง** `CustomerID`

ถ้า PREDICT ไม่พร้อม เซลล์จะลอง `mlflow.pyfunc` ต่ออัตโนมัติ"""
            ),
            code_cell(
                r'''predictions = None
try:
    from synapse.ml.predict import MLFlowTransformer
    spark_scoring = spark.createDataFrame(spark_features)
    model_transformer = MLFlowTransformer(
        inputCols=list(params.feature_columns),
        outputCol="Churn_Prediction",
        modelName="freshmart-churn-model",
        modelVersion=1,
    )
    df_predictions = model_transformer.transform(spark_scoring)
    predictions = df_predictions.toPandas()
    print("Scored with MLFlowTransformer / PREDICT")
except Exception as exc:
    print(f"PREDICT unavailable ({exc}). Using local/registry fallback.")
    try:
        import mlflow
        pyfunc_model = mlflow.pyfunc.load_model("models:/freshmart-churn-model/1")
        preds = pyfunc_model.predict(model_matrix(spark_features, params))
        predictions = spark_features.copy()
        predictions["Churn_Prediction"] = preds
        print("Scored with mlflow.pyfunc")
    except Exception as inner:
        print(f"MLflow registry unavailable ({inner}). Retrain local champion for smoke test.")
        from sklearn.ensemble import RandomForestClassifier
        silver = load_table_or_csv("silver.customer_features", ".local/silver_customer_features.csv")
        if "MembershipTier_Bronze" not in silver.columns:
            raw = load_table_or_csv("bronze.customers", "freshmart_customers.csv")
            silver = transform_customers(raw, params, require_target=True)
        model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        model.fit(model_matrix(silver, params), silver["Churn"].astype(int))
        predictions = spark_features.copy()
        predictions["Churn_Prediction"] = model.predict(model_matrix(spark_features, params))

print(predictions[["CustomerID", "RecencyDays", "MonetaryTotal", "ComplaintCount", "Churn_Prediction"]].head(10))'''
            ),
            md_cell(
                """### ขั้นตอนที่ 3: เขียนตาราง Gold + ความเร่งด่วนแคมเปญ

**โค้ดนี้ทำอะไร**
- เพิ่ม `Action_Priority`: `1` → High (ส่ง voucher), `0` → Normal
- เขียน Delta table `gold.freshmart_predictions`

**ต้องเห็น:** 200 แถว และมีทั้งสองกลุ่มความเร่งด่วน  
(ชุดอ้างอิงท้องถิ่น ≈ 36 High / 164 Normal — บน Fabric อาจขยับเล็กน้อย)

จบแล็บเมื่อพิมพ์ `Lab 4 verification passed`"""
            ),
            code_cell(
                r'''from datetime import datetime, timezone

gold = predictions.copy()
gold["Scored_Timestamp"] = datetime.now(timezone.utc).isoformat()
gold["Action_Priority"] = gold["Churn_Prediction"].map({
    1: "High - Send Retention Voucher",
    0: "Normal - Standard Engagement",
})
assert set(gold["Churn_Prediction"].unique()) <= {0, 1}
print(gold["Action_Priority"].value_counts())

try:
    (
        spark.createDataFrame(gold)
        .write.format("delta")
        .mode("overwrite")
        .option("mergeSchema", "true")
        .saveAsTable("gold.freshmart_predictions")
    )
    print("Published gold.freshmart_predictions")
    spark.sql("""
        SELECT Action_Priority, COUNT(*) AS CustomerCount
        FROM gold.freshmart_predictions
        GROUP BY Action_Priority
    """).show()
except Exception as exc:
    out = Path("labs/data/.local/gold_freshmart_predictions.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    gold.to_csv(out, index=False)
    print(f"Spark write unavailable ({exc}). Wrote {out}")

assert len(gold) == 200
print("Lab 4 verification passed")'''
            ),
        ],
    )
    print("All FreshMart notebooks generated")


if __name__ == "__main__":
    build()

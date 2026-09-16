"""Generate self-contained Azure ML Jupyter notebooks for FreshMart labs.

Reuses the same FreshMart feature contract as the Fabric track, but does not
modify any file under labs/. Notebooks run on an Azure ML compute instance
with pandas + MLflow (no Spark, no Lakehouse).
"""

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

NB_DIR = ROOT / "labs-azureml" / "notebooks"


def make_notebook(cells: list[dict]) -> dict:
    """Build a notebook document for Azure ML studio / Jupyter."""
    return {
        "cells": cells,
        "metadata": {
            "language_info": {"name": "python"},
            "kernelspec": {
                "display_name": "Python 3.10 - SDK v2",
                "language": "python",
                "name": "python3",
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

BRONZE_TRANSACTIONS = "bronze/transactions"
BRONZE_CUSTOMERS = "bronze/customers"
SILVER_CUSTOMER_FEATURES = "silver/customer_features"
GOLD_PREDICTIONS = "gold/freshmart_predictions"
ASSET_BRONZE_TRANSACTIONS = "bronze-transactions"
ASSET_BRONZE_CUSTOMERS = "bronze-customers"
ASSET_SCORING_BATCH = "scoring-batch"
ASSET_SILVER_FEATURES = "silver-customer-features"
ASSET_GOLD_PREDICTIONS = "gold-freshmart-predictions"
TABLE_TO_ASSET = {
    BRONZE_TRANSACTIONS: ASSET_BRONZE_TRANSACTIONS,
    BRONZE_CUSTOMERS: ASSET_BRONZE_CUSTOMERS,
    SILVER_CUSTOMER_FEATURES: ASSET_SILVER_FEATURES,
    GOLD_PREDICTIONS: ASSET_GOLD_PREDICTIONS,
}
CSV_TO_ASSET = {
    "freshmart_transactions.csv": ASSET_BRONZE_TRANSACTIONS,
    "freshmart_customers.csv": ASSET_BRONZE_CUSTOMERS,
    "freshmart_scoring_batch.csv": ASSET_SCORING_BATCH,
}
RAW_FILES = (
    "freshmart_transactions.csv",
    "freshmart_customers.csv",
    "freshmart_scoring_batch.csv",
)


def _first_existing(paths):
    for path in paths:
        candidate = Path(path)
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _writable_dir(path: Path) -> Path | None:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return path.resolve()
    except OSError:
        return None


def resolve_raw_csv(file_name: str) -> Path:
    found = _first_existing([
        Path("data") / "raw" / file_name,
        Path("data") / file_name,
        Path("../data") / "raw" / file_name,
        Path("../data") / file_name,
        Path("../../labs/data") / file_name,
        Path("../labs/data") / file_name,
        Path("labs/data") / file_name,
        Path(file_name),
    ])
    if found is None:
        raise FileNotFoundError(
            f"Cannot find {file_name}. Upload it to data/raw/ next to the notebook "
            "or clone this repo so labs/data/ is available."
        )
    return found


def load_csv(file_name: str) -> pd.DataFrame:
    asset_name = CSV_TO_ASSET.get(file_name)
    if asset_name:
        frame = load_data_asset(asset_name)
        if frame is not None:
            return frame
    found = resolve_raw_csv(file_name)
    print(f"Loaded CSV: {found}")
    return pd.read_csv(found)


def load_data_asset(asset_name: str):
    """Load a registered Azure ML data asset, or return None."""
    try:
        from azure.ai.ml import MLClient
        from azure.identity import DefaultAzureCredential

        ml_client = MLClient.from_config(credential=DefaultAzureCredential())
        asset = ml_client.data.get(name=asset_name, label="latest")
        path = asset.path
        print(f"Loaded data asset {asset_name} v{asset.version}: {path}")
        if str(path).lower().endswith(".parquet"):
            return pd.read_parquet(path)
        return pd.read_csv(path)
    except Exception as exc:
        print(f"Data asset '{asset_name}' unavailable ({exc})")
        return None


def register_data_asset(name: str, path, description: str = "") -> bool:
    """Register a file as an Azure ML data asset. Returns True when saved."""
    try:
        from azure.ai.ml import MLClient
        from azure.ai.ml.entities import Data
        from azure.ai.ml.constants import AssetTypes
        from azure.identity import DefaultAzureCredential

        ml_client = MLClient.from_config(credential=DefaultAzureCredential())
        asset = Data(
            name=name,
            path=str(path),
            type=AssetTypes.URI_FILE,
            description=description or f"FreshMart {name}",
        )
        created = ml_client.data.create_or_update(asset)
        print(f"Registered data asset {created.name} v{created.version}")
        return True
    except Exception as exc:
        print(f"Could not register data asset '{name}' ({exc})")
        return False


def resolve_artifact_root() -> Path:
    for candidate in (
        Path("data"),
        Path("../data"),
        Path("labs-azureml/data"),
    ):
        ready = _writable_dir(candidate)
        if ready is not None:
            return ready
    fallback = Path("data")
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback.resolve()


ARTIFACT_ROOT = resolve_artifact_root()


def layer_path(layer: str, stem: str, suffix: str = ".parquet") -> Path:
    folder = ARTIFACT_ROOT / layer
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{stem}{suffix}"


def load_table_or_csv(table_name: str, file_name: str) -> pd.DataFrame:
    asset_name = TABLE_TO_ASSET.get(table_name)
    if asset_name:
        frame = load_data_asset(asset_name)
        if frame is not None:
            return frame
    layer, _, stem = table_name.partition("/")
    parquet = layer_path(layer, stem)
    if parquet.exists():
        frame = pd.read_parquet(parquet)
        print(f"Loaded parquet {parquet}: {len(frame):,} rows")
        return frame
    csv_fallback = ARTIFACT_ROOT / layer / f"{stem}.csv"
    if csv_fallback.exists():
        frame = pd.read_csv(csv_fallback)
        print(f"Loaded CSV artifact {csv_fallback}: {len(frame):,} rows")
        return frame
    print(f"Layer file '{table_name}' not found. Falling back to published CSV.")
    return load_csv(file_name)


def save_layer(frame: pd.DataFrame, table_name: str) -> Path:
    layer, _, stem = table_name.partition("/")
    parquet = layer_path(layer, stem)
    try:
        frame.to_parquet(parquet, index=False)
        print(f"Wrote {parquet} ({len(frame):,} rows)")
        return parquet
    except Exception as exc:
        csv_path = layer_path(layer, stem, suffix=".csv")
        frame.to_csv(csv_path, index=False)
        print(f"Parquet unavailable ({exc}). Wrote {csv_path}")
        return csv_path
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

# PEP 563: postpone annotation evaluation so `-> FeatureParams` inside the
# class body does not raise NameError when this snippet is pasted into a cell.
FEATURE_CONTRACT_CELL = (
    "from __future__ import annotations\n\n"
    "from dataclasses import asdict, dataclass\n"
    "from typing import Any\n"
    "import logging\n\n"
    "logger = logging.getLogger(__name__)\n\n"
    + CONSTANTS
    + "\n\n"
    + FEATURE_SOURCE
)


def write_notebook(name: str, cells: list[dict]) -> None:
    """Serialize a notebook to labs-azureml/notebooks."""
    NB_DIR.mkdir(parents=True, exist_ok=True)
    path = NB_DIR / name
    path.write_text(json.dumps(make_notebook(cells), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {path}")


def build() -> None:
    """Generate all published FreshMart Azure ML notebooks."""
    write_notebook(
        "00-environment-verification.ipynb",
        [
            md_cell(
                """# FreshMart Lab 0: Environment Verification
**Azure Machine Learning (ทางเลือกฉุกเฉินแทน Fabric)**

เป้าหมาย: ยืนยันว่าพร้อมเข้า Lab 1 — **ไม่ต้องวิเคราะห์ธุรกิจในแล็บนี้**

แทร็กนี้ใช้เมื่อ **Fabric Capacity ใช้ไม่ได้** วงจรธุรกิจ FreshMart เหมือนชุด Fabric แต่รันบน Azure ML Compute Instance ด้วย pandas + MLflow

### ก่อนรัน (เช็ก 30 วินาที)
1. Workspace Azure ML เป็นของคลาสหรือของตนเอง — ทำงานในโฟลเดอร์ `Users/<ชื่อคุณ>/freshmart/`
2. Compute instance สถานะ **Running** และเคอร์เนลเป็น **Python 3.10 - SDK v2**
3. มีไฟล์ CSV สามไฟล์จาก `labs/data/` (clone repo หรืออัปโหลดไป `data/raw/`)
4. **อย่ารันหลายเซลล์ซ้อน** จนกว่าเซลล์ก่อนหน้าจะจบ

### ศัพท์ที่ใช้ในแล็บนี้
Workspace ของ Azure ML คือศูนย์กลางทดลองโมเดล จัดเก็บ Data asset, Experiment และ Model  
ชั้น Medallion ในแทร็กนี้คือ**โฟลเดอร์** `data/bronze` / `data/silver` / `data/gold` ไม่ใช่ schema ของ Lakehouse

### ถ้าติด — อ่านก่อนถาม TA
| อาการ | ทำอะไร |
| --- | --- |
| ไม่เจอไฟล์ CSV | อัปโหลดสามไฟล์จาก `labs/data/` ไป `data/raw/` หรือ `git clone` repo นี้บน compute instance |
| Kernel Starting ค้าง | รอ compute เป็น Running แล้วเลือกเคอร์เนลใหม่ |
| `PermissionError` ตอนเขียนไฟล์ | ตรวจว่าทำงานในโฟลเดอร์ของตนเอง ไม่ใช่ Samples ที่อ่านอย่างเดียว |
| AssertionError จำนวนแถว | ไม่ผ่าน Lab 0 — อย่าข้ามไป Lab 1 |"""
            ),
            md_cell(
                """### เซลล์ถัดไป: ฟังก์ชันโหลดข้อมูล

โค้ดด้านล่างนิยาม `load_table_or_csv` และ `save_layer` ให้แล้ว — **รันครั้งเดียวแล้วใช้ต่อทุก Lab**

- อ่าน parquet ใน `data/bronze` ก่อน ถ้ายังไม่มีค่อยอ่าน CSV จาก `data/raw/` หรือ `labs/data/`
- เขียนชั้น Medallion เป็นไฟล์ในโฟลเดอร์ `data/` ของ workspace
- ไม่ต้องแก้โค้ดนี้"""
            ),
            code_cell(LOADER),
            md_cell(
                """### ตรวจแพ็กเกจที่ต้องใช้

**โค้ดนี้ทำอะไร:** ตรวจว่า pandas / scikit-learn / matplotlib พร้อมบน compute instance

ถ้าขาด เซลล์จะติดตั้งให้แบบเงียบ — รอบแรกอาจใช้เวลา 1–2 นาที"""
            ),
            code_cell(
                """import importlib.util

required = ["pandas", "sklearn", "matplotlib", "seaborn", "mlflow", "pyarrow", "azure.ai.ml"]
missing = [name for name in required if importlib.util.find_spec(name) is None]
if missing:
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pandas", "scikit-learn", "matplotlib", "seaborn", "mlflow", "pyarrow", "azure-ai-ml", "azureml-fsspec"])
    print("Installed:", ", ".join(missing))
else:
    print("Python packages ready:", ", ".join(required))"""
            ),
            md_cell(
                """### สร้างชั้น Bronze จากไฟล์ข้อมูลต้นทาง (CSV)

**โค้ดนี้ทำอะไร:** คัดลอกธุรกรรมและสมาชิกจาก CSV ไปเป็นไฟล์ parquet ใน `data/bronze/`

รันครั้งเดียวหลังมีไฟล์ CSV — รันซ้ำได้ (เขียนทับชุดเดิม)

**สิ่งที่ควรเห็น**
- `bronze/transactions` ประมาณ **3,000** แถว
- `bronze/customers` ประมาณ **1,500** แถว
- ข้อความ `Bronze layers ready`"""
            ),
            code_cell(
                """required = [
    "freshmart_transactions.csv",
    "freshmart_customers.csv",
    "freshmart_scoring_batch.csv",
]
missing = []
for name in required:
    asset_name = CSV_TO_ASSET.get(name)
    if asset_name and load_data_asset(asset_name) is not None:
        continue
    try:
        resolve_raw_csv(name)
    except FileNotFoundError:
        missing.append(name)
if missing:
    raise FileNotFoundError(
        "ไม่พบไฟล์หรือ Data asset: "
        + ", ".join(missing)
        + " — สร้าง Data asset จากหน้า Data หรืออัปโหลดจาก labs/data/"
    )

df_tx = load_csv("freshmart_transactions.csv")
df_cust = load_csv("freshmart_customers.csv")
tx_path = save_layer(df_tx, BRONZE_TRANSACTIONS)
cust_path = save_layer(df_cust, BRONZE_CUSTOMERS)
print("bronze/transactions:", len(df_tx))
print("bronze/customers:", len(df_cust))
print("Artifact root:", ARTIFACT_ROOT)
print("Bronze layers ready")"""
            ),
            md_cell(
                """### โหลด Bronze แล้วดูตัวอย่างแถว

**โค้ดนี้ทำอะไร:** อ่านชั้น Bronze แล้วพิมพ์จำนวนแถวและ 5 แถวแรก

**สิ่งที่ควรเห็น**
- Transactions ประมาณ **3,000** แถว
- Customers ประมาณ **1,500** แถว"""
            ),
            code_cell(
                """df_tx = load_table_or_csv(BRONZE_TRANSACTIONS, "freshmart_transactions.csv")
df_cust = load_table_or_csv(BRONZE_CUSTOMERS, "freshmart_customers.csv")

print(f"Transactions rows: {len(df_tx):,}")
print(f"Customers rows: {len(df_cust):,}")
print("Transaction columns:", list(df_tx.columns))
print("Customer columns:", list(df_cust.columns))
display(df_tx.head(5))
display(df_cust.head(5))"""
            ),
            md_cell(
                """### ลงทะเบียน Data asset ใน Azure ML

**โค้ดนี้ทำอะไร:** ลงทะเบียนชั้น Bronze และชุดทำนายเป็น Data asset ใน workspace  
ถ้าคุณสร้างจากหน้า **Data** ใน studio แล้ว เซลล์นี้จะเพิ่มเวอร์ชันใหม่

**สิ่งที่ควรเห็น:** เมนู **Data** มี `bronze-transactions`, `bronze-customers`, `scoring-batch`"""
            ),
            code_cell(
                """register_data_asset(ASSET_BRONZE_TRANSACTIONS, tx_path, "FreshMart bronze transactions")
register_data_asset(ASSET_BRONZE_CUSTOMERS, cust_path, "FreshMart bronze customers")
try:
    scoring_path = resolve_raw_csv("freshmart_scoring_batch.csv")
    register_data_asset(ASSET_SCORING_BATCH, scoring_path, "FreshMart unlabeled scoring batch")
except FileNotFoundError:
    print("Create scoring-batch from the Data page if the CSV is not on this compute.")"""
            ),
            md_cell(
                """### จุดตรวจอัตโนมัติ

**โค้ดนี้ทำอะไร:** ถ้าจำนวนแถวไม่ตรง จะ `raise AssertionError` และหยุด

- ผ่านแล้วจะพิมพ์ `Lab 0 verification passed`
- ไม่ผ่าน แปลว่าสภาพแวดล้อมยังไม่พร้อม — **ถาม TA พร้อมคัดลอกข้อความ error ทั้งบรรทัด**"""
            ),
            code_cell(
                """if len(df_tx) != 3000:
    raise AssertionError(
        f"คาดว่าธุรกรรม 3,000 แถว แต่ได้ {len(df_tx):,} — ตรวจ data/raw หรือ labs/data"
    )
if len(df_cust) != 1500:
    raise AssertionError(
        f"คาดว่าสมาชิก 1,500 แถว แต่ได้ {len(df_cust):,} — ตรวจ data/raw หรือ labs/data"
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
**Azure Machine Learning (ทางเลือกฉุกเฉินแทน Fabric)**

การสำรวจข้อมูลเบื้องต้น (Exploratory Data Analysis) — ดูสถิติ กราฟ และค่าว่าง **ก่อน** สร้างโมเดล

บทบาท: **นักวิเคราะห์ข้อมูล** — สำรวจข้อมูลก่อนสร้างโมเดล  
จด **3 ข้อสังเกตสั้น ๆ** ส่ง Lab 2 (ไม่ต้องจำสูตรสถิติ)

### สิ่งที่แล็บนี้ตอบ
1. ข้อมูลขาดตรงไหน?
2. ของเสียสูงที่ประเภทสาขาไหน?
3. คนที่ Churn (เลิกซื้อ) พฤติกรรมต่างจากคนอยู่ต่ออย่างไร?

### ถ้าติด — อ่านก่อนถาม TA
| อาการ | ความหมาย |
| --- | --- |
| กราฟไม่ขึ้น | รอเซลล์ก่อนหน้าจบ แล้วรันใหม่ |
| ค่าสหสัมพันธ์ไม่ตรงทศนิยมทุกตัว | ปัด 2 ตำแหน่งใกล้เคียงพอ |
| ไม่เจอชั้น Bronze | กลับไป Lab 0 |"""
            ),
            md_cell(
                """### เตรียมตัวโหลดข้อมูล

รันเซลล์ถัดไปเพื่อนิยาม `load_table_or_csv` — **อย่าข้าม**"""
            ),
            code_cell(LOADER),
            md_cell(
                """### ขั้นตอนที่ 1: โหลดธุรกรรม

**โค้ดนี้ทำอะไร:** อ่าน `bronze/transactions` แล้วใช้ Pandas

- `shape` แสดง `(จำนวนแถว, จำนวนคอลัมน์)` — เมื่อถูกต้องควรได้ประมาณ `(3000, 14)`
- `head()` แสดง 5 แถวแรก เพื่อรู้จักคอลัมน์ เช่น `WasteUnits` (ของเสีย) และ `StoreType`"""
            ),
            code_cell(
                """df = load_table_or_csv(BRONZE_TRANSACTIONS, "freshmart_transactions.csv")
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

Hypermarket กับ Supermarket กล่องมักแบนใกล้ 0 เพราะวันส่วนใหญ่ไม่มีของเสีย — นั่นคือลักษณะข้อมูล ไม่ใช่กราฟพัง

ไม่ต้องได้ตัวเลขเป๊ะทุกทศนิยม — เห็นแนวโน้มถูกทางพอ"""
            ),
            code_cell(
                """plt.figure(figsize=(10, 5))
ax = sns.boxplot(data=df, x="StoreType", y="WasteUnits", hue="StoreType", palette="Set2", dodge=False)
legend = ax.get_legend()
if legend is not None:
    legend.remove()
plt.title("Waste Units by Store Type")
plt.show()"""
            ),
            md_cell(
                """### ขั้นตอนที่ 5: Correlation

**ความรู้จำเป็น**
- ค่าใกล้ **+1** = ไปด้วยกัน, ใกล้ **-1** = สวนทาง, ใกล้ **0** = เกือบไม่เกี่ยว
- Heatmap คือตารางสหสัมพันธ์แบบสี

**ค่าอ้างอิงชุดนี้ (ปัด 2 ตำแหน่ง)**
- DiscountRate กับ UnitsSold ประมาณ **+0.38** (ลดราคาแล้วขายดีขึ้น)
- DiscountRate กับ WasteUnits ประมาณ **-0.12** (ลดราคามักเหลือทิ้งน้อยลง)"""
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
- `Churn = 1` หมายถึงมีแนวโน้มยกเลิกหรือเลิกซื้อ, `0` หมายถึงอยู่ต่อ
- อัตรา Churn ชุดนี้อยู่ที่ประมาณ **19.3%** (290 จาก 1,500)
- `Age` ว่าง **37** แถว — Lab 2 จะเติมด้วยค่ามัธยฐาน (median)

Scatter ด้านล่าง: คนขาดซื้อนาน (`RecencyDays` สูง) และร้องเรียนบ่อย มักกระจุกที่ Churn=1"""
            ),
            code_cell(
                """df_cust = load_table_or_csv(BRONZE_CUSTOMERS, "freshmart_customers.csv")
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
ก่อนไป Lab 2 จด 3 ข้อ: **เติม Age · แปลงหมวดหมู่ · ปรับสเกลเงินและความถี่**"""
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
                """# FreshMart Lab 2: Feature Engineering
**Azure Machine Learning (ทางเลือกฉุกเฉินแทน Fabric)**

เป้าหมาย: (A) ฝึกแปลงข้อมูลแบบเห็นผล  (B) เตรียมฟีเจอร์สมาชิกให้ Lab 3–4

บน Azure ML Studio notebook **ไม่มี Data Wrangler ของ Fabric**  
ส่วน A จึงใช้ pandas ให้เห็นผลเดียวกัน — ถ้าเปิด notebook ใน VS Code จะใช้ส่วนขยาย Data Wrangler แทนได้

### กฎทองที่ต้องจำ (ลดคำถาม Lab 4 ครึ่งหนึ่ง)
โมเดลเรียนรู้จาก **min/max ของชุดฝึก 1,500 คน**  
Lab 4 ทำนายชุดใหม่ 200 คน — **ห้ามคำนวณสเกลใหม่** ต้องใช้ `feature_params.json` จากแล็บนี้

### ถ้าติด — อ่านก่อนถาม TA
| อาการ | ทำอะไร |
| --- | --- |
| หา Data Wrangler ใน Studio ไม่เจอ | ปกติของแทร็กนี้ — ใช้เซลล์ pandas ในส่วน A |
| Export จาก VS Code แล้วสับสน | ส่วน A เป็นการฝึกแปลงข้อมูล — **ส่วน B ต้องรันเซลล์ที่เตรียมให้** เพื่อส่งงาน |"""
            ),
            md_cell(
                """### เตรียมฟังก์ชันโหลด

รันเซลล์ถัดไปก่อนเสมอ"""
            ),
            code_cell("import json\nfrom pathlib import Path\nimport pandas as pd\n\n" + LOADER),
            md_cell(
                """### ส่วน A — โหลดธุรกรรมสำหรับฝึกแปลงข้อมูล

**โค้ดนี้ทำอะไร:** โหลดธุรกรรมแล้วสุ่ม **500 แถว** ให้ทดลองกรองและรวมยอดได้เร็ว

ตัวแปรสำคัญ: **`df`**"""
            ),
            code_cell(
                """df = load_table_or_csv(
    BRONZE_TRANSACTIONS,
    "freshmart_transactions.csv",
)
df = df.sample(n=500, random_state=1).reset_index(drop=True)
print("Sample for Data Wrangler:", df.shape)
df.head(4)"""
            ),
            md_cell(
                """### ส่วน A — จัดข้อความ กรอง และรวมยอด (เทียบเท่า Data Wrangler)

ทำตามทีละข้อในเซลล์ด้านล่าง หรือเปิด VS Code แล้วใช้ Data Wrangler กับ `df` แล้ววางโค้ดแทน

1. จัดรูปแบบ `Category` ให้ขึ้นต้นด้วยตัวพิมพ์ใหญ่
2. กรอง `StoreType = Express` แล้วเรียง `WasteCost` จากมากไปน้อย
3. รวมยอดเฉลี่ย `WasteCost` ตาม `Category`"""
            ),
            code_cell(
                """df_formatted = df.copy()
df_formatted["Category"] = df_formatted["Category"].astype(str).str.title()

express = (
    df_formatted[df_formatted["StoreType"] == "Express"]
    .sort_values("WasteCost", ascending=False)
)
print("Top Express waste rows:")
display(express.head(5))


def summarize_waste(frame: pd.DataFrame) -> pd.DataFrame:
    \"\"\"เทียบเท่า Group by จาก Data Wrangler — ปรับได้ถ้าคุณ export โค้ดจาก VS Code\"\"\"
    return frame.groupby(["Category"]).agg(WasteCost_mean=("WasteCost", "mean")).reset_index()


print(summarize_waste(df_formatted))"""
            ),
            md_cell(
                """### ส่วน B — โหลดสมาชิกสำหรับโมเดล

**ทำไมแยกจากส่วน A:** ส่วน A ฝึกกับธุรกรรม ส่วนโมเดลทำนาย Churn ใช้ตารางสมาชิก

**สิ่งที่ควรเห็น:** shape ประมาณ `(1500, 11)` และ Age ว่าง **37** แถว

**ส่งงาน Lab 3–4 ต้องรันเซลล์สัญญาฟีเจอร์ด้านล่างเท่านั้น**"""
            ),
            code_cell(
                """df_cust = load_table_or_csv(BRONZE_CUSTOMERS, "freshmart_customers.csv")
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
| Min-max scale | ปรับเงินและความถี่ให้อยู่ช่วงประมาณ 0–1 จาก**ชุดฝึก** |

**รันเซลล์ฟังก์ชันก่อน** แล้วค่อยรันเซลล์ `fit` / `transform`"""
            ),
            code_cell(FEATURE_CONTRACT_CELL),
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
- เขียน `data/params/feature_params.json` (Lab 4 ต้องใช้ไฟล์นี้)
- เขียน `data/silver/customer_features.parquet`

**สิ่งที่ควรเห็น:** เซลล์พิมพ์เส้นทางไฟล์ที่บันทึก และ `Lab 2 verification passed`"""
            ),
            code_cell(
                r'''params_dir = ARTIFACT_ROOT / "params"
params_dir.mkdir(parents=True, exist_ok=True)
params_path = params_dir / "feature_params.json"
save_feature_params(params, params_path)
print(f"Saved {params_path}")

silver_path = save_layer(df_clean, SILVER_CUSTOMER_FEATURES)
silver_csv = layer_path("silver", "customer_features", suffix=".csv")
df_clean.to_csv(silver_csv, index=False)
print(f"Saved silver features: {silver_path}")
print(f"Saved AutoML tabular CSV: {silver_csv}")
register_data_asset(ASSET_SILVER_FEATURES, silver_csv, "FreshMart silver customer features for AutoML")'''
            ),
            md_cell(
                """### จุดตรวจ Lab 2

ผ่านแล้วพิมพ์ `Lab 2 verification passed`  
ในโฟลเดอร์ Files ควรเห็น `data/silver/customer_features.parquet`"""
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
                """# FreshMart งานเสริม: Train and Track Models with MLflow
**Azure Machine Learning (ทางเลือกฉุกเฉินแทน Fabric)**

งานนี้เป็น**ทางเลือก** หลังแบบฝึกหัด 3 (Automated ML)  
เป้าหมาย: ฝึกโมเดล 2 ตัวด้วยมือ แล้วลงทะเบียนเป็น `freshmart-churn-manual` — **ห้ามทับ** Champion `freshmart-churn-model`

### ศัพท์ที่ใช้ในแล็บนี้
Experiment คือสมุดรวมผลการทดลองใน Workspace; Run (ใน Azure ML เรียก Job เมื่อส่งเป็นจ็อบ) คือหนึ่งครั้งที่ฝึกโมเดล  
AUC คือคะแนนแยกคนมีแนวโน้ม Churn กับคนที่อยู่ต่อ (ใกล้ 1 ดีกว่า; ประมาณ 0.5 ใกล้เดาสุ่ม)  
ลายเซ็นโมเดล (signature) คือรายชื่อคอลัมน์ที่โมเดลคาดหวัง — ต้องตรง Lab 2

### ค่าอ้างอิงชุดนี้ (seed 42)
- Decision Tree (โมเดลเส้นฐาน) AUC ประมาณ **0.77**
- Random Forest (โมเดลที่เลือกใช้) AUC ประมาณ **0.86** (ควรชนะ)

### ถ้าติด — อ่านก่อนถาม TA
| อาการ | ทำอะไร |
| --- | --- |
| หา Experiment ไม่เจอ | ซ้ายมือเปิด **Jobs** หรือ **Experiments** แล้ว Refresh |
| Random Forest แพ้ Decision Tree | ตรวจว่า Lab 2 บันทึก Silver และ params ครบ |
| MLflow ชี้ไปเครื่องท้องถิ่น | รันบน compute instance ของ Azure ML ไม่ใช่เคอร์เนลเครื่องคุณ |"""
            ),
            md_cell("### เตรียม loader + ฟังก์ชันฟีเจอร์ (รันตามลำดับ)"),
            code_cell("import json\nfrom pathlib import Path\nimport pandas as pd\n\n" + LOADER),
            code_cell(FEATURE_CONTRACT_CELL),
            md_cell(
                """### ขั้นตอนที่ 1: โหลด Silver แล้วแยก Train/Test

**โค้ดนี้ทำอะไร**
1. โหลด `silver/customer_features` (จาก Lab 2)
2. แยก `X` = ฟีเจอร์, `y` = Churn
3. แบ่ง Train 80% / Test 20% แบบ `stratify=y` ให้สัดส่วน Churn ในทั้งสองชุดใกล้เคียงกัน

**สิ่งที่ควรเห็น:** Train 1,200 แถว · Test 300 แถว · ฟีเจอร์ 14 คอลัมน์  
อย่าใส่ `CustomerID` หรือ `Churn` ใน X"""
            ),
            code_cell(
                r'''df_features = load_table_or_csv(SILVER_CUSTOMER_FEATURES, "freshmart_customers.csv")
if "MembershipTier_Bronze" not in df_features.columns:
    raw = load_table_or_csv(BRONZE_CUSTOMERS, "freshmart_customers.csv")
    params = fit_preprocessor(raw)
    df_features = transform_customers(raw, params, require_target=True)
else:
    params_path = _first_existing([
        ARTIFACT_ROOT / "params" / "feature_params.json",
        Path("data/params/feature_params.json"),
        Path("../data/params/feature_params.json"),
    ])
    if params_path:
        params = load_feature_params(params_path)
    else:
        raw = load_table_or_csv(BRONZE_CUSTOMERS, "freshmart_customers.csv")
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
บน compute instance ของ Azure ML การติดตามจะไปที่ workspace อัตโนมัติ — ไปเปิดที่ **Jobs** หลังฝึกโมเดล"""
            ),
            code_cell(
                r'''mlflow_ready = True
try:
    import mlflow
    import mlflow.sklearn
    from mlflow.models.signature import infer_signature
    experiment_name = "freshmart-churn-manual"
    mlflow.set_experiment(experiment_name)
    print(f"MLflow Experiment set to: '{experiment_name}'")
    print("Tracking URI:", mlflow.get_tracking_uri())
except Exception as exc:
    mlflow_ready = False
    infer_signature = None
    print(f"MLflow unavailable ({exc}). Training will still run locally.")'''
            ),
            md_cell(
                """### ขั้นตอนที่ 3: โมเดลเส้นฐาน — Decision Tree

**ความรู้สั้น ๆ:** Decision Tree คือต้นไม้ตัดสินใจ อ่านง่าย แต่โดยทั่วไปแม่นน้อยกว่าโมเดลรวมต้นไม้หลายต้น

**โค้ดนี้ทำอะไร:** ฝึก `DecisionTreeClassifier` แล้วบันทึกเมตริกและโมเดลลง MLflow"""
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
                """### ขั้นตอนที่ 4: โมเดลที่เลือกใช้ — Random Forest

**ความรู้สั้น ๆ:** Random Forest รวม Decision Tree หลายต้น ช่วยลด overfitting และมักได้ AUC สูงกว่า

เซลล์นี้ยังบันทึก **Confusion Matrix** เป็น artifact ใน Experiment  
(แถวคือค่าจริง คอลัมน์คือที่โมเดลทาย — ใช้ดูว่าทาย Churn ผิดตรงไหน)"""
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
                """### ขั้นตอนที่ 5: ลงทะเบียนโมเดลที่ชนะ

**โค้ดนี้ทำอะไร:** เลือก run ที่ AUC สูงสุด แล้ว `register_model` เป็น `freshmart-churn-manual`

แบบฝึกหัด 4 ยังใช้ `freshmart-churn-model` จาก Automated ML"""
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
    mv = mlflow.register_model(model_uri, "freshmart-churn-manual")
    print(f"Registered {mv.name} version {mv.version}")
else:
    print("Skip registry (local mode). Champion model remains in-memory as rf_model.")
print("Lab 3 verification passed")'''
            ),
        ],
    )

    write_notebook(
        "03-automl-classification.ipynb",
        [
            md_cell(
                """# FreshMart Lab 3: Find the best classification model with Automated ML
**Azure Machine Learning (ทางเลือกฉุกเฉินแทน Fabric)**

เส้นหลักของแทร็กนี้: หาโมเดลจำแนก `Churn` ด้วย Automated ML  
ตัวช่วย studio เป็นทางที่แนะนำในห้องเรียน — โน้ตบุ๊กนี้เป็นทาง SDK และทางสำรองเมื่อตัวช่วยใช้ไม่ได้

อ้างอิง Learn: [Find the best classification model with Automated Machine Learning](https://learn.microsoft.com/training/modules/find-best-classification-model-automated-machine-learning/)

### ก่อนรัน
1. ทำแบบฝึกหัด 2 จบแล้ว มี `data/silver/customer_features.csv`
2. รันบน compute instance ของ Azure ML
3. **อย่า Deploy** เป็น endpoint

### ถ้าติด — อ่านก่อนถาม TA
| อาการ | ทำอะไร |
| --- | --- |
| ส่งจ็อบ SDK ไม่ได้ | ใช้เซลล์ทางสำรอง FLAML |
| หาโมเดลไม่เจอ | ตรวจว่าลงทะเบียนชื่อ `freshmart-churn-model` |"""
            ),
            md_cell("### เตรียม loader + ฟังก์ชันฟีเจอร์"),
            code_cell("import json\nfrom pathlib import Path\nimport pandas as pd\n\n" + LOADER),
            code_cell(FEATURE_CONTRACT_CELL),
            md_cell(
                """### ขั้นตอนที่ 1: โหลด Silver สำหรับ AutoML

**สิ่งที่ควรเห็น:** 1,500 แถว และมีคอลัมน์ `Churn`  
อย่าใส่ `CustomerID` ลงในเมทริกซ์ฝึก"""
            ),
            code_cell(
                r'''df_features = load_table_or_csv(SILVER_CUSTOMER_FEATURES, "freshmart_customers.csv")
if "MembershipTier_Bronze" not in df_features.columns:
    raw = load_table_or_csv(BRONZE_CUSTOMERS, "freshmart_customers.csv")
    params = fit_preprocessor(raw)
    df_features = transform_customers(raw, params, require_target=True)
else:
    params_path = _first_existing([
        ARTIFACT_ROOT / "params" / "feature_params.json",
        Path("data/params/feature_params.json"),
        Path("../data/params/feature_params.json"),
    ])
    params = load_feature_params(params_path) if params_path else fit_preprocessor(
        load_table_or_csv(BRONZE_CUSTOMERS, "freshmart_customers.csv")
    )

X = model_matrix(df_features, params)
y = df_features["Churn"].astype(int)
print(f"Features ({len(X.columns)}):", list(X.columns))
print(f"Rows: {len(X):,}")
assert "CustomerID" not in X.columns
assert len(X) == 1500'''
            ),
            md_cell(
                """### ขั้นตอนที่ 2 (ทางเลือก): ส่งงาน AutoML ด้วย SDK v2

ใช้เมื่อต้องการจ็อบบน Azure ML แบบเดียวกับโมดูล Learn  
ถ้าเซลล์นี้ส่งงานไม่ได้ ให้ข้ามไปทางสำรอง FLAML

ค่าจำกัดงบ: `max_trials=5`, `timeout_minutes=20`, เมตริก `AUC_weighted`"""
            ),
            code_cell(
                r'''automl_job_submitted = False
try:
    from azure.ai.ml import MLClient, automl, Input
    from azure.ai.ml.constants import AssetTypes
    from azure.identity import DefaultAzureCredential

    ml_client = MLClient.from_config(credential=DefaultAzureCredential())
    silver_csv = layer_path("silver", "customer_features", suffix=".csv")
    if not silver_csv.exists():
        df_features.to_csv(silver_csv, index=False)

    training_data = Input(type=AssetTypes.URI_FILE, path=str(silver_csv))
    compute_name = None
    for compute in ml_client.compute.list():
        if getattr(compute, "type", "") in {"computeinstance", "ComputeInstance", "amlcompute"}:
            compute_name = compute.name
            break

    classification_job = automl.classification(
        compute=compute_name,
        experiment_name="freshmart-churn-prediction",
        training_data=training_data,
        target_column_name="Churn",
        primary_metric="AUC_weighted",
        n_cross_validations=3,
        enable_model_explainability=False,
        tags={"lab": "freshmart-automl"},
    )
    classification_job.set_limits(
        timeout_minutes=20,
        trial_timeout_minutes=5,
        max_trials=5,
        enable_early_termination=True,
    )
    returned_job = ml_client.jobs.create_or_update(classification_job)
    automl_job_submitted = True
    print("Submitted AutoML job:", returned_job.name)
    print("Monitor at:", getattr(returned_job, "studio_url", "Jobs in Azure ML studio"))
except Exception as exc:
    print(f"SDK AutoML job not submitted ({exc}). Use the studio wizard or the FLAML fallback next.")'''
            ),
            md_cell(
                """### ขั้นตอนที่ 3: ทางสำรอง FLAML (เมื่อตัวช่วยหรือ SDK ใช้ไม่ได้)

งบเวลา 60 วินาที — ได้ Champion ท้องถิ่นเพื่อไปแบบฝึกหัด 4 ได้เมื่อ registry ยังว่าง"""
            ),
            code_cell(
                r'''from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

champion_auc = None
try:
    from flaml import AutoML
    import mlflow
    import mlflow.sklearn
    from mlflow.models.signature import infer_signature

    mlflow.set_experiment("freshmart-churn-prediction")
    automl = AutoML()
    settings = {
        "time_budget": 60,
        "metric": "roc_auc",
        "task": "classification",
        "seed": 42,
        "force_cancel": True,
    }
    with mlflow.start_run(run_name="flaml-automl-fallback") as run:
        automl.fit(X_train, y_train, **settings)
        champion_auc = float(1 - automl.best_loss)
        signature = infer_signature(X_train, automl.predict(X_train))
        mlflow.sklearn.log_model(automl, "model", signature=signature)
        mlflow.log_metric("test_roc_auc", roc_auc_score(y_test, automl.predict_proba(X_test)[:, 1]))
        print("Best config:", automl.best_config)
        print("Best validation AUC:", champion_auc)
        mv = mlflow.register_model(f"runs:/{run.info.run_id}/model", "freshmart-churn-model")
        print(f"Registered {mv.name} version {mv.version}")
except Exception as exc:
    print(f"FLAML/MLflow path unavailable ({exc}). Training a local Random Forest so verification can pass.")
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X_train, y_train)
    champion_auc = float(roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]))
    print(f"Local fallback AUC: {champion_auc:.4f}")

if champion_auc is None or champion_auc < 0.70:
    raise AssertionError("Champion AUC ควรสูงกว่า 0.70 สำหรับชุด FreshMart")
print("Lab 3 verification passed")'''
            ),
        ],
    )

    write_notebook(
        "04-batch-predict.ipynb",
        [
            md_cell(
                """# FreshMart Lab 4: Batch Scoring to Gold
**Azure Machine Learning (ทางเลือกฉุกเฉินแทน Fabric)**

การทำนายเป็นชุด (batch scoring) คือทำนายหลายแถวตามรอบ ไม่ใช่ทีละคำขอทันที  
เป้าหมาย: ใช้ Champion จาก **Automated ML** ทำนายสมาชิกใหม่ 200 คน แล้วเขียน `data/gold/freshmart_predictions.parquet`

แทร็กนี้**ไม่สร้าง Batch Endpoint / Compute cluster** เพื่อคุมค่าใช้จ่ายฉุกเฉิน  
ใช้โมเดลจาก Model Registry ผ่าน `mlflow.pyfunc` บน compute instance เครื่องเดียว

### กฎทอง (ถามบ่อยที่สุด — อ่านก่อนรัน)
**ห้าม** คำนวณ min/max ใหม่จากชุด 200 คน  
**ต้อง** ใช้ `feature_params.json` จาก Lab 2

ถ้า scale ใหม่ ผลทำนายจะเพี้ยนหรือเอียงไปคลาสเดียว

### ถ้าติด — อ่านก่อนถาม TA
| อาการ | สาเหตุที่พบบ่อย | ทำอะไร |
| --- | --- | --- |
| หาโมเดลไม่เจอ | ยังไม่จบ Lab 3 | กลับไป register `freshmart-churn-model` |
| missing column / type mismatch | ลำดับฟีเจอร์ไม่ตรงลายเซ็น | ใช้ params จาก Lab 2 เท่านั้น |
| `models:/...` โหลดไม่ได้ | ยังไม่รันบน compute instance | ตรวจ Tracking URI แล้วรัน Lab 3 ใหม่บน Azure ML |"""
            ),
            md_cell("### เตรียม loader + ฟังก์ชันฟีเจอร์"),
            code_cell("import json\nfrom pathlib import Path\nimport pandas as pd\n\n" + LOADER),
            code_cell(FEATURE_CONTRACT_CELL),
            md_cell(
                """### ขั้นตอนที่ 1: โหลดชุดทำนาย + params ชุดฝึก

**โค้ดนี้ทำอะไร**
1. อ่าน `freshmart_scoring_batch.csv` (200 แถว **ไม่มี** คอลัมน์ Churn)
2. โหลด `feature_params.json` จาก Lab 2
3. `transform_customers(..., require_target=False)` ให้ได้ 14 ฟีเจอร์ตามลายเซ็นโมเดล

รหัสลูกค้าชุดนี้ขึ้นต้น `CUST_05xxx` ไม่ซ้อนกับชุดฝึก"""
            ),
            code_cell(
                r'''df_scoring_raw = load_csv("freshmart_scoring_batch.csv")
print(f"Scoring Batch count: {len(df_scoring_raw):,}")
assert "Churn" not in df_scoring_raw.columns
display(df_scoring_raw.head())

params_path = _first_existing([
    ARTIFACT_ROOT / "params" / "feature_params.json",
    Path("data/params/feature_params.json"),
    Path("../data/params/feature_params.json"),
])
if params_path:
    params = load_feature_params(params_path)
    print(f"Loaded feature params from {params_path}")
else:
    print("feature_params.json not found; fitting from bronze/customers")
    params = fit_preprocessor(load_table_or_csv(BRONZE_CUSTOMERS, "freshmart_customers.csv"))

feature_frame = transform_customers(df_scoring_raw, params, require_target=False)
print("Aligned columns:", list(feature_frame.columns))
print(feature_frame.head())'''
            ),
            md_cell(
                """### ขั้นตอนที่ 2: ทำนายด้วยโมเดลที่ลงทะเบียนไว้

**ความรู้สั้น ๆ:** `mlflow.pyfunc.load_model` โหลดโมเดลจาก Azure ML Model Registry แล้วทำนายหลายแถวพร้อมกัน

ส่งเฉพาะคอลัมน์ฟีเจอร์ — **อย่าส่ง** `CustomerID`  
ถ้าโหลดจาก registry ไม่ได้ เซลล์จะฝึก Random Forest ชั่วคราวเพื่อตรวจ pipeline — ไม่ใช่ผลส่งงานในห้องเรียน"""
            ),
            code_cell(
                r'''predictions = None
try:
    import mlflow
    pyfunc_model = mlflow.pyfunc.load_model("models:/freshmart-churn-model/1")
    preds = pyfunc_model.predict(model_matrix(feature_frame, params))
    predictions = feature_frame.copy()
    predictions["Churn_Prediction"] = preds
    print("Scored with mlflow.pyfunc from Model Registry")
except Exception as exc:
    print(f"Registry unavailable ({exc}). Retrain local champion for smoke test.")
    from sklearn.ensemble import RandomForestClassifier
    silver = load_table_or_csv(SILVER_CUSTOMER_FEATURES, "freshmart_customers.csv")
    if "MembershipTier_Bronze" not in silver.columns:
        raw = load_table_or_csv(BRONZE_CUSTOMERS, "freshmart_customers.csv")
        silver = transform_customers(raw, params, require_target=True)
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(model_matrix(silver, params), silver["Churn"].astype(int))
    predictions = feature_frame.copy()
    predictions["Churn_Prediction"] = model.predict(model_matrix(feature_frame, params))

print(predictions[["CustomerID", "RecencyDays", "MonetaryTotal", "ComplaintCount", "Churn_Prediction"]].head(10))'''
            ),
            md_cell(
                """### ขั้นตอนที่ 3: เขียนชั้น Gold + ความเร่งด่วนแคมเปญ

**โค้ดนี้ทำอะไร**
- เพิ่ม `Action_Priority`: ค่าทำนาย `1` เป็น High (ส่ง voucher), ค่า `0` เป็น Normal
- เขียน `data/gold/freshmart_predictions.parquet`

**สิ่งที่ควรเห็น:** 200 แถว และมีทั้งสองกลุ่มความเร่งด่วน  
(ชุดอ้างอิงท้องถิ่นประมาณ 36 High / 164 Normal — บน Azure ML อาจขยับเล็กน้อยถ้าชนิดข้อมูลไม่ตรง)

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

gold_path = save_layer(gold, GOLD_PREDICTIONS)
print(gold.groupby("Action_Priority").size().rename("CustomerCount"))
print(f"Published gold predictions: {gold_path}")
gold_csv = layer_path("gold", "freshmart_predictions", suffix=".csv")
gold.to_csv(gold_csv, index=False)
register_data_asset(ASSET_GOLD_PREDICTIONS, gold_csv, "FreshMart gold campaign predictions")

assert len(gold) == 200
print("Lab 4 verification passed")'''
            ),
        ],
    )
    print("All FreshMart Azure ML notebooks generated")


if __name__ == "__main__":
    build()

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

def load_table_or_csv(table_name: str, file_name: str) -> pd.DataFrame:
    try:
        frame = spark.read.table(table_name).toPandas()
        print(f"Loaded Spark table {table_name}: {len(frame):,} rows")
        return frame
    except Exception as exc:
        print(f"Spark table '{table_name}' unavailable ({exc}). Falling back to CSV.")
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

ตรวจว่า workspace / Lakehouse FreshMart พร้อมก่อน Lab 1

1. เปิด workspace `labs` แล้วแนบ Default Lakehouse = `lh_freshmart`
2. รันเซลล์ด้านล่างตามลำดับ
3. ถ้าตาราง Bronze ยังไม่พร้อม ระบบอ่าน CSV จาก `Files/raw/` ให้อัตโนมัติ"""
            ),
            code_cell(LOADER),
            md_cell("### โหลด Bronze (ตารางก่อน แล้วค่อย CSV)"),
            code_cell(
                """df_tx = load_table_or_csv("bronze_transactions", "freshmart_transactions.csv")
df_cust = load_table_or_csv("bronze_customers", "freshmart_customers.csv")

print(f"Transactions rows: {len(df_tx):,}")
print(f"Customers rows: {len(df_cust):,}")
print("Transaction columns:", list(df_tx.columns))
print("Customer columns:", list(df_cust.columns))
display(df_tx.head(5))
display(df_cust.head(5))"""
            ),
            md_cell("### จุดตรวจ (ผ่านแล้วค่อยเข้า Lab 1)"),
            code_cell(
                """if len(df_tx) != 3000:
    raise AssertionError(
        f"คาดว่าธุรกรรม 3,000 แถว แต่ได้ {len(df_tx):,} — ตรวจ Files/raw หรือตาราง bronze_transactions"
    )
if len(df_cust) != 1500:
    raise AssertionError(
        f"คาดว่าสมาชิก 1,500 แถว แต่ได้ {len(df_cust):,} — ตรวจ Files/raw หรือตาราง bronze_customers"
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

บทบาท: **Analyst** — สำรวจของเสียและพฤติกรรม Churn  
รันทีละเซลล์ จดสามข้อสังเกตสั้น ๆ ก่อน Lab 2 ไม่ต้องจำสูตรสถิติ"""
            ),
            code_cell(LOADER),
            md_cell("### ขั้นตอนที่ 1: โหลดข้อมูลธุรกรรม"),
            code_cell(
                """df = load_table_or_csv("bronze_transactions", "freshmart_transactions.csv")
print(f"Pandas DataFrame shape: {df.shape}")
df.head()"""
            ),
            md_cell("### ขั้นตอนที่ 2: Data Quality"),
            code_cell(
                """print("=== DataFrame Info ===")
df.info()
print("\\n=== Missing Values Count ===")
missing = df.isnull().sum()
print(missing[missing > 0])
print(f"DiscountRate missing rate: {df['DiscountRate'].isna().mean():.2%}")"""
            ),
            md_cell("### ขั้นตอนที่ 3: Descriptive Statistics"),
            code_cell(
                """df[["UnitsSold", "UnitPrice", "DiscountRate", "SalesAmount", "WasteUnits", "WasteCost"]].describe()"""
            ),
            md_cell("### ขั้นตอนที่ 4: Histogram และ Box Plot"),
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
            code_cell(
                """plt.figure(figsize=(10, 5))
sns.boxplot(data=df, x="StoreType", y="WasteUnits", hue="StoreType", palette="Set2", legend=False)
plt.title("Waste Units by Store Type")
plt.show()"""
            ),
            md_cell("### ขั้นตอนที่ 5: Correlation Heatmap"),
            code_cell(
                """numeric_cols = ["UnitsSold", "UnitPrice", "DiscountRate", "SalesAmount", "WasteUnits", "WasteCost", "IsWeekend"]
corr_matrix = df[numeric_cols].corr(numeric_only=True)
print(corr_matrix.round(2))

plt.figure(figsize=(9, 7))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="vlag", vmin=-1, vmax=1, linewidths=0.5)
plt.title("FreshMart Feature Correlation Matrix")
plt.show()"""
            ),
            md_cell("### ขั้นตอนที่ 6: Customer Churn EDA"),
            code_cell(
                """df_cust = load_table_or_csv("bronze_customers", "freshmart_customers.csv")
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

ใช้ Data Wrangler แล้ว **Add code to notebook** ได้จริง

| ส่วน | ทำอะไร |
| --- | --- |
| **A** | Wrangler กับธุรกรรม (format / filter / group by) → ใส่โค้ดกลับ notebook |
| **B** | รันสัญญาฟีเจอร์สมาชิก → ได้ Silver + `feature_params.json` สำหรับ Lab 3–4 |

Lab 4 ต้องใช้ params จากชุดฝึก — ส่วน B จึงล็อกสเกลให้ทั้งคลาส"""
            ),
            code_cell("import json\nfrom pathlib import Path\nimport pandas as pd\n\n" + LOADER),
            md_cell(
                """### ส่วน A — โหลดธุรกรรมสำหรับ Data Wrangler

สุ่ม 500 แถวให้ UI ตอบสนองเร็วขึ้น"""
            ),
            code_cell(
                """df = load_table_or_csv("bronze_transactions", "freshmart_transactions.csv")
df = df.sample(n=500, random_state=1).reset_index(drop=True)
print("Sample for Data Wrangler:", df.shape)
df.head(4)"""
            ),
            md_cell(
                """### ส่วน A — เปิด Data Wrangler แล้วใส่โค้ดกลับ notebook

1. รอ kernel ว่าง แล้วแท็บ **Home** → **Data Wrangler** → เลือก `df`
2. ดู Summary ของ `WasteCost`
3. **Format** คอลัมน์ `Category` (Capitalize all words) → Apply
4. **Filter** `StoreType` = `Express` และ/หรือ **Sort** `WasteCost` Descending → Apply
5. ลบขั้น Filter/Sort จาก Cleaning steps ถ้าต้องการใช้ทั้งตัวอย่าง แล้ว **Group by** `Category` + aggregate `WasteCost` (Mean)
6. กด **Add code to notebook** — วางโค้ดในเซลล์ว่างด้านล่าง แล้วรัน

ตัวอย่างโครงฟังก์ชันหลังได้โค้ดจาก Wrangler:"""
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

(ทางเลือก) เปิด Wrangler กับ `df_cust` เพื่อลอง Fill Age / One-hot / Scale  
สำหรับส่งงาน Lab 3–4 ให้รันเซลล์สัญญาฟีเจอร์ถัดไป เพื่อได้ `feature_params.json` ชุดเดียวกันทั้งคลาส"""
            ),
            code_cell(
                """df_cust = load_table_or_csv("bronze_customers", "freshmart_customers.csv")
print("Customers DataFrame loaded:", df_cust.shape)
print("Age missing:", int(df_cust["Age"].isna().sum()))
df_cust.head(3)"""
            ),
            md_cell("### ส่วน B — รันสัญญาฟีเจอร์ที่เตรียมให้"),
            code_cell(
                "from dataclasses import asdict, dataclass\nfrom typing import Any\nimport logging\n\n"
                "logger = logging.getLogger(__name__)\n\n" + CONSTANTS + "\n\n" + FEATURE_SOURCE
            ),
            code_cell(
                """params = fit_preprocessor(df_cust)
df_clean = transform_customers(df_cust, params, require_target=True)
print(f"Cleaned DataFrame Shape: {df_clean.shape}")
print("Feature columns:", params.feature_columns)
print(f"Age median used for imputation: {params.age_median:.1f}")
display(df_clean.head(5))"""
            ),
            md_cell("### ส่วน B — บันทึก Silver table และ params สำหรับ Lab 4"),
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
    spark.createDataFrame(df_clean).write.format("delta").mode("overwrite").saveAsTable("silver_customer_features")
    print("Saved silver_customer_features to Lakehouse")
except Exception as exc:
    out = local_dir / "silver_customer_features.csv"
    df_clean.to_csv(out, index=False)
    print(f"Spark write unavailable ({exc}). Wrote {out}")'''
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

ทำนาย **Churn** (classification) แล้วเทียบ Decision Tree กับ Random Forest

**AUC** = คะแนนแยกกลุ่ม Churn (ใกล้ 1 ดีกว่า) — เก็บตัวชนะเป็น `freshmart-churn-model`"""
            ),
            code_cell("import json\nfrom pathlib import Path\nimport pandas as pd\n\n" + LOADER),
            code_cell("from dataclasses import asdict, dataclass\nfrom typing import Any\nimport logging\n\nlogger = logging.getLogger(__name__)\n\n" + CONSTANTS + "\n\n" + FEATURE_SOURCE),
            md_cell("### ขั้นตอนที่ 1: โหลด Silver features"),
            code_cell(
                r'''df_features = load_table_or_csv("silver_customer_features", ".local/silver_customer_features.csv")
if "MembershipTier_Bronze" not in df_features.columns:
    raw = load_table_or_csv("bronze_customers", "freshmart_customers.csv")
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
        raw = load_table_or_csv("bronze_customers", "freshmart_customers.csv")
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
            md_cell("### ขั้นตอนที่ 2: MLflow Experiment"),
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
            md_cell("### ขั้นตอนที่ 3: Baseline Decision Tree"),
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
            md_cell("### ขั้นตอนที่ 4: Champion Random Forest"),
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
            md_cell("### ขั้นตอนที่ 5: ลงทะเบียน Champion"),
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

ทำนายสมาชิกชุดใหม่ 200 คน แล้วเขียนตาราง Gold + `Action_Priority` พร้อมแคมเปญ

กฎทอง: ใช้ `feature_params.json` จาก Lab 2 เท่านั้น อย่าคำนวณ min/max ใหม่จากชุด scoring"""
            ),
            code_cell("import json\nfrom pathlib import Path\nimport pandas as pd\n\n" + LOADER),
            code_cell("from dataclasses import asdict, dataclass\nfrom typing import Any\nimport logging\n\nlogger = logging.getLogger(__name__)\n\n" + CONSTANTS + "\n\n" + FEATURE_SOURCE),
            md_cell("### ขั้นตอนที่ 1: โหลด scoring batch และ params ของชุดฝึก"),
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
    print("feature_params.json not found; fitting from bronze_customers")
    params = fit_preprocessor(load_table_or_csv("bronze_customers", "freshmart_customers.csv"))

spark_features = transform_customers(df_scoring_raw, params, require_target=False)
print("Aligned columns:", list(spark_features.columns))
print(spark_features.head())'''
            ),
            md_cell("### ขั้นตอนที่ 2: PREDICT / fallback"),
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
        silver = load_table_or_csv("silver_customer_features", ".local/silver_customer_features.csv")
        if "MembershipTier_Bronze" not in silver.columns:
            raw = load_table_or_csv("bronze_customers", "freshmart_customers.csv")
            silver = transform_customers(raw, params, require_target=True)
        model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        model.fit(model_matrix(silver, params), silver["Churn"].astype(int))
        predictions = spark_features.copy()
        predictions["Churn_Prediction"] = model.predict(model_matrix(spark_features, params))

print(predictions[["CustomerID", "RecencyDays", "MonetaryTotal", "ComplaintCount", "Churn_Prediction"]].head(10))'''
            ),
            md_cell("### ขั้นตอนที่ 3: เขียน Gold table"),
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
        .saveAsTable("gold_freshmart_predictions")
    )
    print("Published gold_freshmart_predictions")
    spark.sql("""
        SELECT Action_Priority, COUNT(*) AS CustomerCount
        FROM gold_freshmart_predictions
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

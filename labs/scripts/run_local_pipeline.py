"""Run the FreshMart Lab 1-4 logic locally without Microsoft Fabric.

This smoke script is the instructor/pre-class verification path. It uses the
same feature contract as the published notebooks.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "labs" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from freshmart_features import (  # noqa: E402
    fit_preprocessor,
    model_matrix,
    save_feature_params,
    transform_customers,
)
from freshmart_io import (  # noqa: E402
    DATA_DIR,
    FEATURE_PARAMS_PATH,
    LOCAL_ARTIFACT_DIR,
    save_local_csv,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("freshmart.local")


def main() -> int:
    """Execute the local FreshMart pipeline and write Gold artifacts."""
    try:
        customers = pd.read_csv(DATA_DIR / "freshmart_customers.csv")
        scoring = pd.read_csv(DATA_DIR / "freshmart_scoring_batch.csv")
        transactions = pd.read_csv(DATA_DIR / "freshmart_transactions.csv")

        logger.info("Transactions=%s Customers=%s Scoring=%s", len(transactions), len(customers), len(scoring))
        logger.info("Churn rate=%.1f%%", customers["Churn"].mean() * 100)
        logger.info(
            "WasteCost by Category:\n%s",
            transactions.groupby("Category")["WasteCost"].sum().sort_values(ascending=False).to_string(),
        )

        params = fit_preprocessor(customers)
        silver = transform_customers(customers, params, require_target=True)
        save_feature_params(params, FEATURE_PARAMS_PATH)
        save_local_csv(silver, "silver_customer_features.csv")

        x = model_matrix(silver, params)
        y = silver["Churn"].astype(int)
        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=0.20, random_state=42, stratify=y
        )

        dt = DecisionTreeClassifier(max_depth=5, random_state=42).fit(x_train, y_train)
        rf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42).fit(
            x_train, y_train
        )
        dt_auc = roc_auc_score(y_test, dt.predict_proba(x_test)[:, 1])
        rf_auc = roc_auc_score(y_test, rf.predict_proba(x_test)[:, 1])
        logger.info("DecisionTree AUC=%.4f", dt_auc)
        logger.info("RandomForest AUC=%.4f", rf_auc)
        logger.info("RandomForest report:\n%s", classification_report(y_test, rf.predict(x_test)))
        if rf_auc <= dt_auc:
            raise RuntimeError("Champion Random Forest did not beat Decision Tree")

        scored = transform_customers(scoring, params, require_target=False)
        scored["Churn_Prediction"] = rf.predict(model_matrix(scored, params))
        scored["Action_Priority"] = scored["Churn_Prediction"].map(
            {
                1: "High - Send Retention Voucher",
                0: "Normal - Standard Engagement",
            }
        )
        save_local_csv(scored, "gold_freshmart_predictions.csv")
        summary = scored.groupby("Action_Priority").size()
        logger.info("Gold prediction summary:\n%s", summary.to_string())
        logger.info("Local artifacts written to %s", LOCAL_ARTIFACT_DIR)
        print("LOCAL PIPELINE OK")
        return 0
    except Exception:
        logger.exception("Local FreshMart pipeline failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

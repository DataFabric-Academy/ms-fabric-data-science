"""End-to-end churn-model smoke tests for Lab 3 and Lab 4."""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from freshmart_features import (
    fit_preprocessor,
    model_matrix,
    transform_customers,
)


def test_random_forest_beats_decision_tree(customers_df) -> None:
    """Champion Random Forest should outrank the Decision Tree baseline."""
    params = fit_preprocessor(customers_df)
    silver = transform_customers(customers_df, params, require_target=True)
    x = model_matrix(silver, params)
    y = silver["Churn"].astype(int)

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.20, random_state=42, stratify=y
    )

    dt = DecisionTreeClassifier(max_depth=5, random_state=42)
    rf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    dt.fit(x_train, y_train)
    rf.fit(x_train, y_train)

    dt_auc = roc_auc_score(y_test, dt.predict_proba(x_test)[:, 1])
    rf_auc = roc_auc_score(y_test, rf.predict_proba(x_test)[:, 1])
    rf_f1 = f1_score(y_test, rf.predict(x_test))

    assert rf_auc > dt_auc
    assert rf_auc >= 0.72
    assert rf_f1 >= 0.40


def test_scoring_batch_produces_both_classes(customers_df, scoring_df) -> None:
    """Lab 4 Gold table should contain both stay and churn actions."""
    params = fit_preprocessor(customers_df)
    silver = transform_customers(customers_df, params, require_target=True)
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(model_matrix(silver, params), silver["Churn"].astype(int))

    scored = transform_customers(scoring_df, params, require_target=False)
    preds = model.predict(model_matrix(scored, params))

    assert len(preds) == 200
    assert set(np.unique(preds)) == {0, 1}
    churn_count = int((preds == 1).sum())
    assert 20 <= churn_count <= 160

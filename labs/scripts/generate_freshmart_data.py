"""Generate FreshMart datasets whose statistical patterns match the lab story."""

from __future__ import annotations

import csv
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[1] / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)
random.seed(42)


def _pick_tier(tiers: list[str], probs: list[float]) -> str:
    """Draw a membership tier from the published mix."""
    draw = random.random()
    cumulative = 0.0
    for tier, prob in zip(tiers, probs, strict=True):
        cumulative += prob
        if draw <= cumulative:
            return tier
    return tiers[-1]


def generate_transactions(path: Path, n_rows: int = 3000) -> None:
    """Write transaction rows with discount, waste, and store-type patterns."""
    stores = ["ST001_Siam", "ST002_Sukhumvit", "ST003_Silom", "ST004_Ari", "ST005_Ladprao"]
    store_types = {
        "ST001_Siam": "Hypermarket",
        "ST002_Sukhumvit": "Supermarket",
        "ST003_Silom": "Express",
        "ST004_Ari": "Supermarket",
        "ST005_Ladprao": "Hypermarket",
    }
    products = [
        ("PRD_BAK_001", "Croissant Butter", "Bakery", 45.0),
        ("PRD_BAK_002", "Whole Wheat Bread", "Bakery", 55.0),
        ("PRD_BAK_003", "Baguette Traditional", "Bakery", 40.0),
        ("PRD_BAK_004", "Danish Apple", "Bakery", 50.0),
        ("PRD_PRD_001", "Organic Avocado", "Produce", 69.0),
        ("PRD_PRD_002", "Japanese Salad Mix", "Produce", 59.0),
        ("PRD_PRD_003", "Sweet Cherry Tomato", "Produce", 49.0),
        ("PRD_DAI_001", "Fresh Milk Pasteurized 1L", "Dairy", 48.0),
        ("PRD_DAI_002", "Greek Yogurt Plain", "Dairy", 35.0),
        ("PRD_BEV_001", "Cold Pressed Orange Juice", "Beverages", 65.0),
        ("PRD_BEV_002", "Organic Green Tea", "Beverages", 40.0),
    ]
    start_date = datetime(2026, 1, 1)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "TransactionID",
                "Date",
                "StoreID",
                "StoreType",
                "ProductID",
                "ProductName",
                "Category",
                "UnitsSold",
                "UnitPrice",
                "DiscountRate",
                "SalesAmount",
                "WasteUnits",
                "WasteCost",
                "IsWeekend",
            ]
        )
        for index in range(1, n_rows + 1):
            day_offset = random.randint(0, 180)
            tx_date = start_date + timedelta(days=day_offset)
            store = random.choice(stores)
            store_type = store_types[store]
            product_id, product_name, category, base_price = random.choice(products)

            if category in {"Bakery", "Produce"}:
                discount = random.choice([0.0, 0.0, 0.05, 0.10, 0.15, 0.20])
            else:
                discount = random.choice([0.0, 0.0, 0.05, 0.10])

            base_qty = {"Hypermarket": 7, "Supermarket": 5, "Express": 4}[store_type]
            qty = max(1, int(random.gauss(base_qty * (1 + 2.2 * discount), 1.6)))
            final_price = round(base_price * (1 - discount), 2)
            sales_amount = round(qty * final_price, 2)
            is_weekend = int(tx_date.weekday() >= 5)

            waste_prob = {"Bakery": 0.16, "Produce": 0.13, "Dairy": 0.04, "Beverages": 0.03}[category]
            if store_type == "Express":
                waste_prob += 0.14
            if store_type == "Express" and is_weekend:
                waste_prob += 0.12
            if discount == 0.0:
                waste_prob += 0.10
            else:
                waste_prob -= 0.08
            waste_prob = min(0.85, max(0.01, waste_prob))

            if random.random() < waste_prob:
                waste_units = max(1, int(random.gauss(2.2 if store_type == "Express" else 1.1, 0.8)))
            else:
                waste_units = 0
            waste_cost = round(waste_units * base_price * 0.6, 2)
            discount_str = f"{discount:.2f}" if random.random() > 0.034 else ""

            writer.writerow(
                [
                    f"TX{index:06d}",
                    tx_date.strftime("%Y-%m-%d"),
                    store,
                    store_type,
                    product_id,
                    product_name,
                    category,
                    qty,
                    f"{base_price:.2f}",
                    discount_str,
                    f"{sales_amount:.2f}",
                    waste_units,
                    f"{waste_cost:.2f}",
                    is_weekend,
                ]
            )


def generate_customers(path: Path, n_rows: int = 1500) -> int:
    """Write labeled customers with a learnable churn signal.

    Returns:
        Number of churned customers.
    """
    tiers = ["Bronze", "Silver", "Gold", "Platinum"]
    tier_probs = [0.45, 0.30, 0.18, 0.07]
    churn_count = 0

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "CustomerID",
                "Age",
                "Gender",
                "MembershipTier",
                "TenureMonths",
                "RecencyDays",
                "Frequency",
                "MonetaryTotal",
                "AvgBasketSize",
                "ComplaintCount",
                "Churn",
            ]
        )
        for cid in range(1001, 1001 + n_rows):
            age = max(18, min(75, int(random.gauss(38, 11))))
            gender = random.choice(["F", "M", "Other"])
            tier = _pick_tier(tiers, tier_probs)
            tenure = max(1, min(72, int(random.expovariate(1 / 18))))
            recency = max(1, min(120, int(random.expovariate(1 / 25))))
            freq_mean = {"Bronze": 4, "Silver": 8, "Gold": 15, "Platinum": 24}[tier]
            frequency = max(1, int(random.gauss(freq_mean, freq_mean * 0.25)))
            basket_mean = {"Bronze": 380, "Silver": 650, "Gold": 1200, "Platinum": 2300}[tier]
            monetary = round(frequency * max(150, random.gauss(basket_mean, basket_mean * 0.2)), 2)
            avg_basket = round(monetary / frequency, 2)
            complaint_rate = 0.25 if tier in {"Gold", "Platinum"} else 0.7
            complaints = max(0, min(5, int(random.gauss(complaint_rate, 0.8))))

            churn_z = (
                -2.4
                + (recency * 0.055)
                + (complaints * 1.15)
                - (frequency * 0.12)
                - (tenure * 0.03)
            )
            churn_prob = 1.0 / (1.0 + math.exp(-max(-8.0, min(8.0, churn_z))))
            churn = 1 if random.random() < churn_prob else 0
            churn_count += churn
            age_str = str(age) if random.random() > 0.023 else ""

            writer.writerow(
                [
                    f"CUST_{cid:05d}",
                    age_str,
                    gender,
                    tier,
                    tenure,
                    recency,
                    frequency,
                    f"{monetary:.2f}",
                    f"{avg_basket:.2f}",
                    complaints,
                    churn,
                ]
            )
    return churn_count


def generate_scoring_batch(path: Path, n_rows: int = 200) -> None:
    """Write an unlabeled scoring cohort with unseen customer IDs."""
    tiers = ["Bronze", "Silver", "Gold", "Platinum"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "CustomerID",
                "Age",
                "Gender",
                "MembershipTier",
                "TenureMonths",
                "RecencyDays",
                "Frequency",
                "MonetaryTotal",
                "AvgBasketSize",
                "ComplaintCount",
            ]
        )
        for cid in range(5001, 5001 + n_rows):
            age = max(20, min(70, int(random.gauss(40, 10))))
            gender = random.choice(["F", "M"])
            tier = random.choice(tiers)
            tenure = random.randint(2, 48)
            recency = random.randint(3, 85)
            freq_mean = {"Bronze": 3, "Silver": 7, "Gold": 14, "Platinum": 22}[tier]
            frequency = max(1, int(random.gauss(freq_mean, 2)))
            basket_mean = {"Bronze": 380, "Silver": 680, "Gold": 1250, "Platinum": 2500}[tier]
            monetary = round(frequency * max(150, random.gauss(basket_mean, 150)), 2)
            avg_basket = round(monetary / frequency, 2)
            complaints = random.choice([0, 0, 0, 1, 1, 2])
            writer.writerow(
                [
                    f"CUST_{cid:05d}",
                    age,
                    gender,
                    tier,
                    tenure,
                    recency,
                    frequency,
                    f"{monetary:.2f}",
                    f"{avg_basket:.2f}",
                    complaints,
                ]
            )


def main() -> None:
    """Generate all published FreshMart CSV files."""
    tx_path = OUT_DIR / "freshmart_transactions.csv"
    cust_path = OUT_DIR / "freshmart_customers.csv"
    score_path = OUT_DIR / "freshmart_scoring_batch.csv"
    generate_transactions(tx_path)
    churn_count = generate_customers(cust_path)
    generate_scoring_batch(score_path)
    print(f"Generated {tx_path.name}: 3000 rows")
    print(f"Generated {cust_path.name}: 1500 rows (churn={churn_count/1500:.1%})")
    print(f"Generated {score_path.name}: 200 rows")


if __name__ == "__main__":
    main()

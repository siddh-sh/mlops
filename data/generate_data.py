"""Generate a car price dataset with the same schema as the Kaggle
"Vehicle dataset from CarDekho" (CAR DETAILS FROM CAR DEKHO.csv).

If you download the real Kaggle CSV, save it as data/car_data.csv and
skip this script - the training code works with either.
"""
import os

import numpy as np
import pandas as pd

BRANDS = {
    # brand: (base price in INR, models)
    "Maruti": (550_000, ["Swift", "Alto", "Wagon R", "Baleno", "Ertiga"]),
    "Hyundai": (700_000, ["i10", "i20", "Creta", "Verna", "Venue"]),
    "Honda": (850_000, ["City", "Amaze", "Jazz", "WR-V"]),
    "Toyota": (1_400_000, ["Innova", "Fortuner", "Corolla", "Etios"]),
    "Mahindra": (950_000, ["XUV500", "Scorpio", "Bolero", "Thar"]),
    "Tata": (600_000, ["Nexon", "Tiago", "Harrier", "Indica"]),
    "Ford": (750_000, ["EcoSport", "Figo", "Endeavour"]),
    "BMW": (4_000_000, ["3 Series", "5 Series", "X1"]),
    "Audi": (3_800_000, ["A4", "A6", "Q3"]),
}
FUELS = {"Petrol": 1.0, "Diesel": 1.15, "CNG": 0.9, "LPG": 0.85, "Electric": 1.3}
SELLERS = {"Individual": 1.0, "Dealer": 1.08, "Trustmark Dealer": 1.12}
TRANSMISSIONS = {"Manual": 1.0, "Automatic": 1.25}
OWNERS = {
    "First Owner": 1.0,
    "Second Owner": 0.88,
    "Third Owner": 0.78,
    "Fourth & Above Owner": 0.7,
    "Test Drive Car": 1.1,
}


def generate(n_rows: int = 4000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n_rows):
        brand = rng.choice(list(BRANDS))
        base, models = BRANDS[brand]
        model = rng.choice(models)
        year = int(rng.integers(2005, 2025))
        age = 2025 - year
        km = int(max(1000, rng.normal(12_000 * age + 5_000, 15_000)))
        fuel = rng.choice(list(FUELS), p=[0.48, 0.45, 0.04, 0.01, 0.02])
        seller = rng.choice(list(SELLERS), p=[0.75, 0.2, 0.05])
        trans = rng.choice(list(TRANSMISSIONS), p=[0.85, 0.15])
        owner = rng.choice(list(OWNERS), p=[0.6, 0.25, 0.08, 0.04, 0.03])

        price = (
            base
            * (0.88 ** age)
            * FUELS[fuel]
            * SELLERS[seller]
            * TRANSMISSIONS[trans]
            * OWNERS[owner]
            * max(0.5, 1 - km / 600_000)
            * rng.normal(1.0, 0.08)
        )
        rows.append(
            {
                "name": f"{brand} {model}",
                "year": year,
                "selling_price": int(round(max(price, 30_000), -3)),
                "km_driven": km,
                "fuel": fuel,
                "seller_type": seller,
                "transmission": trans,
                "owner": owner,
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "car_data.csv")
    df = generate()
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} rows to {out}")

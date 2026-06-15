import argparse
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "data" / "douban_movies.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect the real Douban CSV schema")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="CSV input path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"CSV not found: {input_path}")

    dataframe = pd.read_csv(input_path)
    print("=== COLUMN NAMES ===")
    print(list(dataframe.columns))
    print("\n=== FIRST 5 ROWS ===")
    print(dataframe.head(5).to_string(index=False))
    print("\n=== MISSING VALUE COUNTS ===")
    print(dataframe.isna().sum().to_string())


if __name__ == "__main__":
    main()


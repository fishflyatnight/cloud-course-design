import argparse
from pathlib import Path

import pandas as pd


OUTPUT_COLUMNS = [
    "engine",
    "executors",
    "query",
    "run",
    "seconds",
    "speedup_vs_pandas",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build performance_results.csv from real measured timings"
    )
    parser.add_argument(
        "--input",
        default="timings.csv",
        help="CSV with engine,executors,query,run,seconds,notes",
    )
    parser.add_argument("--output", default="performance_results.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        pd.DataFrame(columns=OUTPUT_COLUMNS).to_csv(output_path, index=False)
        print(
            f"No timing input found at {input_path}. "
            f"Created an empty framework at {output_path}; fill it only with real runs."
        )
        return

    timings = pd.read_csv(input_path)
    required = {"engine", "executors", "query", "run", "seconds"}
    missing = sorted(required.difference(timings.columns))
    if missing:
        raise ValueError(f"Timing CSV is missing columns: {missing}")

    timings["seconds"] = pd.to_numeric(timings["seconds"], errors="raise")
    if "notes" not in timings.columns:
        timings["notes"] = ""

    pandas_rows = timings[timings["engine"].str.lower() == "pandas"]
    if pandas_rows.empty:
        timings["speedup_vs_pandas"] = pd.NA
    else:
        pandas_baselines = pandas_rows.groupby("query")["seconds"].mean()
        timings["speedup_vs_pandas"] = timings.apply(
            lambda row: (
                pandas_baselines.get(row["query"], float("nan")) / row["seconds"]
                if row["seconds"] > 0
                else float("nan")
            ),
            axis=1,
        )

    timings[OUTPUT_COLUMNS].to_csv(output_path, index=False)
    print(f"Performance comparison written from measured input to {output_path}")


if __name__ == "__main__":
    main()


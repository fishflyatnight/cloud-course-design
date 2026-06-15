import argparse
import time
from pathlib import Path

import pandas as pd


DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "data" / "douban_movies.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pandas baseline for genre analysis")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--timing-output", help="Optional CSV file for measured timings")
    parser.add_argument("--run", type=int, default=1, help="Run number stored in timing CSV")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_started = time.perf_counter()
    movies = pd.read_csv(args.input)
    load_seconds = time.perf_counter() - load_started

    required = {"genres", "rating_score"}
    missing = sorted(required.difference(movies.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}; actual={list(movies.columns)}")

    query_started = time.perf_counter()
    genre_rows = movies[["genres", "rating_score"]].dropna(subset=["rating_score"]).copy()
    genre_rows["genres"] = genre_rows["genres"].fillna("未知").str.split("/")
    genre_rows = genre_rows.explode("genres").rename(columns={"genres": "genre"})
    result = (
        genre_rows.groupby("genre", as_index=False)
        .agg(movie_count=("rating_score", "size"), avg_rating=("rating_score", "mean"))
        .sort_values(
            by=["avg_rating", "movie_count", "genre"],
            ascending=[False, False, True],
        )
        .head(20)
    )
    query_seconds = time.perf_counter() - query_started

    print("=== PANDAS 类型维度评分分析 ===")
    print(result.to_string(index=False))
    print(f"TIMING engine=pandas phase=load seconds={load_seconds:.6f}")
    print(f"TIMING engine=pandas phase=query seconds={query_seconds:.6f}")

    if args.timing_output:
        pd.DataFrame(
            [
                {
                    "engine": "pandas",
                    "executors": 0,
                    "query": "genre_rating",
                    "run": args.run,
                    "seconds": query_seconds,
                    "notes": f"load_seconds={load_seconds:.6f}",
                }
            ]
        ).to_csv(args.timing_output, index=False)
        print(f"Measured timing CSV saved to {args.timing_output}")


if __name__ == "__main__":
    main()

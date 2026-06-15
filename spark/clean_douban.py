import argparse
from pathlib import Path
from typing import Iterable, Optional

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "data" / "douban_movies.csv"
ALIASES = {
    "movie_id": ("movie_id", "id"),
    "title": ("title", "movie_title", "name"),
    "year": ("year", "release_year"),
    "rating_score": ("rating_score", "rating", "score"),
    "genres": ("genres", "genre", "types"),
    "directors": ("directors", "director"),
    "summary": ("summary", "description", "intro"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean the Douban movie CSV with PySpark")
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Local CSV path or s3a://[OBS_BUCKET]/douban_movies.csv",
    )
    parser.add_argument(
        "--output",
        default="data/cleaned/douban_movies",
        help="Local output directory or an s3a:// path",
    )
    parser.add_argument("--format", choices=("parquet", "csv"), default="parquet")
    return parser.parse_args()


def spark_path(raw_path: str) -> str:
    if "://" in raw_path:
        return raw_path
    return Path(raw_path).resolve().as_uri()


def first_matching(
    columns: Iterable[str], candidates: Iterable[str]
) -> Optional[str]:
    lookup = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]
    return None


def normalize_columns(dataframe: DataFrame) -> DataFrame:
    for canonical, candidates in ALIASES.items():
        matched = first_matching(dataframe.columns, candidates)
        if matched and matched != canonical:
            dataframe = dataframe.withColumnRenamed(matched, canonical)
    required = {"year", "rating_score", "genres", "directors", "summary"}
    missing = sorted(required.difference(dataframe.columns))
    if missing:
        raise ValueError(
            f"Required columns are missing after alias matching: {missing}; "
            f"actual columns={dataframe.columns}"
        )
    return dataframe


def missing_expression(column_name: str):
    column = F.col(column_name)
    return F.when(column.isNull() | (F.trim(column.cast("string")) == ""), 1).otherwise(0)


def print_missing_report(dataframe: DataFrame, total_rows: int) -> None:
    aggregations = [
        F.sum(missing_expression(column_name)).alias(column_name)
        for column_name in dataframe.columns
    ]
    counts = dataframe.agg(*aggregations).first().asDict()
    print("=== MISSING VALUE REPORT ===", flush=True)
    for column_name in dataframe.columns:
        missing_count = int(counts[column_name] or 0)
        ratio = missing_count / total_rows if total_rows else 0.0
        print(
            f"{column_name}: missing={missing_count}, ratio={ratio:.6f}",
            flush=True,
        )


def main() -> None:
    args = parse_args()
    spark = SparkSession.builder.appName("DoubanDataCleaning").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    input_path = spark_path(args.input)
    output_path = spark_path(args.output)
    print(f"=== CLEANING START input={input_path} output={output_path} ===", flush=True)

    dataframe = (
        spark.read.option("header", True)
        .option("inferSchema", True)
        .option("multiLine", True)
        .option("quote", '"')
        .option("escape", '"')
        .option("encoding", "UTF-8")
        .csv(input_path)
    )
    dataframe = normalize_columns(dataframe)
    dataframe = dataframe.withColumn("year", F.col("year").cast("int")).withColumn(
        "rating_score", F.col("rating_score").cast("double")
    )
    for optional_count_column in ("rating_count", "collect_count"):
        if optional_count_column in dataframe.columns:
            dataframe = dataframe.withColumn(
                optional_count_column, F.col(optional_count_column).cast("long")
            )

    print("=== RAW SCHEMA ===", flush=True)
    dataframe.printSchema()
    print("=== RAW FIRST 5 ROWS ===", flush=True)
    dataframe.show(5, truncate=False)

    before_count = dataframe.count()
    print(f"RAW_ROW_COUNT={before_count}", flush=True)
    print_missing_report(dataframe, before_count)

    # Task A-1: drop rows whose key analytical fields are unusable.
    cleaned = dataframe.dropna(subset=["rating_score", "year"])

    # Task A-1: fill text fields rather than discarding otherwise usable movies.
    cleaned = cleaned.fillna(
        {
            "genres": "未知",
            "directors": "未知",
            "summary": "",
        }
    )

    after_count = cleaned.count()
    print(f"CLEAN_ROW_COUNT={after_count}", flush=True)
    print(f"DROPPED_ROW_COUNT={before_count - after_count}", flush=True)

    numeric_columns = [
        column_name
        for column_name in (
            "year",
            "rating_score",
            "rating_count",
            "collect_count",
        )
        if column_name in cleaned.columns
    ]
    print("=== NUMERIC SUMMARY mean/std/min/max ===", flush=True)
    cleaned.select(*numeric_columns).summary("mean", "stddev", "min", "max").show(
        truncate=False
    )

    writer = cleaned.write.mode("overwrite")
    if args.format == "csv":
        writer.option("header", True).csv(output_path)
    else:
        writer.parquet(output_path)

    print(f"=== CLEANING COMPLETE saved={output_path} format={args.format} ===", flush=True)
    spark.stop()


if __name__ == "__main__":
    main()

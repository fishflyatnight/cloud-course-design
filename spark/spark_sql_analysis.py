import argparse
import time
from pathlib import Path
from typing import Callable

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window


DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "data" / "douban_movies.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Spark SQL analysis for Douban movies")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--format", choices=("csv", "parquet"), default="csv")
    parser.add_argument("--director-limit", type=int, default=20)
    return parser.parse_args()


def spark_path(raw_path: str) -> str:
    if "://" in raw_path:
        return raw_path
    return Path(raw_path).resolve().as_uri()


def load_movies(spark: SparkSession, input_path: str, input_format: str) -> DataFrame:
    path = spark_path(input_path)
    if input_format == "parquet":
        dataframe = spark.read.parquet(path)
    else:
        dataframe = (
            spark.read.option("header", True)
            .option("inferSchema", True)
            .option("multiLine", True)
            .option("quote", '"')
            .option("escape", '"')
            .option("encoding", "UTF-8")
            .csv(path)
        )

    required = {"title", "year", "rating_score", "genres", "directors"}
    missing = sorted(required.difference(dataframe.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}; actual={dataframe.columns}")

    return (
        dataframe.withColumn("year", F.col("year").cast("int"))
        .withColumn("rating_score", F.col("rating_score").cast("double"))
        .dropna(subset=["title", "year", "rating_score"])
        .fillna({"genres": "未知", "directors": "未知"})
    )


def timed_query(title: str, query_id: str, query: Callable[[], DataFrame]) -> None:
    print(f"\n=== {title} ===", flush=True)
    started = time.perf_counter()
    result = query()
    result.show(20, truncate=False)
    elapsed = time.perf_counter() - started
    print(f"TIMING query={query_id} seconds={elapsed:.6f}", flush=True)


# Task A-2: GROUP BY aggregation and type-dimension rating analysis.
def query_genre_rating(movies: DataFrame) -> DataFrame:
    exploded = movies.withColumn("genre", F.explode(F.split("genres", "/")))
    return (
        exploded.groupBy("genre")
        .agg(
            F.count("*").alias("movie_count"),
            F.avg("rating_score").alias("avg_rating"),
        )
        .orderBy(F.desc("avg_rating"), F.desc("movie_count"), "genre")
    )


# Task A-2: time-dimension trend analysis by year.
def query_year_trend(movies: DataFrame) -> DataFrame:
    return (
        movies.groupBy("year")
        .agg(
            F.count("*").alias("movie_count"),
            F.avg("rating_score").alias("avg_rating"),
        )
        .orderBy("year")
    )


# Task A-2: ORDER BY Top-N analysis for directors.
def query_director_top_n(movies: DataFrame, limit: int) -> DataFrame:
    exploded = movies.withColumn("director", F.explode(F.split("directors", "/")))
    return (
        exploded.groupBy("director")
        .agg(
            F.count("*").alias("movie_count"),
            F.avg("rating_score").alias("avg_rating"),
        )
        .orderBy(F.desc("movie_count"), F.desc("avg_rating"), "director")
        .limit(limit)
    )


# Task A-2: window function, selecting the top three rated movies each year.
def query_yearly_top_three(movies: DataFrame) -> DataFrame:
    ranking = Window.partitionBy("year").orderBy(
        F.desc("rating_score"), F.asc("title")
    )
    return (
        movies.withColumn("rank_in_year", F.row_number().over(ranking))
        .filter(F.col("rank_in_year") <= 3)
        .select("year", "rank_in_year", "title", "rating_score")
        .orderBy("year", "rank_in_year")
    )


# Task A-2: JOIN each movie/genre score with the corresponding genre average.
def query_movie_vs_genre_average(movies: DataFrame) -> DataFrame:
    movie_genres = movies.select(
        "movie_id",
        "title",
        "rating_score",
        F.explode(F.split("genres", "/")).alias("genre"),
    )
    genre_average = movie_genres.groupBy("genre").agg(
        F.avg("rating_score").alias("genre_avg_rating")
    )
    return (
        movie_genres.join(genre_average, on="genre", how="inner")
        .withColumn(
            "difference_from_genre_avg",
            F.col("rating_score") - F.col("genre_avg_rating"),
        )
        .orderBy(F.desc("difference_from_genre_avg"), "title")
    )


def main() -> None:
    args = parse_args()
    spark = SparkSession.builder.appName("DoubanSparkSQLAnalysis").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    movies = load_movies(spark, args.input, args.format).cache()
    print(f"ANALYSIS_INPUT_ROW_COUNT={movies.count()}", flush=True)

    timed_query("1. 类型维度评分分析", "genre_rating", lambda: query_genre_rating(movies))
    timed_query("2. 年份趋势分析", "year_trend", lambda: query_year_trend(movies))
    timed_query(
        "3. 导演 Top-N",
        "director_top_n",
        lambda: query_director_top_n(movies, args.director_limit),
    )
    timed_query(
        "4. 每年评分最高 Top 3（窗口函数）",
        "yearly_top_three",
        lambda: query_yearly_top_three(movies),
    )
    timed_query(
        "5. 电影评分与类型平均评分对比（JOIN）",
        "movie_vs_genre_average",
        lambda: query_movie_vs_genre_average(movies),
    )
    spark.stop()


if __name__ == "__main__":
    main()


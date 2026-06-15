from pyspark.sql import SparkSession


def main() -> None:
    spark = SparkSession.builder.appName("CloudCourseWordCount").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    print("=== WORDCOUNT JOB START ===", flush=True)
    lines = spark.sparkContext.parallelize(
        [
            "hello spark",
            "hello kubernetes",
            "spark on huawei cloud",
        ]
    )
    word_counts = (
        lines.flatMap(lambda line: line.split())
        .map(lambda word: (word.lower(), 1))
        .reduceByKey(lambda left, right: left + right)
        .sortBy(lambda item: (-item[1], item[0]))
    )
    print("WORDCOUNT_RESULT_START", flush=True)
    for word, count in word_counts.collect():
        print(f"{word}\t{count}", flush=True)
    print("WORDCOUNT_RESULT_END", flush=True)
    print("=== WORDCOUNT JOB COMPLETE ===", flush=True)
    spark.stop()


if __name__ == "__main__":
    main()


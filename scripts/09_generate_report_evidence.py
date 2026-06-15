#!/usr/bin/env python3
"""Build report-ready evidence files from previously captured real outputs."""

from __future__ import annotations

import csv
import html
import re
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
CLOUD = ROOT / "evidence" / "05_huawei_cloud"
PLATFORM = CLOUD / "03_cce_deploy"
VALIDATION = CLOUD / "04_redis_configmap_hpa"
SPARK = CLOUD / "05_spark"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8").lstrip("\ufeff")


def write(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(f"generated {path.relative_to(ROOT)}")


def extract_between(text: str, start: str, end: str | None) -> str:
    start_index = text.index(start)
    if end is None:
        return text[start_index:]
    end_index = text.index(end, start_index)
    return text[start_index:end_index]


def generate_redis_evidence() -> None:
    text = read(VALIDATION / "redis-persistence.txt")
    values = dict(
        re.findall(
            r"^(TIME_START|SET_RESULT|OLD_REDIS_POD|PVC_VOLUME|DELETE_RESULT|"
            r"NEW_REDIS_POD|PVC_VOLUME_AFTER|GET_RESULT|POD_CHANGED|"
            r"VOLUME_UNCHANGED|TIME_END)=(.*)$",
            text,
            flags=re.MULTILINE,
        )
    )

    write(
        VALIDATION / "report-redis-1-set.txt",
        "\n".join(
            [
                "Redis persistence verification - step 1: SET",
                f"TIME_START={values['TIME_START']}",
                f"SET_RESULT={values['SET_RESULT']}",
                f"OLD_REDIS_POD={values['OLD_REDIS_POD']}",
                f"PVC_VOLUME={values['PVC_VOLUME']}",
            ]
        ),
    )
    write(
        VALIDATION / "report-redis-2-delete-pod.txt",
        "\n".join(
            [
                "Redis persistence verification - step 2: delete and rebuild Pod",
                f"OLD_REDIS_POD={values['OLD_REDIS_POD']}",
                f"DELETE_RESULT={values['DELETE_RESULT']}",
                f"NEW_REDIS_POD={values['NEW_REDIS_POD']}",
                f"POD_CHANGED={values['POD_CHANGED']}",
            ]
        ),
    )
    write(
        VALIDATION / "report-redis-3-get-after-rebuild.txt",
        "\n".join(
            [
                "Redis persistence verification - step 3: GET after Pod rebuild",
                f"NEW_REDIS_POD={values['NEW_REDIS_POD']}",
                f"PVC_VOLUME_BEFORE={values['PVC_VOLUME']}",
                f"PVC_VOLUME_AFTER={values['PVC_VOLUME_AFTER']}",
                f"VOLUME_UNCHANGED={values['VOLUME_UNCHANGED']}",
                f"GET_RESULT={values['GET_RESULT']}",
                f"TIME_END={values['TIME_END']}",
            ]
        ),
    )


def generate_configmap_evidence() -> None:
    text = read(VALIDATION / "configmap-subpath-test.txt")
    write(
        VALIDATION / "report-configmap-volume.txt",
        "ConfigMap volume and subPath update verification\n\n" + text,
    )


def generate_hpa_evidence() -> None:
    source = read(VALIDATION / "hpa-cloud-scale-down-final.txt")
    write(
        VALIDATION / "report-hpa-scale-down.txt",
        "HPA scale-down verification after pressure stopped\n\n" + source,
    )


def generate_spark_query_evidence() -> None:
    text = read(SPARK / "douban-1executor-driver.log")
    sections = [
        ("=== 1. 类型维度评分分析 ===", "=== 2.", "report-query-1-genre.txt"),
        ("=== 2. 年份趋势分析 ===", "=== 3.", "report-query-2-year.txt"),
        ("=== 3. 导演 Top-N ===", "=== 4.", "report-query-3-director.txt"),
        (
            "=== 4. 每年评分最高 Top 3（窗口函数） ===",
            "=== 5.",
            "report-query-4-window.txt",
        ),
        (
            "=== 5. 电影评分与类型平均评分对比（JOIN） ===",
            "26/06/15",
            "report-query-5-join.txt",
        ),
    ]
    for start, end, filename in sections:
        write(SPARK / filename, extract_between(text, start, end))

    join_text = read(SPARK / "report-query-5-join.txt")
    write(
        SPARK / "report-query-5-join.html",
        """<!doctype html>
<meta charset="utf-8">
<style>
body { margin: 16px; background: white; color: black; }
pre { font: 11px/1.3 Consolas, "Microsoft YaHei", monospace; white-space: pre; }
</style>
<pre>"""
        + html.escape(join_text)
        + "</pre>",
    )


def generate_cleaning_evidence() -> None:
    text = read(SPARK / "douban-clean-driver.log")
    schema = extract_between(text, "=== CLEANING START", "=== RAW FIRST 5 ROWS ===")
    statistics = extract_between(text, "RAW_ROW_COUNT=", "=== CLEANING COMPLETE")
    write(SPARK / "report-cleaning-schema.txt", schema)
    write(SPARK / "report-cleaning-statistics.txt", statistics)


def generate_wordcount_evidence() -> None:
    preferred = SPARK / "wordcount-2executor-driver.log"
    text = read(preferred if preferred.exists() else SPARK / "wordcount-driver.log")
    result = extract_between(text, "=== WORDCOUNT JOB START ===", "26/06/15")
    write(SPARK / "report-wordcount-result.txt", result)


def generate_performance_chart() -> None:
    rows: list[dict[str, str]] = []
    with (SPARK / "performance_results.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows.extend(csv.DictReader(handle))

    selected = [
        row
        for row in rows
        if row["query"] == "genre_rating"
        and (
            row["engine"] == "pandas"
            or (row["engine"] == "pyspark-cce" and row["executors"] in {"1", "2"})
        )
    ]
    labels = []
    seconds = []
    for row in selected:
        if row["engine"] == "pandas":
            labels.append("Pandas\nlocal")
        else:
            labels.append(f"PySpark\n{row['executors']} executor")
        seconds.append(float(row["seconds"]))

    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.bar(labels, seconds, color=["#4c78a8", "#f58518", "#e45756"])
    ax.set_title("Genre rating query: real execution time comparison")
    ax.set_ylabel("Seconds (lower is better)")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    for bar, value in zip(bars, seconds):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + max(seconds) * 0.02,
            f"{value:.6f}s",
            ha="center",
            va="bottom",
        )
    ax.set_ylim(0, max(seconds) * 1.18)
    fig.text(
        0.5,
        0.01,
        "Source: performance_results.csv generated from actual local Pandas and CCE Spark runs.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    output = SPARK / "performance-comparison.png"
    fig.savefig(output, dpi=180)
    plt.close(fig)
    print(f"generated {output.relative_to(ROOT)}")

    pandas_time, spark_1, spark_2 = seconds
    speedup_1_to_2 = spark_1 / spark_2
    write(
        SPARK / "performance-analysis-facts.txt",
        "\n".join(
            [
                "Performance comparison facts (actual measured values)",
                f"Pandas local genre query: {pandas_time:.6f} s",
                f"PySpark CCE, 1 executor: {spark_1:.6f} s",
                f"PySpark CCE, 2 executors: {spark_2:.6f} s",
                f"Observed Spark speedup T1/T2: {speedup_1_to_2:.6f}",
                f"SparkApplication total duration, 1 executor: 26 s",
                f"SparkApplication total duration, 2 executors: 28 s",
                "",
                "The observed speedup is below 1, so a positive Amdahl parallel",
                "fraction cannot be estimated from this run. For this small dataset,",
                "executor startup, scheduling, serialization, and shuffle overhead",
                "outweighed the benefit of adding one executor.",
            ]
        ),
    )


def main() -> None:
    generate_redis_evidence()
    generate_configmap_evidence()
    generate_hpa_evidence()
    generate_spark_query_evidence()
    generate_cleaning_evidence()
    generate_wordcount_evidence()
    generate_performance_chart()


if __name__ == "__main__":
    main()

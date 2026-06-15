# Spark 方向 A 基础代码

本目录只提供明天运行所需的代码和 SparkApplication 骨架，不包含任何虚构统计结果。

已实际读取 `data/douban_movies.csv` 的表头，字段为：

`movie_id,title,original_title,year,rating_score,rating_count,genres,countries,directors,collect_count,summary`

## 本地检查

```bash
python spark/inspect_douban_schema.py
python spark/pandas_baseline.py
```

安装 PySpark 后可运行：

```bash
python spark/clean_douban.py \
  --input data/douban_movies.csv \
  --output data/cleaned/douban_movies

python spark/spark_sql_analysis.py \
  --input data/douban_movies.csv \
  --format csv
```

## OBS/S3A

`clean_douban.py` 和 `spark_sql_analysis.py` 接受 `s3a://` 路径。示例：

```bash
spark-submit spark/clean_douban.py \
  --input s3a://[OBS_BUCKET]/douban_movies.csv \
  --output s3a://[OBS_BUCKET]/outputs/douban-cleaned
```

OBS 的认证方式、S3A connector 与 endpoint 必须按 CCE/Spark 镜像的真实环境配置。不要把 AK、SK 写入代码或 YAML；优先使用华为云推荐的身份机制或临时凭据。

## 性能记录

`performance_compare.py` 只消费真实耗时。可先创建 `timings.csv`：

```csv
engine,executors,query,run,seconds,notes
```

完成 Pandas、1 executor、2 executors 的真实运行后再填写并执行：

```bash
python spark/pandas_baseline.py --timing-output timings-pandas.csv
python spark/performance_compare.py --input timings.csv
```

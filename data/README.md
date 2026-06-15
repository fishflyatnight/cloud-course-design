# 数据目录

`douban_movies.csv` 来自课程设计提供的数据文件。已确认其 UTF-8 表头为：

`movie_id,title,original_title,year,rating_score,rating_count,genres,countries,directors,collect_count,summary`

本目录不存放伪造的清洗结果。`data/cleaned/` 将在真实运行 `spark/clean_douban.py` 后生成，并已加入 `.gitignore`。

后续上传 OBS 时建议保留原始文件名，并把真实路径填写为 `[OBS_DATA_PATH]`，例如 `s3a://实际桶名/douban_movies.csv`。不要在仓库中提交 OBS 访问密钥。


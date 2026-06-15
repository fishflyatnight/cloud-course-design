# 后续真实截图位置

本文件只是截图待办，不是报告模板。截图必须来自真实运行，且应保留命令、资源名、状态、时间或返回值。

| 状态 | 截图位置 | 对应任务 | 证据 |
|---|---|---|---|
| 已有总览，待补 Tag | SWR 镜像列表 | 任务 1 | `02_swr_push/swr-console-image-list.png`；另补版本页中直接可见的 `v1` |
| 已完成 | Docker Compose 联调 | 任务 1 | `evidence/01_local_compose/` |
| 已完成 | `kubectl get nodes -o wide` | 任务 2 | `05_huawei_cloud/03_cce_deploy/report-platform-status.png` |
| 已完成 | Pod、Service、PVC | 任务 3/4 | `05_huawei_cloud/03_cce_deploy/report-platform-status.png` |
| 已完成 | ELB `/api/ping` | 任务 3 | `05_huawei_cloud/03_cce_deploy/cce-elb-api-ping.png` |
| 已完成 | Redis SET/删除/GET | 任务 4 | `05_huawei_cloud/04_redis_configmap_hpa/report-redis-*.png` |
| 已完成 | ConfigMap Volume | 任务 5 | `05_huawei_cloud/04_redis_configmap_hpa/report-configmap-volume.png` |
| 已完成 | HPA 扩容 | 任务 6 | `05_huawei_cloud/04_redis_configmap_hpa/report-hpa-scale-up.png` |
| 已完成 | HPA 缩容 | 任务 6 | `05_huawei_cloud/04_redis_configmap_hpa/report-hpa-scale-down-complete.png` |
| 已完成 | Spark Operator | A-0 | `05_huawei_cloud/05_spark/report-spark-status.png` |
| 已完成 | WordCount Driver/Executor | A-0 | `report-wordcount-driver-executors-running.png`、`report-wordcount-completed.png` |
| 已完成 | 数据清洗输出 | A-1 | `report-cleaning-schema.png`、`report-cleaning-statistics.png` |
| 已完成 | Spark SQL 查询 | A-2 | `report-query-1-genre.png` 至 `report-query-5-join.png` |
| 已完成 | 性能对比 | A-3 | `performance-comparison.png` |

截图前先避免把 `.env`、Token、AK/SK、KubeConfig 或 Secret 明文放入终端画面。

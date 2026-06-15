# 云计算技术课程设计工程

本地预验证和主要华为云实验已于 2026-06-15 真实完成。当前状态见
[`docs/00_current_status.md`](docs/00_current_status.md)，报告材料从
[`evidence/05_huawei_cloud/REPORT_MATERIAL_INDEX.md`](evidence/05_huawei_cloud/REPORT_MATERIAL_INDEX.md)
进入。

这是《云计算技术》课程设计的前期环境与工程准备，路线为：

1. 华为云 CCE：Flask API + Redis + Nginx，配合 SWR、ELB、PVC、ConfigMap Volume 与 HPA。
2. 方向 A：使用 `douban_movies.csv` 完成 PySpark 清洗、Spark SQL 和 Pandas/PySpark 性能对比。

当前工程已经包含 CCE、SWR 推送、ELB、PVC、ConfigMap、HPA 和 Spark 的真实运行材料。
尚未生成课程设计报告正文和老师验收问答。

## 已准备内容

- Flask 的 `/api/ping`、Redis 写入/读取接口及后端访问日志。
- Nginx 静态页、反向代理、Dockerfile 与三服务 `docker-compose.yml`。
- CCE/Kubernetes 的 Namespace、ConfigMap、Secret、PVC、Deployment、Service、HPA。
- SWR 构建/推送、K8s 部署/验证、Redis 持久化、HPA 压测和清理脚本。
- Spark 清洗、5 项 SQL 查询、Pandas 基线、性能记录框架及 SparkApplication。
- 明日操作顺序、环境检查、占位符说明、命令清单、截图待办和故障排查。

## 继续推进

先打开 [`docs/06_huawei_cloud_handoff.md`](docs/06_huawei_cloud_handoff.md)。自动化主实验已经完成，
不要重复创建 CCE、ELB 或 PVC。当前主要剩余事项是 SWR 控制台截图、按教师要求确认 OBS、
发布代码仓库，以及之后基于真实证据生成报告。

## 本地构建提醒

华为云 SWR 可能无法解析带 provenance/OCI 附件的 manifest。手动构建与脚本均应使用：

```bash
docker build --provenance=false ...
```

可运行：

```bash
bash scripts/01_prepare_env.sh
bash scripts/00_check_prerequisites.sh
bash scripts/02_build_images.sh
```

`docker compose up --build` 适合本地联调，但若随后要推送 SWR，仍建议用 `scripts/02_build_images.sh` 重新以 `--provenance=false` 构建。

## 密钥规则

- `.env` 已被 `.gitignore` 忽略。
- 不要把 AK、SK、SWR 临时 Token、Redis 真密码或 KubeConfig 写进代码、YAML、截图或 Git。
- `k8s/01-configmap-secret.yaml` 当前只含占位符的 base64，不是可用密码。
- 推送和部署前必须人工确认当前 Region、镜像地址和 kubectl context。

## 数据字段

已实际读取提供的 CSV 表头：

`movie_id,title,original_title,year,rating_score,rating_count,genres,countries,directors,collect_count,summary`

代码只会在真实运行时计算缺失值、统计量和耗时，不包含预设结果。已运行结果保存在
`evidence/05_huawei_cloud/`，可用 `python scripts/09_generate_report_evidence.py`
从原始日志重新生成报告用分项材料。

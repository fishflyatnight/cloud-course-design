# 当前状态

截至 2026-06-15，课程设计工程已经完成本地预验证和主要华为云实跑。

## 华为云已完成

- CCE 集群 `cloud-course-cce` 已通过公网 KubeConfig 连接。
- 两个 Worker 节点均为 `Ready`，Kubernetes 为 `v1.35.3-r0-35.0.8`。
- Metrics Server 已安装，`kubectl top nodes/pods` 可返回真实指标。
- Backend、Frontend、Spark、Redis 和 Spark Operator 镜像已推送到 `cn-north-4` 的 SWR。
- Flask Backend、Nginx Frontend、Redis 已在 CCE 运行。
- Backend 已通过公网 ELB `123.249.121.136` 暴露，`/api/ping` 和 Redis API 已验证。
- Redis PVC 为 `csi-disk`、`10Gi`、`Bound`。
- Redis Pod 删除重建后，测试键和值仍存在。
- ConfigMap `subPath` 不热更新和删除 Pod 后更新的行为已验证。
- HPA 已真实完成 1 到 4 的扩容和 4 到 1 的缩容。
- Spark Operator Controller/Webhook 均运行正常。
- WordCount 已按任务书以 2 个 `1g` Executor 重跑并完成，运行时 Driver 和两个 Executor 均已留证。
- Douban 清洗、1 executor SQL、2 executors SQL 均为 `COMPLETED`。
- 真实日志、命令输出和截图保存在 `evidence/05_huawei_cloud/`。
- Redis 三步验证、ConfigMap、HPA 扩缩容、清洗结果、5 个查询和性能图均已生成报告用 PNG。

## 真实数据摘要

- Douban 原始行数：67132。
- 清洗后行数：61853。
- 删除关键字段缺失行数：5279。
- 1 executor SparkApplication 总耗时：26 秒。
- 2 executors SparkApplication 总耗时：28 秒。
- 当前小数据集上，2 executors 未快于 1 executor，属于真实调度开销结果。

## 尚未完成

- 教师暂未提供 `s3a://` OBS 数据路径；本次豆瓣分析基于随课程设计提供的本地
  `data/douban_movies.csv` 完成，Spark 云端运行时使用镜像内同一份数据文件。
- 尚未把清洗结果持久化到 OBS。
- 已保存 SWR 控制台镜像列表总览；仍建议补一张版本详情页截图，使 Tag `v1` 直接可见。
- 尚未发布 GitHub/Gitee 代码仓库。
- 尚未生成课程设计报告正文。
- 尚未生成老师验收问答。

报告阶段应从 `evidence/05_huawei_cloud/REPORT_MATERIAL_INDEX.md` 选取真实材料，不得修改或伪造结果。

# 附加题真实材料索引

本目录仅保存实际部署、实际运行和实际查询所得材料，不包含伪造输出。

## 附加题 1：Prometheus 与 Grafana

- `01_monitoring/monitoring-stack-summary.png`：监控组件在 CCE 中运行的终端证据。
- `01_monitoring/grafana-dashboard-node-cpu-pod-memory.png`：Grafana 节点 CPU 折线图与 Pod 内存柱状图。
- `01_monitoring/prometheus-query-validation.json`：Prometheus 查询接口返回的指标序列验证。
- `01_monitoring/helm-install-nohooks.txt`：kube-prometheus-stack 安装输出。

## 附加题 2：CI/CD

- `02_cicd/github-actions-all-passed.png`：GitHub Actions 全流程成功页面。
- `02_cicd/deployment-images-after-cicd.png`：CCE Deployment 更新后的镜像 Tag。
- `02_cicd/workflow-success-summary.txt`：工作流、提交和执行结果摘要。
- `02_cicd/workflow-run.json`、`workflow-jobs.json`：GitHub API 返回的真实运行元数据。

## 附加题 3：PyTorch DDP

- `03_distributed_ai/local-smoke-test.txt`：镜像内训练程序的本地小规模冒烟测试。
- `03_distributed_ai/single-result.txt`：CCE 单 Worker 训练日志。
- `03_distributed_ai/ddp-rank0-result.txt`、`ddp-rank1-result.txt`：CCE 两个 Worker 的 DDP 日志。
- `03_distributed_ai/ddp-pods-and-results.png`：两个 Worker Pod、节点分布和训练结果。
- `03_distributed_ai/performance-comparison.png`：单 Worker 与双 Worker 真实耗时对比。
- `03_distributed_ai/performance-results.csv`：用于绘图和报告的数据。

SWR 临时密码、KubeConfig、GitHub Token、Grafana 管理员密码均不进入本目录和 Git。

# 明天从这里开始

> 状态更新（2026-06-15）：本文保留为完整操作流程记录，其中主要本地与华为云步骤已经完成。
> 当前继续入口请改看 `docs/06_huawei_cloud_handoff.md`，不要重复创建收费资源。

以下流程用于 2026-06-12 的第一轮推进。每一步都只在前一步真实成功后继续。

## 1. 检查工程目录

- 在哪里做：本机终端，进入 `cloud-course-design/`。
- 要做什么：确认 `backend/`、`frontend/`、`k8s/`、`scripts/`、`spark/`、`docs/`、`data/` 都存在。
- 执行命令：`find . -maxdepth 2 -type f | sort`，PowerShell 可用 `Get-ChildItem -Recurse -File`。
- 成功应看到：本工程清单中的文件和 `data/douban_movies.csv`。
- 失败先看：`README.md`，确认当前目录是否正确。

## 2. 填写 `.env`

- 在哪里做：工程根目录。
- 要做什么：从示例创建 `.env`，先填非敏感身份、Region、组织、镜像和 Redis 密码；临时 Token 在推送前再填。
- 执行命令：`bash scripts/01_prepare_env.sh`，然后编辑 `.env`。
- 成功应看到：`.env` 存在且关键值不再是方括号占位符。
- 失败先看：`docs/03_huawei_cloud_placeholders.md`。

## 3. 替换首页学号姓名

- 在哪里做：`frontend/index.html`。
- 要做什么：替换 `[STUDENT_ID]` 与 `[STUDENT_NAME]`。
- 执行命令：`grep -nE '\[STUDENT_(ID|NAME)\]' frontend/index.html`。
- 成功应看到：搜索无结果，页面显示真实学号姓名。
- 失败先看：`README.md` 的“第一批必须替换”。

## 4. 检查 Docker 等工具

- 在哪里做：本机、Git Bash、WSL 或准备构建镜像的 ECS。
- 要做什么：只检查 Docker、Compose、kubectl、Helm、Python、Git。
- 执行命令：`bash scripts/00_check_prerequisites.sh`。
- 成功应看到：所需命令显示 `[OK]`；Docker 还需执行 `docker info` 验证 daemon。
- 失败先看：`docs/02_environment_setup.md`。

## 5. 选择本机构建或 ECS 构建

- 在哪里做：根据本机 Docker 与网络情况决定。
- 要做什么：能稳定运行 Docker 就本机构建；若 Docker Desktop/网络持续不可用，可在同 Region 的华为云 ECS 构建。
- 执行命令：本机和候选 ECS 分别执行 `docker info`、`docker pull python:3.11-slim`。
- 成功应看到：选定环境能访问 Docker daemon，并能获取基础镜像或加载离线镜像。
- 失败先看：`docs/troubleshooting.md` 的“Docker Compose 拉取镜像超时”。

## 6. 构建镜像

- 在哪里做：第 5 步选定的构建环境。
- 要做什么：构建 backend、frontend、spark 本地镜像，使用 SWR 兼容参数。
- 执行命令：`bash scripts/02_build_images.sh`。
- 成功应看到：`docker images` 中有 `cloud-course-backend:local`、`cloud-course-frontend:local`、`cloud-course-spark:local`。
- 失败先看：`docs/troubleshooting.md` 的网络超时和 manifest 小节。

## 7. 创建 SWR 组织

- 在哪里做：华为云控制台，确保 Region 与后续 CCE 一致。
- 要做什么：创建或确认 `[SWR_ORG]`，记录控制台给出的登录命令格式。
- 执行命令：控制台操作；本地只需核对 `.env` 中 `REGION`、`SWR_ORG`。
- 成功应看到：SWR 组织页面存在，能进入镜像仓库页面。
- 失败先看：`docs/03_huawei_cloud_placeholders.md` 和华为云控制台提示。

## 8. 推送镜像到 SWR

- 在哪里做：已构建镜像的环境。
- 要做什么：从 SWR“登录指令”获取当前临时登录密码/Token，填写 `.env` 后推送。
- 执行命令：`bash scripts/03_push_to_swr.sh`。
- 成功应看到：三个 `docker push` 完成，并能在 SWR 控制台看到正确仓库与 Tag。
- 失败先看：`docs/troubleshooting.md` 的 manifest、认证、跨 Region 小节。

## 9. 创建 CCE 集群

- 在哪里做：华为云 CCE 控制台。
- 要做什么：按任务书创建 Kubernetes `>=1.27`、Yangtse CNI、2 个 Worker 的集群；资源不足时再评估增加 2 vCPU/8 GiB 节点。
- 执行命令：控制台操作，不由本工程脚本创建。
- 成功应看到：集群可用，两个 Worker 节点正常。
- 失败先看：`docs/troubleshooting.md` 的资源不足小节。

## 10. 配置 kubeconfig 或 CloudShell

- 在哪里做：CCE 控制台下载 KubeConfig 后在本机，或直接使用 CloudShell。
- 要做什么：让 kubectl 指向刚创建的 CCE，避免误操作旧 minikube。
- 执行命令：`export KUBECONFIG="[KUBECONFIG_PATH]"`、`kubectl config current-context`、`kubectl get nodes -o wide`。
- 成功应看到：CCE Worker 为 `Ready`，`VERSION` 至少 1.27。
- 失败先看：`docs/02_environment_setup.md` 和 `kubectl config get-contexts`。

## 11. 替换 Kubernetes 镜像与 Secret

- 在哪里做：`k8s/`。
- 要做什么：替换 backend/frontend 镜像；把真实 Redis 密码编码后替换 Secret data。
- 执行命令：`printf '%s' '真实密码' | base64`，再执行 `grep -R -nE '\[[A-Z0-9_]+\]' k8s`。
- 成功应看到：`k8s/` 不再含 SWR 镜像占位符，Secret 中只有 base64。
- 失败先看：`docs/03_huawei_cloud_placeholders.md`。

## 12. 部署 Kubernetes 资源

- 在哪里做：kubectl 已连接 CCE 的终端。
- 要做什么：按文件编号顺序 apply，不创建集群。
- 执行命令：`bash scripts/04_deploy_k8s.sh`。
- 成功应看到：各资源显示 `created` 或 `configured`。
- 失败先看：`kubectl describe` 事件和 `docs/troubleshooting.md`。

## 13. 验证 Pod、Service、PVC

- 在哪里做：同一 kubectl 终端。
- 要做什么：查看节点、Pod、Service、PVC、HPA、metrics。
- 执行命令：`bash scripts/05_verify_k8s.sh`。
- 成功应看到：Pod 最终 `Running`、PVC `Bound`、LoadBalancer 获得地址；`kubectl top nodes` 有数据。
- 失败先看：`docs/troubleshooting.md` 的 Pending、ImagePullBackOff、metrics 小节。

## 14. 测试 `/api/ping`

- 在哪里做：能访问 ELB 公网 IP 的终端或浏览器。
- 要做什么：访问后端 LoadBalancer，并检查 backend 日志。
- 执行命令：`curl "http://[ELB_IP]/api/ping"`、`kubectl logs -n cloud-course -l app=backend --tail=100`。
- 成功应看到：真实响应 `{"status":"ok"}`，日志出现 `/api/ping` 请求。
- 失败先看：`kubectl describe svc backend-svc -n cloud-course` 和 Pod 日志。

## 15. 测试 Redis 持久化

- 在哪里做：kubectl 终端，确认 PVC 已 `Bound`。
- 要做什么：写入、删除 Redis Pod、等待重建、读取。
- 执行命令：先 `bash scripts/06_test_redis_persistence.sh` 预览，再运行 `bash scripts/06_test_redis_persistence.sh --execute`。
- 成功应看到：重建后的真实 `GET testkey` 返回 `hello`。
- 失败先看：`kubectl describe pvc redis-data-pvc -n cloud-course` 和 Redis Pod 日志。

## 16. 测试 ConfigMap Volume

- 在哪里做：`k8s/07-nginx-configmap.yaml` 与 kubectl 终端。
- 要做什么：临时将 upstream 端口 `80` 改为 `81`，apply 后删除 frontend Pod 重建，再进入 Pod 查看文件；验证后恢复 `80`。
- 执行命令：`kubectl apply -f k8s/07-nginx-configmap.yaml`、`kubectl delete pod -n cloud-course -l app=frontend`、`kubectl exec -n cloud-course deploy/frontend -- cat /etc/nginx/conf.d/default.conf`。
- 成功应看到：重建 Pod 内文件反映真实修改；恢复端口并再次重建后代理正常。
- 失败先看：`docs/troubleshooting.md` 的 ConfigMap `subPath` 小节。

## 17. 测试 HPA

- 在哪里做：两个终端；一个观察 HPA/Pod，一个执行压测。
- 要做什么：先确认 metrics，并等待 HPA 将空闲 backend 稳定到 1 个副本，再持续请求约 2 分钟，观察扩容和停止后的缩容。
- 执行命令：观察端 `kubectl get hpa,pods -n cloud-course -w`；压测端 `python scripts/07_hpa_pressure_test.py --url "http://[ELB_IP]/api/ping" --requests 10000 --concurrency 200`。
- 成功应看到：真实 Pod 数从 1 增加到 2 或更多，停止后等待稳定窗口再回落。
- 失败先看：`kubectl describe hpa backend-hpa -n cloud-course` 和 `docs/troubleshooting.md` 的 HPA 小节。

## 18. 开始 Spark Operator 与 Douban 分析

- 在哪里做：有 Docker、Helm、kubectl 且连接 CCE 的终端。
- 要做什么：加载教师离线镜像、推送到同 Region SWR、安装离线 Spark Operator Chart、替换 Spark YAML 占位符，再按 WordCount、1 executor、2 executors 顺序提交。
- 执行命令：先阅读并运行 `bash scripts/08_spark_submit_notes.sh`，然后按其中命令操作。
- 成功应看到：Operator Pod Running，WordCount Driver Completed，Douban Driver 日志打印真实 Schema、查询和耗时。
- 失败先看：`docs/troubleshooting.md` 的 Spark Operator 与 executor 资源小节，以及 `spark/README.md`。

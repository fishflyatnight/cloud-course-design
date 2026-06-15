# 常见问题排查

## minikube 导入大镜像后卡住或出现 `exec format error`

本地预验证曾遇到 `minikube image load` 导入 Spark/Operator 大镜像时返回 `unexpected EOF`，以及节点内旧镜像启动时报 `exec format error`。宿主机同一镜像可正常运行时，优先绕过 minikube 缓存，直接导入节点：

```bash
docker save cloud-course-spark:local | docker exec -i minikube docker load
docker save ghcr.io/kubeflow/spark-operator/controller:2.5.0 | \
  docker exec -i minikube docker load
```

如果节点仍使用旧镜像，先删除相关临时 Deployment，再删除节点内旧标签并重新导入。该问题只属于本地 minikube 预验证；CCE 应优先从同 Region SWR 拉取镜像，不应使用 `minikube image load`。

内容依据课程提供的《课设问题合集》整理，并结合当前工程路径适配。先用 `describe`、`logs`、`events` 获取真实原因，再选择处理方式。

## Docker Compose 拉取镜像超时

现象：`docker compose up --build` 或 Dockerfile 第一行拉取基础镜像超时。

先查：

```bash
docker info
docker pull python:3.11-slim
docker pull redis:7-alpine
```

国内网络可能无法稳定访问 Docker Hub。可在 Docker Desktop 的 Docker Engine 配置可用镜像源并重启，或在华为云同 Region ECS 构建。镜像源可用性会变化，不能把问题合集中的地址视为永久有效。教师 PySpark/Spark Operator 大镜像优先使用离线 tar。

## SWR 报 `Invalid image, fail to parse manifest.json`

课程问题合集记录的原因是较新 Docker 默认生成的 OCI/provenance manifest 与 SWR 解析不兼容。

重新构建，不要只重新 push：

```bash
docker build --provenance=false -f backend/Dockerfile.backend \
  -t cloud-course-backend:local backend
```

三个镜像都由 `scripts/02_build_images.sh` 使用 `--provenance=false` 构建。随后重新 tag、push，并确认推送的是新镜像。

## CCE Pod Pending：`Insufficient memory` / `Insufficient cpu`

调度器看 `resources.requests`，不是 `kubectl top` 的实时使用率。

```bash
kubectl describe pod <pod> -n <namespace>
kubectl describe node <node>
kubectl top nodes
```

先降低不必要的 requests、减少临时副本或停止暂不用的工作负载。问题合集显示 2 vCPU/4 GiB 节点的可调度资源可能明显少于标称值；仍不足时再增加 2 vCPU/8 GiB Worker，避免盲目花费代金券。

## `ImagePullBackOff`

```bash
kubectl describe pod <pod> -n <namespace>
kubectl get events -n <namespace> --sort-by=.lastTimestamp
```

检查：

- 镜像地址和 Tag 是否真实存在。
- CCE 与 SWR 是否同 Region。
- SWR 仓库是否允许集群拉取。
- 私有仓库是否需要 `imagePullSecret`。
- 节点是否能访问 Docker Hub/GHCR。

如使用私有 SWR，可按控制台真实参数创建 Secret，不要把命令写入 Git：

```bash
kubectl create secret docker-registry swr-secret \
  --docker-server=swr.[REGION].myhuaweicloud.com \
  --docker-username='[REGION]@[SWR_AK]' \
  --docker-password='[SWR_LOGIN_PASSWORD]' \
  -n cloud-course
```

然后在 Pod spec 中添加 `imagePullSecrets`。

## 跨 Region 拉取 SWR 镜像失败

优先做法是让 CCE、SWR、OBS 位于同一 Region，并把镜像重新推送到该 Region 的 SWR 组织。跨 Region 私有拉取通常还需要认证与网络可达性，容易产生 `401 Unauthorized` 或 `ImagePullBackOff`。

不要仅修改镜像域名；必须确认目标 Region 仓库里确实存在对应 manifest 和 Tag。

## ConfigMap `subPath` 不热更新

Kubernetes 的已知行为：以 `subPath` 挂载单文件时，ConfigMap 更新不会自动传播到已有 Pod。

```bash
kubectl apply -f k8s/07-nginx-configmap.yaml
kubectl delete pod -n cloud-course -l app=frontend
kubectl exec -n cloud-course deploy/frontend -- \
  cat /etc/nginx/conf.d/default.conf
```

必须检查重建后的 Pod。任务验证完成后恢复正确 upstream 端口并再次重建。

## Spark Operator 的 `ghcr.io` 镜像拉取失败

教师离线包已包含：

- `spark/spark-operator-2.5.0.tar`
- `spark/spark-operator/` Chart

先 `docker load`，确认真实原始 Tag，再推送到同 Region SWR。当前离线 tar 已识别原始 controller Tag 为：

`ghcr.io/kubeflow/spark-operator/controller:2.5.0`

该 Chart 的实际 values 使用顶层 `image.registry`、`image.repository`、`image.tag`，安装前执行：

```bash
helm show values <OFFLINE_RESOURCE_ROOT>/spark/spark-operator/
```

不要直接照搬与该 Chart 版本不匹配的 `controller.image.*` 参数。

## Spark executor 因资源请求过高 Pending

问题合集中的典型情况是节点只剩约 195m 可请求 CPU，而 executor 默认请求 1 CPU。

本工程 YAML 使用：

```yaml
executor:
  cores: 1
  coreRequest: "100m"
  memory: "512m"
  memoryOverhead: "128m"
```

`cores` 是 Spark 逻辑核心，`coreRequest` 是 Kubernetes 调度预留。先提交 1 executor，确认资源后再提交 2 executors：

```bash
kubectl describe pod <executor-pod>
kubectl describe node <node>
```

## `kubectl top nodes` 没数据

CCE metrics-server 可能需要等待几分钟。先执行：

```bash
kubectl top nodes
kubectl get apiservice | grep metrics
kubectl get pods -A | grep metrics
```

若持续不可用，查看 metrics 组件 Pod 日志和 APIService 状态。HPA 依赖资源 metrics，没有数据时不要开始扩容验收。

## HPA 不扩容

依次检查：

```bash
kubectl get hpa -n cloud-course
kubectl describe hpa backend-hpa -n cloud-course
kubectl top pods -n cloud-course
kubectl get deployment backend -n cloud-course -o yaml
```

常见原因：

- metrics-server 尚无数据。
- backend 没有 `resources.requests.cpu`，导致 CPU 利用率无法计算。
- 压测时间太短或请求没有真正到达 backend。
- ELB/Service 地址错误，压测产生的全是失败请求。
- 当前负载未超过目标 60%。
- 扩缩容存在采集、评估和稳定窗口延迟。

用 backend 日志确认 `/api/ping` 请求确实到达，再观察 `kubectl get hpa,pods -w`。不要为了截图伪造扩容状态；若真实环境未触发，保留 `describe hpa` 的真实排查信息。

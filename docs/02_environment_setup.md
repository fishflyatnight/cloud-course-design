# 环境准备说明

今晚不要求把所有环境安装成功。2026-06-12 开始时先运行 `scripts/00_check_prerequisites.sh`。

## 工具作用

| 工具 | 用途 |
|---|---|
| Docker | 构建、运行和推送 backend/frontend/spark 镜像 |
| Docker Compose | 本地联调 Redis、Flask、Nginx |
| kubectl | 连接 CCE，部署和检查 Kubernetes 资源 |
| Helm | 从教师离线 Chart 安装 Spark Operator |
| Python 3 | 本地数据检查、Pandas 基线和 HPA 压测 |
| Git | 保存工程代码；不得提交密钥 |

## 版本检查

macOS/Linux/WSL/Git Bash：

```bash
docker --version
docker compose version
kubectl version --client
helm version
python3 --version
git --version
```

Windows PowerShell：

```powershell
docker --version
docker compose version
kubectl version --client
helm version
python --version
git --version
```

旧作业目录 `D:\ygl\cloud calculation` 中已有 `tools\kubectl.exe`、`minikube.exe` 和 Docker Desktop 安装材料。使用前仍要执行版本检查，并确认 `kubectl config current-context` 指向 CCE 而不是旧 minikube。

## Docker

优先使用 Docker Desktop 或稳定的 Linux Docker Engine。`docker --version` 成功不代表 daemon 可用，还要执行：

```bash
docker info
docker compose version
```

网络受限时先看 `troubleshooting.md`，不要反复执行大镜像拉取占满磁盘。

## kubectl

kubectl 客户端应与 CCE 版本大致兼容。下载 KubeConfig 后只在本机安全位置保存：

```bash
export KUBECONFIG="[KUBECONFIG_PATH]"
kubectl config current-context
kubectl get nodes -o wide
```

不要把 KubeConfig 放进工程目录或 Git。

## Helm 压缩包与离线 Chart

当前资料已识别出两类不同资源：

1. `../helm-v4.2.0-linux-amd64(2)/linux-amd64/helm` 是 Linux amd64 的 Helm 客户端二进制，不是 Windows `.exe`。已在 WSL 中实际执行 `helm version`，版本为 `v4.2.0`，内置 KubeClient 为 `v1.36`。
2. 教师 2.6G 资源包中另有真实 Spark Operator 2.5.0 Chart：`离线包/spark/spark-operator/`。

若拿到原始 `helm-v4.2.0-linux-amd64.tar.gz`，在 Linux/WSL 解压和检查：

```bash
tar -xzf helm-v4.2.0-linux-amd64.tar.gz
chmod +x linux-amd64/helm
./linux-amd64/helm version
mkdir -p "$HOME/.local/bin"
cp linux-amd64/helm "$HOME/.local/bin/helm"
export PATH="$HOME/.local/bin:$PATH"
helm version
```

当前目录已是解压状态，可从 `chmod +x` 开始。Windows 原生 PowerShell 不能直接运行 Linux ELF；可在 WSL/Linux 使用，或另行安装 Windows 版 Helm。

课程资料和 CCE 的实际兼容性仍需明天验证。Helm v4.2.0 的内置 Kubernetes client 明显新于课程要求的 CCE 1.27，如 `helm lint`、`helm template` 或安装出现兼容问题，改用稳定的 Helm 3 客户端。不要仅凭文件名假设 Spark Operator 已安装成功。

安装前可离线检查：

```bash
helm lint "<离线包路径>/spark/spark-operator"
helm template spark-op "<离线包路径>/spark/spark-operator" \
  -n spark-operator --set spark.serviceAccount.name=spark
```

## Python

本地轻量脚本使用 Python 3。建议单独虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r spark/requirements.txt
```

Windows Git Bash 的激活路径通常为 `source .venv/Scripts/activate`。PySpark 还需要兼容 Java；只运行 `inspect_douban_schema.py`、`pandas_baseline.py` 和 HPA 压测时不需要本地 Spark/Java。

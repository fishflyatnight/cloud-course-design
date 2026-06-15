# 华为云与个人占位符

| 占位符 | 含义与来源 | 主要填写位置 | 敏感 | 可提交 Git |
|---|---|---|---|---|
| `[STUDENT_ID]` | 本人学号 | `.env`、`frontend/index.html` | 个人信息 | 课程要求时可提交 |
| `[STUDENT_NAME]` | 本人姓名 | `.env`、`frontend/index.html` | 个人信息 | 课程要求时可提交 |
| `[REGION]` | CCE/SWR/OBS 所在 Region，来自各服务控制台顶部区域 | `.env`、镜像地址、Spark 安装命令 | 否 | 可以 |
| `[SWR_ORG]` | SWR 控制台的组织名 | `.env`、SWR 镜像地址 | 否 | 可以 |
| `[SWR_AK]` | IAM“访问密钥”或 SWR 登录命令中的用户名部分 | 仅本地 `.env` | 是 | 不可以 |
| `[SWR_SK]` | IAM 永久 SK；不一定等于 SWR 登录密码 | 仅本地 `.env`，尽量不用 | 是 | 不可以 |
| `[SWR_LOGIN_PASSWORD]` | SWR 控制台“登录指令”中的当前临时密码/Token | 仅本地 `.env` | 是 | 不可以 |
| `[SWR_IMAGE_BACKEND]` | SWR backend 完整地址和 Tag | `.env`、`k8s/05-backend-deployment.yaml` | 否 | 可以 |
| `[SWR_IMAGE_FRONTEND]` | SWR frontend 完整地址和 Tag | `.env`、`k8s/08-frontend-deployment.yaml` | 否 | 可以 |
| `[SWR_IMAGE_SPARK]` | SWR PySpark 完整地址和 Tag | `.env`、`spark/*.yaml` | 否 | 可以 |
| `[CCE_CLUSTER_NAME]` | CCE 控制台集群名称 | `.env`、个人操作记录 | 否 | 可以 |
| `[KUBECONFIG_PATH]` | CCE 控制台下载文件在本机的路径 | 仅本地 `.env`/shell 环境 | 路径本身一般否，文件内容是 | 路径可不提交，文件绝不提交 |
| `[OBS_BUCKET]` | OBS 控制台桶名 | `.env`、Spark 命令 | 通常否 | 可提交，公开仓库需考虑隐私 |
| `[OBS_DATA_PATH]` | OBS 中数据对象的完整 `s3a://` 路径 | `.env`、Douban SparkApplication | 通常否 | 可提交，不能带签名参数 |
| `[ELB_IP]` | CCE LoadBalancer Service/ELB 控制台分配的公网 IP | `.env`、curl/压测命令 | 否 | 可提交但资源释放后会失效 |
| `[REDIS_PASSWORD]` | 自行生成的 Redis 密码 | 仅本地 `.env`；YAML 中仅放 base64/Secret | 是 | 不可以 |

Git Bash 中的 `[KUBECONFIG_PATH]` 建议使用 `D:/path/to/kubeconfig` 或 `/d/path/to/kubeconfig` 形式，避免反斜杠被 shell 当作转义字符。

## 镜像地址格式

通常形如：

```text
swr.[REGION].myhuaweicloud.com/[SWR_ORG]/backend:v1
swr.[REGION].myhuaweicloud.com/[SWR_ORG]/frontend:v1
swr.[REGION].myhuaweicloud.com/[SWR_ORG]/pyspark:v1
```

以 SWR 控制台实际“客户端上传”命令为准，并让 CCE 与 SWR 保持同 Region。

## Secret 编码

base64 是编码，不是加密。只在部署前生成：

```bash
printf '%s' '真实Redis密码' | base64
```

把输出写入 `k8s/01-configmap-secret.yaml` 的 `data.password`。仓库提交前应恢复占位符，真实 Secret 另行安全保存。

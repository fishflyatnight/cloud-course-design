# 后续推进接力

主要华为云实验已经完成。本文件只列剩余操作，避免重复创建收费资源。

## 已确认环境

- Region：`cn-north-4`
- CCE：`cloud-course-cce`
- Worker：2 个，均为 Ready
- SWR 组织：`cloud_course`
- ELB：已分配并验证
- Metrics Server：已工作

敏感信息不要发到聊天中，也不要写入 Git：

- 不发送 AK、SK、SWR 登录密码或临时 Token。
- 不粘贴私钥正文。
- 只提供私钥文件路径，由本机 SSH 客户端读取。
- KubeConfig 保存在工程外或受忽略的本地路径。

## 每次继续前的确认

```bash
kubectl config current-context
kubectl get nodes -o wide
```

必须确认输出是目标 CCE，不是 `minikube`。

## 剩余操作

1. SWR 镜像列表总览已经保存。再进入镜像版本详情页，补一张直接显示 Tag `v1` 的截图。
2. 教师暂未提供 OBS `s3a://` 路径；当前分析使用本地 `douban_movies.csv`。
   若教师后续强制指定 OBS，只需补充桶名和对象路径，不需要提供 AK/SK。
3. 本地 Git 仓库已经初始化；待选择 GitHub/Gitee 并登录后再创建远端、提交和推送。
   发布前先检查 `.env`、KubeConfig、Token、Secret 明文均未进入暂存区。
4. 基于 `evidence/05_huawei_cloud/REPORT_MATERIAL_INDEX.md` 生成最终报告。
5. 报告和截图确认完成后，再执行清理并手动释放 ELB、CCE 节点、磁盘和 OBS 等收费资源。

## 已有本地镜像

```text
cloud-course-backend:local
cloud-course-frontend:local
cloud-course-spark:local
ghcr.io/kubeflow/spark-operator/controller:2.5.0
```

这些镜像已经推送完成。除非修改代码或 Tag，不需要再次推送。

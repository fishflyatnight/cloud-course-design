#!/usr/bin/env bash
set -u

cat <<'EOF'
These are notes for tomorrow, not proof that Spark is installed or running.

1. Load and retag the teacher-provided offline images if external registries fail:

   docker load -i <OFFLINE_RESOURCE_ROOT>/spark/spark-operator-2.5.0.tar
   docker load -i <OFFLINE_RESOURCE_ROOT>/spark/pyspark-v9.tar
   docker tag ghcr.io/kubeflow/spark-operator/controller:2.5.0 \
     swr.[REGION].myhuaweicloud.com/[SWR_ORG]/spark-operator:2.5.0

2. Install the provided Spark Operator 2.5.0 chart from its local directory.
   Inspect values first because this chart uses top-level image.* values:

   helm show values <OFFLINE_RESOURCE_ROOT>/spark/spark-operator/
   helm upgrade --install spark-op <OFFLINE_RESOURCE_ROOT>/spark/spark-operator/ \
     -n spark-operator --create-namespace \
     --set image.registry=swr.[REGION].myhuaweicloud.com \
     --set image.repository=[SWR_ORG]/spark-operator \
     --set image.tag=2.5.0 \
     --set spark.serviceAccount.name=spark

3. Check the operator and CRD:

   helm list -n spark-operator
   kubectl get pods -n spark-operator
   kubectl get crd | grep sparkapplications

4. Submit and inspect SparkApplication resources:

   kubectl apply -f spark/sparkapplication-wordcount.yaml
   kubectl get sparkapplications
   kubectl get pods -w
   kubectl describe sparkapplication spark-wordcount

5. Read real driver/executor logs:

   DRIVER_POD=$(kubectl get pods -l spark-role=driver -o jsonpath='{.items[0].metadata.name}')
   kubectl logs "$DRIVER_POD"
   kubectl get pods -l spark-role=executor

6. For the Douban jobs:

   kubectl apply -f spark/sparkapplication-douban-1executor.yaml
   kubectl apply -f spark/sparkapplication-douban-2executor.yaml

Do not record sample text in this note as a result. Only actual kubectl output and
driver logs from your cluster count as evidence.
EOF


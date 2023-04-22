#!/bin/bash

source ~/.bashrc

spark-submit \
    --master $SPARK_MASTER \
    --conf spark.executor.cores=1               \
    --conf spark.executor.memory=512m           \
    $@

# - "spark.executor.instances=5"
# - "spark.executor.memory=48g"
# - "spark.executor.cores=15"
# - "spark.default.parallelism=150"
# - "spark.driver.memory=48g"
# - "spark.driver.cores=15"
# - "spark.yarn.executor.memoryOverhead=8192"
# - "spark.yarn.driver.memoryOverhead=8192"
# - "spark.dynamicAllocation.enabled=false"
# - "spark.executor.extraJavaOptions=-Xss512m"
# - "spark.driver.extraJavaOptions=-Xss512m"
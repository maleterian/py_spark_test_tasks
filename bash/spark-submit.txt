#!/bin/bash

source ~/.bashrc

spark-submit \
    --master $SPARK_MASTER \
    --conf spark.executor.instances=1 \
    --conf spark.executor.cores=1     \
    --conf spark.executor.memory=512m \
    $@
#!/bin/bash

apt-get update && apt-get install -y curl vim wget dos2unix software-properties-common \
                                         ssh net-tools ca-certificates iputils-ping\
                                         python3 python3-pip python3-numpy \
                                         python3-matplotlib python3-scipy \
                                         python3-pandas python3-simpy

update-alternatives --install "/usr/bin/python" "python" "$(which python3)" 1

#export SPARK_HOME=/opt/spark

echo "SPARK_MASTER_PORT=7077
SPARK_MASTER_WEBUI_PORT=8080
SPARK_LOG_DIR=/usr/lib/spark/logs
SPARK_APPS=/opt/spark-apps/main
SPARK_DATA=/opt/spark-data
SPARK_TEST=/opt/spark-apps/test
SPARK_LOG=/opt/spark-log
SPARK_MASTER_LOG=/usr/lib/spark/logs/spark-master.out
SPARK_WORKER_LOG=/usr/lib/spark/logs/spark-worker.out
SPARK_WORKER_WEBUI_PORT=8080
SPARK_WORKER_PORT=7000
SPARK_MASTER="spark://spark-master:7077"
SPARK_WORKLOAD="master"
PYSPARK_PYTHON=python3
SERVICE_BASH=/opt/bash/service
PATH="$PATH:$SPARK_HOME/bin"
PYTHONPATH=$SPARK_HOME/python:$SPARK_APPS:$PYTHONPATH
WEB_APP=$SPARK_APPS/web \
WEB_APP_SCRIPT=app.py
PYTHONHASHSEED=1" >> /etc/environment

mkdir -p /opt/spark

mkdir -p $SPARK_LOG_DIR && \
touch $SPARK_MASTER_LOG && \
touch $SPARK_WORKER_LOG && \
ln -sf /dev/stdout $SPARK_MASTER_LOG && \
ln -sf /dev/stdout $SPARK_WORKER_LOG

export OPT_BASH=/opt/bash \
OPT_APPS=/opt/spark-apps \
OPT_DATA=/opt/spark-data \
OPT_LOGS=/opt/spark-log

mkdir -p $OPT_BASH && mkdir -p $OPT_APPS && mkdir -p $OPT_DATA && mkdir -p $OPT_LOGS


find /opt/spark-* -type f -print0 | xargs -0 dos2unix

gsutil cp -r gs://pyspark-test-tasks-bucket/py_spark_test_tasks/src/* $OPT_APPS
gsutil cp -r gs://pyspark-test-tasks-bucket/py_spark_test_tasks/data/* $OPT_DATA
gsutil cp -r gs://pyspark-test-tasks-bucket/py_spark_test_tasks/bash/* $OPT_BASH

#python3 -m pip install -r $SERVICE_BASH/requirements.txt

#/bin/bash -c "/opt/spark-apps/main/web/start_app.sh"















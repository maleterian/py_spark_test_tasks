#!/bin/bash

set -o pipefail
set -e

source "/opt/bash/.bashrc"

mkdir -p $SPARK_LOG_DIR && \
  touch $SPARK_MASTER_LOG && \
  touch $SPARK_WORKER_LOG && \
  ln -sf /dev/stdout $SPARK_MASTER_LOG && \
  ln -sf /dev/stdout $SPARK_WORKER_LOG

mkdir -p $SCRIPTS_SERVICE \
         $SPARK_TEST \
         $SPARK_LOG \
         $SPARK_APPS_LOG

echo "start ssh"
/usr/sbin/sshd -D &

if ! /opt/spark-apps/main/web/start_app.sh ; then
  echo "Cannot start web app"
  exit 1
fi

if ! /opt/bash/start-spark.sh ; then
  echo "Cannot start spark"
  exit 1
fi


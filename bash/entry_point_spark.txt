#!/bin/bash

source ~/.bashrc

set -eEu
set -o pipefail

mkdir -p $SPARK_LOG_DIR && \
  touch $SPARK_MASTER_LOG && \
  touch $SPARK_WORKER_LOG && \
  ln -sf /dev/stdout $SPARK_MASTER_LOG && \
  ln -sf /dev/stdout $SPARK_WORKER_LOG

mkdir -p $SCRIPTS_SERVICE \
         $SPARK_APPS_TEST \
         $SPARK_LOG \
         $SPARK_APPS_LOG \
         $SCRIPTS_SERVICE_SSH

print_info "start ssh"
/usr/sbin/sshd -D &

sleep 5
service ssh status

if [[ "$HOSTNAME" == "$SPARK_MASTER_HOST" ]]; then
    print_info "Copy common key"
    cp -r $SSH_DIR/* $SCRIPTS_SERVICE_SSH

    print_info "Starting web app"
    if ! /opt/spark-apps/main/web/start_app.sh ; then
      print_error "Cannot start web app"
      exit 1
    fi
fi

print_info "Starting spark"
if ! /opt/bash/start-spark.sh ; then
  print_error "Cannot start spark"
  exit 1
fi

ls -la


#!/bin/bash

source "/opt/spark/bin/load-spark-env.sh"

l_spark_class='/opt/spark/bin/spark-class'

# When the spark work_load is master run class org.apache.spark.deploy.master.Master
if [ "$SPARK_WORKLOAD" == "worker" ]; then
    # When the spark work_load is worker run class org.apache.spark.deploy.master.Workerhttp://localhost:8080
    $l_spark_class org.apache.spark.deploy.worker.Worker \
      --webui-port $SPARK_WORKER_WEBUI_PORT $SPARK_MASTER >> $SPARK_WORKER_LOG
elif [ "$SPARK_WORKLOAD" == "master" ]; then

    export SPARK_MASTER_HOST=`hostname`

    $l_spark_class org.apache.spark.deploy.master.Master \
      --ip $SPARK_MASTER_HOST \
      --port $SPARK_MASTER_PORT \
      --webui-port $SPARK_MASTER_WEBUI_PORT >> $SPARK_MASTER_LOG

elif [ "$SPARK_WORKLOAD" == "submit" ]; then
    echo "SPARK SUBMIT"
else
    echo "Undefined Workload Type $SPARK_WORKLOAD, must specify: master, worker, submit"
fi

#TEST

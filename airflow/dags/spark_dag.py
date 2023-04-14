from airflow.operators.dummy_operator import DummyOperator

import airflow
import datetime
from airflow.providers.ssh.operators.ssh import SSHOperator

with airflow.DAG(
        'compute_ssh_dag',
        start_date=datetime.datetime(2022, 1, 1)
) as dag:
    ssh_task = SSHOperator(
        task_id="spark_job",
        ssh_conn_id="ssh_default",
        # command="spark-submit /opt/spark-apps/main/pyspark_task.py -g 1",
        command="source /opt/bash/.bashrc ; hostname -i; env; spark-submit /opt/spark-apps/main/pyspark_task.py -g 1",
        dag=dag)

now = datetime.datetime.now()

start = DummyOperator(task_id="start", dag=dag)
spark_job = ssh_task
end = DummyOperator(task_id="end", dag=dag)

start >> spark_job >> end
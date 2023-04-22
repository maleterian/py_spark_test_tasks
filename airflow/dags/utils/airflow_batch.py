from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator


def get_spark_submit_operator(group_id: int, task_id: int, dag: DAG):
    return SSHOperator(
        task_id=f"pyspark_task_group_{group_id}_task_{task_id}",
        ssh_conn_id="ssh_default",
        command=f"/opt/bash/spark-submit.sh /opt/spark-apps/main/pyspark_task.py -g {group_id} -t {task_id}",
        dag=dag
    )

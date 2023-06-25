from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
import os

AWS_BUCKET = os.getenv("AWS_BUCKET", "eu-python-retraining-airflow-emr")
PROJECT_NAME = os.getenv("PROJECT_NAME", "py_spark_test_tasks")

AWS_S3_PROJECT_LOCATION = f"s3://{AWS_BUCKET}/{PROJECT_NAME}"
AWS_S3_BOOT_STRAP_ACTIONS_SCRIPT_PATH = f"{AWS_S3_PROJECT_LOCATION}/cloud/aws/bootstrap_actions.sh"

EMR_MANAGED_MASTER_SECURITY_GROUP = "sg-04cf4867d3b16f5c6"
EMR_MANAGED_SLAVE_SECURITY_GROUP = "sg-092b6c6432801b42e"
EMR_SUBNET = "subnet-06ae5853fb2ddbb80"
EMR_KEY_NAME = "ubart-python-retraining-program"

JOB_FLOW_ROLE = 'EMR_EC2_DefaultRole',
SERVICE_ROLE = 'arn:aws:iam::516763997660:role/EMR_DefaultRole',


def get_dag_name(in_file):
    return os.path.basename(in_file).replace(".py", "")


def get_spark_submit_operator(group_id: int, task_id: int, dag: DAG):
    return SSHOperator(
        task_id=f"pyspark_task_group_{group_id}_task_{task_id}",
        ssh_conn_id="ssh_default",
        command=f"/opt/bash/spark-submit.sh /opt/spark-apps/main/pyspark_task.py -g {group_id} -t {task_id}",
        dag=dag
    )

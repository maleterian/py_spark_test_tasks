from airflow import DAG
from airflow.utils.task_group import TaskGroup
from datetime import datetime
from utils.aws_airflow_batch import get_spark_submit_operator

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now(),
}

with DAG('spark_submit_all_tasks', default_args=default_args, schedule_interval=None) as dag:
    def get_task_operator(group_id, task_id):
        return get_spark_submit_operator(group_id, task_id, dag)

    # Define task groups

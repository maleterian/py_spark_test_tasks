from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime


def get_task_operator(group_id, task_id):
    return SSHOperator(
        task_id=f"pystark_task_group_{group_id}_task_{task_id}",
        ssh_conn_id="ssh_default",
        command=f"$SPARK_SUBMIT_SCRIPT $SPARK_APPS/pyspark_task.py -g {group_id} -t {task_id}",
        dag=dag
    )

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2022, 4, 23),
}

with DAG('spark_submit_all_tasks', default_args=default_args, schedule_interval='@daily') as dag:
    # Define task groups
    with TaskGroup('group1') as processing_tasks_group1:
        group1_task_1 = get_task_operator(1, 1)
        group1_task_2 = get_task_operator(1, 2)

    with TaskGroup('group2') as processing_tasks_group2:
        group2_task_1 = get_task_operator(2, 1)
        group2_task_2 = get_task_operator(2, 2)
        group2_task_3 = get_task_operator(2, 3)
        group2_task_4 = get_task_operator(2, 4)
        group2_task_5 = get_task_operator(2, 5)

    with TaskGroup('group3') as processing_tasks_group3:
        group3_task_1 = get_task_operator(3, 1)
        group3_task_2 = get_task_operator(3, 2)
        group3_task_3 = get_task_operator(3, 3)
        group3_task_4 = get_task_operator(3, 4)
        group3_task_5 = get_task_operator(3, 5)

    # Define dependencies between task groups
    processing_tasks_group1.set_downstream(processing_tasks_group2)
    processing_tasks_group2.set_downstream(processing_tasks_group3)

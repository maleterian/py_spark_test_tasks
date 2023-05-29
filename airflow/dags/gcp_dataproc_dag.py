# STEP 1: Import necessary libraries
from datetime import timedelta, datetime
from airflow import models
from airflow.operators import python_operator
from airflow.contrib.operators import dataproc_operator
from airflow.utils import trigger_rule

# STEP 2: Define references
SPARK_CODE = 'file:///opt/spark-apps/main/pyspark_task.py'
REGION = 'europe-central2'
ZONE = 'europe-central2-b'
CLUSTER_NAME = models.Variable.get('cluster_name')
PROJECT_ID = models.Variable.get('project_id')
BUCKET_NAME = models.Variable.get('bucket_name')
TASKS_LIST = [2, 5, 5, 3, 1]

# Define a start date
yesterday = datetime.now() - timedelta(days=1)

# STEP 3: Set default arguments for the DAG
default_dag_args = {
    'start_date': yesterday,
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'project_id': PROJECT_ID
}

# STEP 4: Define DAG
# Set the DAG name, add a DAG description, define the schedule interval and pass the default arguments defined before
with models.DAG(
        'pyspark_tasks_workflow',
        description='DAG for deployment a Dataproc Cluster',
        schedule_interval=timedelta(days=1),
        default_args=default_dag_args) as dag:

    # 4.a: Create dataproc cluster
    create_dataproc = dataproc_operator.DataprocClusterCreateOperator(
        task_id='create_cluster',
        cluster_name=CLUSTER_NAME,
        region=REGION,
        zone=ZONE,
        storage_bucket=BUCKET_NAME,
        num_workers=2,
        master_machine_type='n1-standard-2',
        worker_machine_type='n1-standard-2',
        init_actions_uris=[f'gs://{BUCKET_NAME}/init.sh']
    )

    # 4.b: Define display status function
    def print_status():
        return "PASS"

    # 4.c: Define print operators
    print_operator_1 = python_operator.PythonOperator(task_id="status_1", python_callable=print_status)
    print_operator_2 = python_operator.PythonOperator(task_id="status_2", python_callable=print_status)
    print_operator_3 = python_operator.PythonOperator(task_id="status_3", python_callable=print_status)
    print_operator_4 = python_operator.PythonOperator(task_id="status_4", python_callable=print_status)
    print_operator_5 = python_operator.PythonOperator(task_id="status_5", python_callable=print_status)

    # 4.1: Run the sql PySpark job group 1
    for idx in range(TASKS_LIST[0]):
        sql_job = dataproc_operator.DataProcPySparkOperator(
            task_id=f'run_sql_1_{idx + 1}',
            main=SPARK_CODE,
            cluster_name=CLUSTER_NAME,
            job_name=f"job_sql_1_{idx + 1}",
            region=REGION,
            arguments=[
                "-g=1",
                f"-t={idx + 1}",
                "-tt=sql"
            ],
        )

        # 4.2: Run the df PySpark job group 1
        df_job = dataproc_operator.DataProcPySparkOperator(
            task_id=f'run_df_1_{idx + 1}',
            main=SPARK_CODE,
            cluster_name=CLUSTER_NAME,
            job_name=f"job_df_1_{idx + 1}",
            region=REGION,
            arguments=[
                f"-g=1",
                f"-t={idx + 1}",
                "-tt=df"
            ],
        )

        # Set DAGs dependencies - each task should run after have finished the task before
        create_dataproc >> sql_job >> df_job >> print_operator_1

    # 4.3: Run the sql PySpark job group 2
    for idx in range(TASKS_LIST[1]):
        sql_job = dataproc_operator.DataProcPySparkOperator(
            task_id=f'run_sql_2_{idx + 1}',
            main=SPARK_CODE,
            cluster_name=CLUSTER_NAME,
            job_name=f"job_sql_2_{idx + 1}",
            region=REGION,
            arguments=[
                "-g=2",
                f"-t={idx + 1}",
                "-tt=sql"
            ],
        )

        # 4.4: Run the df PySpark job group 2
        df_job = dataproc_operator.DataProcPySparkOperator(
            task_id=f'run_df_2_{idx + 1}',
            main=SPARK_CODE,
            cluster_name=CLUSTER_NAME,
            job_name=f"job_df_2_{idx + 1}",
            region=REGION,
            arguments=[
                "-g=2",
                f"-t={idx + 1}",
                "-tt=df"
            ],
        )

        # Set DAGs dependencies - each task should run after have finished the task before
        print_operator_1 >> sql_job >> df_job >> print_operator_2

    # 4.5: Run the sql PySpark job group 3
    for idx in range(TASKS_LIST[2]):
        sql_job = dataproc_operator.DataProcPySparkOperator(
            task_id=f'run_sql_3_{idx + 1}',
            main=SPARK_CODE,
            cluster_name=CLUSTER_NAME,
            job_name=f"job_sql_3_{idx + 1}",
            region=REGION,
            arguments=[
                "-g=3",
                f"-t={idx + 1}",
                "-tt=sql"
            ],
        )

        # 4.6: Run the df PySpark job group 3
        df_job = dataproc_operator.DataProcPySparkOperator(
            task_id=f'run_df_3_{idx + 1}',
            main=SPARK_CODE,
            cluster_name=CLUSTER_NAME,
            job_name=f"job_df_3_{idx + 1}",
            region=REGION,
            arguments=[
                "-g=3",
                f"-t={idx + 1}",
                "-tt=df"
            ],
        )

        # Set DAGs dependencies - each task should run after have finished the task before
        print_operator_2 >> sql_job >> df_job >> print_operator_3

    # 4.7: Run the sql PySpark job group 4
    for idx in range(TASKS_LIST[3]):
        sql_job = dataproc_operator.DataProcPySparkOperator(
            task_id=f'run_sql_4_{idx + 1}',
            main=SPARK_CODE,
            cluster_name=CLUSTER_NAME,
            job_name=f"job_sql_4_{idx + 1}",
            region=REGION,
            arguments=[
                "-g=4",
                f"-t={idx + 1}",
                "-tt=sql"
            ],
        )

        # 4.8: Run the df PySpark job group 4
        df_job = dataproc_operator.DataProcPySparkOperator(
            task_id=f'run_df_4_{idx + 1}',
            main=SPARK_CODE,
            cluster_name=CLUSTER_NAME,
            job_name=f"job_df_4_{idx + 1}",
            region=REGION,
            arguments=[
                "-g=4",
                f"-t={idx + 1}",
                "-tt=df"
            ],
        )

        # Set DAGs dependencies - each task should run after have finished the task before
        print_operator_3 >> sql_job >> df_job >> print_operator_4

    # 4.9: Run the sql PySpark job group 5
    for idx in range(TASKS_LIST[4]):
        sql_job = dataproc_operator.DataProcPySparkOperator(
            task_id=f'run_sql_5_{idx + 1}',
            main=SPARK_CODE,
            cluster_name=CLUSTER_NAME,
            job_name=f"job_sql_5_{idx + 1}",
            region=REGION,
            arguments=[
                "-g=5",
                f"-t={idx + 1}",
                "-tt=sql"
            ],
        )

        # 4.10: Run the df PySpark job group 5
        df_job = dataproc_operator.DataProcPySparkOperator(
            task_id=f'run_df_5_{idx + 1}',
            main=SPARK_CODE,
            cluster_name=CLUSTER_NAME,
            job_name=f"job_df_5_{idx + 1}",
            region=REGION,
            arguments=[
                "-g=5",
                f"-t={idx + 1}",
                "-tt=df"
            ],
        )

        # Set DAGs dependencies - each task should run after have finished the task before
        print_operator_4 >> sql_job >> df_job >> print_operator_5

    # 4.d: Delete Cloud Dataproc cluster
    delete_dataproc = dataproc_operator.DataprocClusterDeleteOperator(
        task_id='delete_cluster',
        cluster_name=CLUSTER_NAME,
        trigger_rule=trigger_rule.TriggerRule.ALL_DONE,
        region=REGION
    )

    # Set DAGs dependencies - each task should run after have finished the task before
    print_operator_5 >> delete_dataproc

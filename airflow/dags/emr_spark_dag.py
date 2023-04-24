from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.operators.emr_create_job_flow import EmrCreateJobFlowOperator
from airflow.providers.amazon.aws.operators.emr_add_steps import EmrAddStepsOperator
from airflow.providers.amazon.aws.operators.emr_terminate_job_flow import EmrTerminateJobFlowOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'my_emr_dag',
    default_args=default_args,
    description='Run my Python project on EMR',
    schedule_interval=None,
)

cluster_name = 'eu-python-retraining-airflow-emr-cluster'
s3_bucket = 'eu-python-retraining-airflow-emr'
#s3://eu-python-retraining-airflow-emr

s3_project_path = f's3://{s3_bucket}/my_project'
s3_data_path = f's3://{s3_bucket}/my_data'

create_cluster = EmrCreateJobFlowOperator(
    task_id='create_emr_cluster',
    job_flow_overrides={
        'Name': cluster_name,
        'ReleaseLabel': 'emr-6.2.0',
        'Applications': [
            {'Name': 'Hadoop'},
            {'Name': 'Spark'},
            {'Name': 'Hive'},
            {'Name': 'Pig'}
        ],
        'Instances': {
            'InstanceGroups': [
                {
                    'Name': 'Master nodes',
                    'Market': 'SPOT',
                    'InstanceRole': 'MASTER',
                    'InstanceType': 'm5.xlarge',
                    'InstanceCount': 1,
                },
                {
                    'Name': 'Slave nodes',
                    'Market': 'SPOT',
                    'InstanceRole': 'CORE',
                    'InstanceType': 'm5.xlarge',
                    'InstanceCount': 2,
                }
            ],
            'Ec2KeyName': 'my-key-pair',
            'KeepJobFlowAliveWhenNoSteps': True,
            'TerminationProtected': False,
            'Ec2SubnetId': 'subnet-12345678',
            'EmrManagedMasterSecurityGroup': 'sg-12345678',
            'EmrManagedSlaveSecurityGroup': 'sg-12345678'
        }
    },
    aws_conn_id='aws_default',
    dag=dag,
)

step_addition = EmrAddStepsOperator(
    task_id='add_emr_step',
    job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
    aws_conn_id='aws_default',
    steps=[
        {
            'Name': 'My Python Project',
            'ActionOnFailure': 'CONTINUE',
            'HadoopJarStep': {
                'Jar': 'command-runner.jar',
                'Args': [
                    'spark-submit',
                    '--deploy-mode',
                    'client',
                    f'{s3_project_path}/my_script.py',
                    f'--data_path={s3_data_path}/my_data.csv'
                ]
            }
        }
    ],
    dag=dag,
)

terminate_cluster = EmrTerminateJobFlowOperator(
    task_id='terminate_emr_cluster',
    job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
    aws_conn_id='aws_default',
    dag=dag,
)

create_cluster >> step_addition >> terminate_cluster
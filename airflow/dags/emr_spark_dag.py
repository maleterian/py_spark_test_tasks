from airflow import DAG
from airflow.providers.amazon.aws.operators.emr import EmrAddStepsOperator
from airflow.providers.amazon.aws.operators.emr import EmrCreateJobFlowOperator
from airflow.providers.amazon.aws.operators.emr import EmrTerminateJobFlowOperator
from datetime import datetime, timedelta

from utils.airflow_batch import *

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'emr_example',
    default_args=default_args,
    description='Copy PySpark files to EMR',
    schedule_interval=None,
)

# Define the bootstrap actions
bootstrap_actions = [
    {
        'Name': 'Copy project files to EMR Cluster',
        'ScriptBootstrapAction': {
            'Path': AWS_S3_BOOT_STRAP_ACTIONS_SCRIPT_PATH,
            'Args': [
                PROJECT_NAME,
                AWS_BUCKET
            ]
        }
    }
]


# Step 1: Create EMR Cluster
create_cluster = EmrCreateJobFlowOperator(
    task_id='create_cluster',
    job_flow_overrides={
        'Name': 'Python retraining EMR Cluster',
        'ReleaseLabel': 'emr-6.3.0',
        'LogUri': f's3://{AWS_BUCKET}/logs',
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
                    'Name': 'Worker nodes',
                    'Market': 'SPOT',
                    'InstanceRole': 'CORE',
                    'InstanceType': 'm5.xlarge',
                    'InstanceCount': 2,
                }
            ],
            'TerminationProtected': False,
            'KeepJobFlowAliveWhenNoSteps': True,
            'Ec2KeyName': EMR_KEY_NAME,
            'Ec2SubnetId': EMR_SUBNET,
            'EmrManagedMasterSecurityGroup': EMR_MANAGED_MASTER_SECURITY_GROUP,
            'EmrManagedSlaveSecurityGroup': EMR_MANAGED_SLAVE_SECURITY_GROUP
        },
        'Applications': [
            {
                'Name': 'Spark'
            }
        ],
        'VisibleToAllUsers': True,
        'BootstrapActions': bootstrap_actions  # Add the bootstrap actions here
    },
    aws_conn_id='aws_default',
    dag=dag,
)

# Step 3: Submit Spark job
spark_submit = EmrAddStepsOperator(
    task_id='spark_submit',
    job_flow_id="{{ task_instance.xcom_pull('create_cluster', key='return_value') }}",
    aws_conn_id='aws_default',
    steps=[
        {
            'Name': 'Submit Spark Job',
            'ActionOnFailure': 'CONTINUE',
            'HadoopJarStep': {
                'Jar': 'command-runner.jar',
                'Args': [
                    '~/spark_submit.sh $SPARK_APPS/pyspark_task.py',
                    '-t',
                    '1'
                ],
            },
        }
    ],
    dag=dag,
)

# Step 4: Terminate the EMR cluster
terminate_cluster = EmrTerminateJobFlowOperator(
    task_id='terminate_cluster',
    job_flow_id="{{ task_instance.xcom_pull('create_cluster', key='return_value') }}",
    aws_conn_id='aws_default',
    dag=dag,
)

# Define the DAG dependencies
create_cluster >> spark_submit >> terminate_cluster

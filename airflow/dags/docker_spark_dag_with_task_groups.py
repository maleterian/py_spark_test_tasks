from airflow import DAG
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now(),
}

with DAG('spark_submit_all_tasks', default_args=default_args, schedule_interval=None) as dag:
     #Create YOUR data flow here

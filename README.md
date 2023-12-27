# Training project for PySpark

## Requirements:
* Docker 
  * on Linux 
  * on Windows with Ubuntu on WSL. Instruction is [here](https://ubuntu.com/tutorials/install-ubuntu-on-wsl2-on-windows-11-with-gui-support#1-overview) 
* 6 cores, 16 GB RAM for Spark cluster 
* 6 cores, 32 GB RAM for Spark cluster + Airflow 

## Project files description

Data transformation tasks (1-4) and schema description:
* data_transformation_task_description.txt

Inputs:
* data/input/tables/accounts/*.parquet
* data/input/tables/country_abbreviation/*.parquet
* data/input/tables/transactions/*.parquet

Outputs:
* data/output/df/task.../...
* data/output/sql/task.../...

Expected outputs:
* src/test/task1/expected_output/..
* src/test/task../expected_output/..

Code:
* src/main/pyspark_task.py - dataframes and sql definition
* src/main/pyspark_task_validator.py - module to invoke and test dataframes and sql definition
* src/main/resources/sql/.. - sql files with the same logic as for dataframes
* src/main/web/.. - web UI on flask for task invocation

* src/test/test_app.py - all tests definition
* docker/start-docker.sh - file to start project using bash commands. 
  * First parameter can have values **spark,airflow,all** used to start only spark/airflow or both. 
  * Second parameter can have values **y,n**, used to build image or not.
  * Third parameter can have values **y,n**, used to start test or not. 
* bash/... other files are related to the spark env config

## How to work with project:
1. How to initialize the project :
    1. Permissions set
       > chmod -R 755 ./*
    2. Docker image build
        1. Using prepared bash script
           > ./docker/start-docker.sh spark y

        2. Using docker commands
           ``` 
           docker build -f ./docker/DockerfileSpark  --build-arg SPARK_VERSION=3.0.2 --build-arg HADOOP_VERSION=3.2 -t cluster-apache-spark:3.0.2 ./       
           docker build -f ./docker/DockerfileAirflow  -t airflow-with-spark:1.0.0 ./
           ```     

2. How to run only spark cluster without airflow
    1. Using prepared bash script
       > ./docker/start-docker.sh spark n
    2. Using docker commands
       ```
       docker compose -f ./docker-compose-spark.yaml up -d
       docker container exec -it py_spark_test_tasks-spark-master-1 /bin/bash
       ```
3. How to run Spark and Airflow (already connected via ssh)
    1. Using prepared bash script
       > ./docker/start-docker.sh all n
    2. Using docker commands
       ``` 
       docker compose -f ./docker-compose-spark.yaml -f ./docker-compose-airflow.yaml up -d 
       ```

4. How to use main script **pyspark_task.py**:
   ``` spark-submit /opt/spark-apps/main/pyspark_task.py -g <GROUP_ID> -t <TASK_ID> -tt <TASK_TYPE> ```
    1. GROUP_ID has values from list [1,2,3,4]
    2. TASK_ID has values 1 from 5, depends on task, not every group task has 5 tasks
    3. TASK_TYPE has values from list [df,sql]

    ```
    #Examples
    spark-submit /opt/spark-apps/main/pyspark_task.py -g 1 -t 1 -tt df
    spark-submit /opt/spark-apps/main/pyspark_task.py -g 1 -t 1 -tt sql   
    spark-submit /opt/spark-apps/main/pyspark_task.py -g 2 -t 1 -tt df
    spark-submit /opt/spark-apps/main/pyspark_task.py -g 3 -t 1 -tt sql
    ``` 

6. How to run all tests using bash script:
> ./bash/start-docker.sh spark n y
6. How to run all tests manually:
```
  ./bash/start-docker.sh spark n  
  pytest /opt/spark-apps/test
```
6. How to run all failed tests:
> ./bash/start-docker.sh spark n f
5. Flask App to execute tasks from UI:
> http://localhost:8000/run_task
6. Spark Master UI
> http://localhost:9090/
7. Airflow UI
> http://localhost:8080/

###  Airflow integration task 
Summary: Run all tasks using airflow Group DAG.
```
You need to run Main script /opt/spark-apps/main/pyspark_task.py using Airflow.
User and PWD for AirFlow UI http://localhost:8080/ is airflow/airflow.
``` 
   1. Start spark cluster and airflow  
      ``` 
      docker compose -f ./docker-compose-spark.yaml -f ./docker-compose-airflow-no-connection-with-spark.yaml up -d
      ```
      if airflow doesn't start you need to clean up your docker images and volumes :
      ```
      docker rm -f $(docker ps -a -q)
      docker volume rm $(docker volume ls -q)
      docker system prune  
      ```
   2. Install and configure SSH and Spark submit providers
   3. Create simple DAG by connecting to the spark master host and running task 1.1 
   4. Create 4 group dags (one per each task)
      1. Group Dags need to be executed one by one
      2. Tasks inside group need to be executed in parallel
      3. Add your code to airflow/dags/docker_spark_dag_with_task_groups.py or create your own DAG
      4. Check and understand the config, write your own DAG 
   5. If you had issues with the config use next command and check the solution.  
      1. command to create spark cluster + airflow + ssh connection between them
      > ./docker/start-docker.sh all y 
      2. command to connect to any container          
      > docker container exec -it [container_name] /bin/bash
      3. command to get list of container names 
      ```docker compose -f ./docker-compose-spark.yaml -f ./docker-compose-airflow-no-connection-with-spark.yaml ps```
   6. List of bash commands that you need to add to the dag
      ```
      # df
      ## group 1
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 1 -t 1 -tt df
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 1 -t 2 -tt df
      ## group 2    
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 2 -t 1 -tt df
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 2 -t 2 -tt df
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 2 -t 3 -tt df
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 2 -t 4 -tt df
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 2 -t 5 -tt df
      ## group 3
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 3 -t 1 -tt df      
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 3 -t 2 -tt df
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 3 -t 3 -tt df
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 3 -t 4 -tt df
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 3 -t 5 -tt df
      ## group 4
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 4 -t 1 -tt df
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 4 -t 2 -tt df
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 4 -t 3 -tt df
      
      # sql
      ## group 1
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 1 -t 1 -tt sql
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 1 -t 2 -tt sql
      ## group 2    
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 2 -t 1 -tt sql
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 2 -t 2 -tt sql
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 2 -t 3 -tt sql
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 2 -t 4 -tt sql
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 2 -t 5 -tt sql
      ## group 3
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 3 -t 1 -tt sql      
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 3 -t 2 -tt sql
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 3 -t 3 -tt sql
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 3 -t 4 -tt sql
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 3 -t 5 -tt sql
      ## group 4
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 4 -t 1 -tt sql
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 4 -t 2 -tt sql
      spark-submit /opt/spark-apps/main/pyspark_task.py -g 4 -t 3 -tt sql      
      ```
   7. if you would like to run them manually please connect to the master host using command below and then just execute spark submit commands
      > docker container exec -it py_spark_test_tasks-spark-master-1 /bin/bash
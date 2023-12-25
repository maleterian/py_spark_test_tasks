# Training project for PySpark

## Requirements:
* Docker ( on Linux or on Windows with WSL support to run bash scripts )
   * 6 cores, 12 GB RAM
      - SPARK_WORKER_CORES : 2 * 3
      - SPARK_WORKER_MEMORY : 2G * 3
      - SPARK_DRIVER_MEMORY : 1G * 3
      - SPARK_EXECUTOR_MEMORY : 1G * 3

## Project data
Data transformation tasks (1-4) and schema description:
* data_transformation_task_description.txt

Inputs:
* data/tables/accounts/*.parquet
* data/tables/country_abbreviation/*.parquet
* data/tables/transactions/*.parquet

Outputs:
* data/df/task.../...
* data/sql/task.../...

Expected outputs:
* src/test/task1/expected_output/..
* src/test/task../expected_output/..

## Project realisation files
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

## Project tasks
### 1. Pyspark Task : Spark API + Spark SQL + pytest (easy difficulty)
Summary : Use spark sql and dataframes API for data processing. Implement all tasks described in data_transformation_task_description.txt 
   1. Write sql code in all src/main/resources/sql/task*/
   2. Write pyspark code for all dataframes in pyspark_task.py 
   3. Check how we can invoke subsets of tests for
      1. Data Frame
      2. SQLs
      3. Task group
      4. Particular Task
   4. Understand implementation of config and tests for pytest ( conftest.py, test_app.py )
   5. Make sure that all test passed 
      1. Option1: Run all tests using prepared bash script  
      ```
      ./docker/start-docker.sh spark y y
      ```
      2. Option2: Connect to master node and run all tests
      ```
      docker container exec -it py_spark_test_tasks-spark-master-1 /bin/bash
      pytest /opt/spark-apps/test
      ```
      3. Option3: Run one test for task (for debug/development)
      ```
      pytest /opt/spark-apps/test/test_app.py --task_type sql --task_group_id 2 --task_id 1 --skip-xfail       
      pytest /opt/spark-apps/test/test_app.py --task_type df  --task_group_id 2 --task_id 1 --skip-xfail
      ```
   

### 2. Python core task (hard)
Summary : Implement modules specified below by yourself
   1. Create own data comparison framework (write your own pyspark_task_validator.py)
   2. Test created all transformations for SQL and Dataframe api using pytest-spark (write your own test_app.py)
   3. Add logging to all your functions using decorators(write your own project_logs.py)


### 3. Airflow integration task (easy) 
Summary: Run all tasks using airflow Group DAG.
```
You need to run Main script /opt/spark-apps/main/pyspark_task.py using Airflow.
Script parameters described in "How to work with project".
User and PWD for AirFlow UI http://localhost:8080/ is airflow/airflow.
```

   1. Start spark cluster and airflow  
   > ./docker/start-docker.sh all y y
   2. Install and configure SSH and Spark submit providers
   3. Create simple DAG by connecting to the spark master host and running task 1.1 
   4. Create 4 group dags (one per each task)
      1. Group Dags need to be executed one by one
      2. Tasks inside group need to be executed in parallel
      3. Add your code here airflow/dags/docker_spark_dag_with_task_groups.py
      4. Check and understand the config, write your own DAG 

### 4. Python core + flask (hard)
Summary: Create UI using flask for execution of implemented tasks. 
1. You need to write code in **src/main/web/app.py** and **src/main/web/templates/main.html**
2. Flask app need to be accessible from http://localhost:8000/run_task
3. You should have ability to
   1. Choose task from drop down list
   2. Choose method of execution (sql, dataframe or both) from drop down list
   3. Button to start execution
   4. See logs generated by your script in real time on your web page

### 5. Cloud task (hard)
Summary: Make this solution work on any cloud. 
Example for GCP you can find in ./cloud/gcp/PySpark_on_GCP_Tutorial.pdf.
It has explanation of all steps but uses previous structure of the project, so you will need to amend it to make it work 


## How to work with project:
1. Initialization :
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

2. Run only spark cluster without airflow
    1. Using prepared bash script
       > ./docker/start-docker.sh spark n
    2. Using docker commands
       ```
       docker compose -f ./docker/docker-compose-spark.yaml up -d
       docker container exec -it py_spark_test_tasks-spark-master-1 /bin/bash
       ```
3. Run Spark and Airflow
    1. Using prepared bash script
       > ./docker/start-docker.sh all n
    2. Using docker commands
       ``` 
       docker compose -f ./docker/docker-compose-spark.yaml -f ./docker/docker-compose-airflow.yaml up -d 
       ```

4. Main script **/opt/spark-apps/main/pyspark_task.py** and its parameters:
    1. GROUP_ID has values from list [1,2,3,4]
    2. TASK_ID has values 1 from 5, depends on task, not every group task has 5 tasks
    3. TASK_TYPE has values from list [df,sql]
    
    ```
    #spark-submit /opt/spark-apps/main/pyspark_task.py -g <GROUP_ID> -t <TASK_ID> -tt <TASK_TYPE>
    spark-submit /opt/spark-apps/main/pyspark_task.py -g 1 -t 1 -tt df
    spark-submit /opt/spark-apps/main/pyspark_task.py -g 1 -t 1 -tt sql   
    spark-submit /opt/spark-apps/main/pyspark_task.py -g 2 -t 1 -tt df
    spark-submit /opt/spark-apps/main/pyspark_task.py -g 3 -t 1 -tt sql
    ``` 

5. How to run all tests using bash script:
> ./bash/start-docker.sh spark n y
6. How to run all tests manually:
>   ./bash/start-docker.sh spark n
>
>   pytest /opt/spark-apps/test
6. How to run all failed tests:
> ./bash/start-docker.sh spark n f
5. Flask App to execute tasks from UI:
> http://localhost:8000/run_task
6. Spark Master UI
> http://localhost:9090/
7. Airflow UI
> http://localhost:8080/ 
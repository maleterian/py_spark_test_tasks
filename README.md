# Test project for pyspark
## Goals :
### Easy Mode
1. Use spark sql and dataframes API for data processing 
   1. Write sql code in all src/sql/task*/
   2. Write pyspark code for all dataframes in pyspark_task.py 
   3. Make sure that all test passed, 
      1. run command 
      > ./bash/start-docker.sh y y
      2. or in master container execute 
      > pytest /opt/spark-test

### Hard Mode
1. Implement easy mode 
2. Create own data comparison framework (write your own pyspark_task_validator.py)
3. Test created all transformations for SQL and Dataframe api using pytest-spark (write your own test_app.py)
4. Add logging to all your functions using decorators(write your own project_logs.py)  
5. Create docker image and run spark cluster (1 master 2 workers) on it (Add your own docker compose and Docker file)

###  Extra Hard Mode
1. Implement hard mode
2. Create UI using flask for execution implemented tasks, you should have ability to
   1. Choose task from drop down list
   2. Choose method of execution (sql, dataframe or both) from drop down list
   3. Button to start execution
   4. See logs generated by your script in real time on your web page

###  Expert Mode
1. Implement Extra Hard mode
2. Make this solution work on any cloud
3. Add CD/CI to your git project (https://circleci.com/)

## Requirements:
* Docker ( on Linux or with WSL support to run bash scripts )
  * 6 cores, 12 GB RAM
    - SPARK_WORKER_CORES : 2 * 3
    - SPARK_WORKER_MEMORY : 2G * 3
    - SPARK_DRIVER_MEMORY : 1G * 3
    - SPARK_EXECUTOR_MEMORY : 1G * 3

## How work with project environment:
1. First time execution needs flag L_IN_BUILD_IMAGE = "y" :
> ./bash/start-docker.sh y 
2. To connect to docker container :
> ./bash/start-docker.sh n
3. To run all tests : 
> ./bash/start-docker.sh n y
4. To run failed tests : 
> ./bash/start-docker.sh n f


## Project data
Tasks Description:
* Task_Description.txt

Inputs:
* data/tables/accounts/*.parquet
* data/tables/country_abbreviation/*.parquet
* data/tables/transactions/*.parquet

Outputs:
* data/df/task.../...
* data/sql/task.../...

Expected outputs:
* test/task1/expected_output/..
* test/task../expected_output/..

## Project realisation files
* src/pyspark_sql.py - general logic for tasks implementation using sql/df together with testing framework
* src/pyspark_dataframe.py - dataframes definition
* src/sql/.. - sql files with the same logic as for dataframes 

* test/test_app.py - all tests definition
* bash/start-docker.sh - file to start project
* bash/... other files are related to the spark env config 



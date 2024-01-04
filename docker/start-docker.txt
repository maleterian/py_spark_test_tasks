#!/bin/bash

# For first time run use L_IN_BUILD_IMAGE = "y" it will build spark cluster image
#    example ./bash/start-spark-docker.sh y
# To start project with tests run set L_IN_RUN_TEST="y"
#    example ./bash/start-spark-docker.sh n y
# To rerun failed tests set L_IN_RUN_TEST="f"
#    example ./bash/start-spark-docker.sh n f

set -eEu
set -o pipefail

# syntax below is not compatible with some Mac OS thus using tr '[:upper:]' '[:lower:]'
#declare -l


declare L_IN_YAML_SPARK="-f ./docker-compose-spark.yaml "
declare L_IN_YAML_AIRFLOW="-f ./docker-compose-airflow.yaml "
declare L_IN_YAML_ALL="$L_IN_YAML_SPARK $L_IN_YAML_AIRFLOW"

declare L_IN_YAML=$( tr '[:upper:]' '[:lower:]' <<< "${1:-spark}" )
declare L_IN_BUILD_IMAGE=$( tr '[:upper:]' '[:lower:]' <<< "${2:-n}" )
declare L_IN_RUN_TEST=$( tr '[:upper:]' '[:lower:]' <<< "${3:-n}" )
declare L_IN_SPARK_VERSION=$( tr '[:upper:]' '[:lower:]' <<< "${4:-3.0.2}" )
declare L_IN_HADOOP_VERSION=$( tr '[:upper:]' '[:lower:]' <<< "${5:-3.2}" )

if  [[ "$L_IN_YAML" == "spark" ]]; then
  l_yaml=$L_IN_YAML_SPARK
elif  [[ "$L_IN_YAML" == "airflow" ]]; then
  l_yaml=$L_IN_YAML_AIRFLOW
else
  l_yaml="$L_IN_YAML_ALL"
fi

declare l_spark_master_container

export SPARK_IMAGE="cluster-apache-spark:$L_IN_SPARK_VERSION"
export AIRFLOW_IMAGE_NAME=airflow-with-spark:1.0.0
export SPARK_VERSION=$L_IN_SPARK_VERSION
export HADOOP_VERSION=$L_IN_HADOOP_VERSION
#export AIRFLOW_UID=100

function fn_run_command() {
  declare l_in_command=${1:?}
  declare l_in_err_msg=${2:?}
  declare l_in_err_code=${3:-1}
  declare l_in_exit=$( tr '[:upper:]' '[:lower:]' <<< "${4:-y}" )

  declare l_proc_exit_code=0

  echo "************************************************************"
  echo "Running: $l_in_command"
  echo "************************************************************"

  if ! eval $l_in_command ; then
    echo "$l_in_err_msg"
    l_proc_exit_code=1

    if  [[ "$l_in_exit" == "y" ]]; then
      exit $l_in_err_code
    fi

  fi

  return $l_proc_exit_code
}

function fn_get_proj_folder() {

  fn_run_command "l_spark_master_container=\$( docker compose $l_yaml  ps | grep '\-spark\-master\-1' | cut -d ' ' -f1 )" \
                 "Cannot get docker project name"\
                 "30"\
                 "n"
}

if [[ "$L_IN_BUILD_IMAGE" == 'y' ]]; then

  rm -f ~/.docker/config.json
#  sudo apt-get update
#  sudo apt-get install dos2unix
#
#  dos2unix ./*

  fn_run_command "docker compose $l_yaml down " \
                 "Cannot Stop project"\
                 "10"\
                 "n"

  fn_run_command "docker build -f ./docker/DockerfileSpark --build-arg SPARK_VERSION=$L_IN_SPARK_VERSION --build-arg HADOOP_VERSION=$L_IN_HADOOP_VERSION -t $SPARK_IMAGE ./ "\
                 "Cannot build image"\
                 "20"

  fn_run_command "docker build -f ./docker/DockerfileAirflow  -t $AIRFLOW_IMAGE_NAME ./ "\
                 "Cannot build image"\
                 "25"

fi

if ! fn_get_proj_folder ; then

  fn_run_command "docker compose $l_yaml up -d " \
                 "Cannot Start project"\
                 "40"

  if ! fn_get_proj_folder ; then
    exit 45
  fi

fi

l_test_cmd=""

if  [[ "$L_IN_RUN_TEST" != "n" ]]; then

  # rerun failed
  l_rerun_flag=""
  if [[ "$L_IN_RUN_TEST" == "f" ]]; then
    l_rerun_flag=" --lf"
  fi

  l_test_cmd="-c 'pytest /opt/spark-test $l_rerun_flag'"
fi

fn_run_command "docker container exec -it ${l_spark_master_container} /bin/bash $l_test_cmd"  \
               "Cannot connect to the master"\
               "50"

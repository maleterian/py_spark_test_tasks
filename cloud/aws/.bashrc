#!/bin/bash

# Note: PS1 and umask are already set in /etc/profile. You should not
# need this unless you want different defaults for root.
# PS1='${debian_chroot:+($debian_chroot)}\h:\w\$ '
# umask 022

export SHELL=/bin/bash

# change variables to run on EMR
export AWS_BUCKET=eu-python-retraining-airflow-emr
export PROJECT_NAME=py_spark_test_tasks
export PROJECT_PATH=~/$PROJECT_NAME
export SCRIPTS=$PROJECT_PATH/cloud/aws/
export SPARK_DATA="s3://$AWS_BUCKET/$PROJECT_NAME/data"
export SPARK_APPS=$PROJECT_PATH/src/main
export SPARK_APPS_LOG=$PROJECT_PATH/src/log
export SPARK_APPS_TEST=$PROJECT_PATH/src/test
export SPARK_SUBMIT_SCRIPT=$SCRIPTS/spark-submit.sh
export SPARK_MASTER="yarn"

# python var
export PYSPARK_PYTHON=python3
export PYTHONHASHSEED=1
export PYTHONPATH=$PYTHONPATH:$SPARK_APPS

mkdir -p $SCRIPTS    \
         $SPARK_APPS \
         $SPARK_APPS_LOG \
         $SPARK_APPS_TEST

alias ls='ls $LS_OPTIONS'
alias ll='ls $LS_OPTIONS -l'
alias l='ls $LS_OPTIONS -lA'

# Some more alias to avoid making mistakes:
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

function print_step() {
    echo "***********************************************"
    echo "$@"
    echo "***********************************************"
}

function print_error() {
    print_step "ERROR : $@"
}

function print_info() {
    print_step "INFO : $@"
}

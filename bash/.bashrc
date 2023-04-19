# ~/.bashrc: executed by bash(1) for non-login shells.

# Note: PS1 and umask are already set in /etc/profile. You should not
# need this unless you want different defaults for root.
# PS1='${debian_chroot:+($debian_chroot)}\h:\w\$ '
# umask 022

# You may uncomment the following lines if you want `ls' to be colorized:
# export LS_OPTIONS='--color=auto'
# eval "`dircolors`"
alias ls='ls $LS_OPTIONS'
alias ll='ls $LS_OPTIONS -l'
alias l='ls $LS_OPTIONS -lA'

# Some more alias to avoid making mistakes:
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

cd /opt/spark-apps 

# APP params
export WEB_APP=/opt/spark-apps/main/web
export WEB_APP_SCRIPT=app.py
export SCRIPTS=/opt/bash/
export SCRIPTS_SERVICE=$SCRIPTS/service
export SPARK_DATA=/opt/spark-data
export SPARK_APPS=/opt/spark-apps/main
export SPARK_APPS_LOG=/opt/spark-apps/log
export SPARK_APPS_TEST=/opt/spark-apps/test
export SPARK_SUBMIT_SCRIPT=$SCRIPTS/spark-submit.sh

#spark logs
export SPARK_LOG=/opt/spark-log
export SPARK_LOG_DIR=/opt/spark/logs
export SPARK_MASTER_LOG=$SPARK_LOG_DIR/spark-master.out
export SPARK_WORKER_LOG=$SPARK_LOG_DIR/spark-worker.out

# spark master params
export SPARK_MASTER=spark://spark-master:7077
export SPARK_MASTER_PORT=7077
export SPARK_MASTER_WEBUI_PORT=8080
export SPARK_MASTER_HOST=spark-master

# spark worker params
export SPARK_WORKER_WEBUI_PORT=8080
export SPARK_WORKER_PORT=7000
export SPARK_HOME=/opt/spark

# env var
export PWD=/root
export HOME=/root
export LANG=C.UTF-8
export TERM=xterm
export SSH_DIR=~/.ssh
export PATH=/usr/local/openjdk-11/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/spark/bin
export JAVA_HOME=/usr/local/openjdk-11
export JAVA_VERSION=11.0.11+9

# python var
export PYSPARK_PYTHON=python3
export PYTHONHASHSEED=1
export PYTHONPATH=/opt/spark/python:/opt/spark-apps/main:



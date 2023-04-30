#!/bin/bash

# Note: PS1 and umask are already set in /etc/profile. You should not
# need this unless you want different defaults for root.
# PS1='${debian_chroot:+($debian_chroot)}\h:\w\$ '
# umask 022

export SHELL=/bin/bash

# APP params
export SPARK_DATA=/opt/spark-data
export SPARK_APPS=/opt/spark-apps/main
export SPARK_APPS_LOG=/opt/spark-apps/log
export SPARK_APPS_TEST=/opt/spark-apps/test
export SPARK_SUBMIT_SCRIPT=$SCRIPTS/spark-submit.sh

# SPARK cluster env var
if [[ -d "$SPARK_APPS" ]]; then
    # python var
    export PYSPARK_PYTHON=python3
    export PYTHONHASHSEED=1
    export PYTHONPATH=$PYTHONPATH:$SPARK_APPS:
fi

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

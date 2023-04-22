#!/bin/bash

function add_connection() {
    l_name="$1"
    l_json="$2"

    if ! l_output=$(airflow connections add $l_name --conn-json "$l_json" 2>&1 )  ; then
        if ! grep "$l_name already exists."  <<< "$l_output" ; then
            return 1
        fi
    fi
}

add_connection 'spark_default' '{
    "conn_type": "spark",
    "host": "spark://spark-master",
    "port": "7077",
    "extra": {
        "queue": "root.default"
    }
}'

add_connection 'ssh_default' '{
    "conn_type": "ssh",
    "host": "spark-master",
    "login": "airflow",
    "port": "22",
    "extra": {
        "key_file": "/home/airflow/.ssh/id_rsa"
    }
}'
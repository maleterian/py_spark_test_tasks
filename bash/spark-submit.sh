#!/bin/bash

source "/opt/bash/.bashrc"

spark-submit --master $SPARK_MASTER $@
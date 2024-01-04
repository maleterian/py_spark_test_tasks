#!/bin/bash

source ~/.bashrc

l_cmd="spark-submit --master yarn --deploy-mode cluster $@"

print_step " $l_cmd "

if ! $l_cmd 2>&1 ; then
    print_error "command $l_cmd failed"
fi
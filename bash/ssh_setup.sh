#!/bin/bash

source ~/.bashrc

set -eEu
set -o pipefail

l_shared_key=$SCRIPTS_SERVICE_SSH/$SSH_FILE_PUB

if [[ -s $l_shared_key ]]; then
    print_info "Found $l_shared_key "

    print_info "Creating $SSH_DIR"
    mkdir -v -p $SSH_DIR

    print_info "Copying keys"
    cp -v $SCRIPTS_SERVICE_SSH/* $SSH_DIR
    cp -v $SCRIPTS_SERVICE_SSH/$SSH_FILE_PUB $SSH_DIR/authorized_key

    ls -la $SSH_DIR

    print_info "Setting permissions to make keys work"
    chmod -v 600 $SSH_DIR/$SSH_FILE
    chmod -v 700 $SSH_DIR

    print_info "Adding spark master key to known_hosts "
    ssh-keyscan spark-master > $SSH_DIR/known_hosts
fi

# print_info "start ssh"
# /usr/sbin/sshd -D &

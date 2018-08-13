#!/usr/bin/env bash

function env_build(){
    date
    cd `dirname $0`
    cd ../grafana
    echo "pwd="`pwd`
}

function main(){
    env_build

    nohup python collect_es_metric_to_grafana_esdb.py 1>/dev/null 2>&1 &
}

main
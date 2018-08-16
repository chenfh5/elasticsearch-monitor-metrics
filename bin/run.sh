#!/usr/bin/env bash

# parameter initial
# srcServerList="localhost:9200,localhost:9202"
# destServer="localhost:9200"
# your_storage_index_name="es_metric_collect"
# interval_in_second=10
srcServerList=$1
destServer=$2
your_storage_index_name=$3
interval_in_second=$4

function env_build(){
    date
    cd `dirname $0`
    cd ../monitor
    echo "pwd="`pwd`

    export PYTHONPATH=`pwd`
}

function main(){
    env_build
    echo ${srcServerList}
    echo ${destServer}
    echo ${your_storage_index_name}
    echo ${interval_in_second}

    # executor
    nohup python collect_es_metric_to_grafana_esdb.py ${srcServerList} ${destServer} ${your_storage_index_name} ${interval_in_second} 1>shell.log 2>&1 &
    tailf ../logdir/LOGGER.log
}

main
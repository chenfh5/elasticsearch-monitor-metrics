#!/usr/bin/env bash

echo "start to stop"
ps aux | grep "collect_es_metric_to_grafana_esdb" | grep -v "grep" | awk '{print $2}' | xargs kill -9
echo "end to stop at:" `date`
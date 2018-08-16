# elasticsearch-monitor-metrics

> 使用grafana(dataSource=es)展示多集群的es监控信息

----
# QuickStart
1. mark your_storage_index_name to store monitor metrics
2. Set up one or more es clusters
3. Set up the grafana and configure its data source(name=own_grafana_es) using es with your_index_name and pattern([your_storage_index_name_]YYYYMMDD)
4. Import Dashboard using JSON format from ./grafana/dashboard.json
5. sh ./bin/run.sh localhost:9200,localhost:9202 localhost:9200 es_metric_collect 30
6. check grafana and enjoy your trip

----
# TODO Upgrade
| build-in  | third-party |
|---:|---:|
| sys.argv | argparse |
| urllib | request |
| while-true-timer | schedule |

# Reference
- [Grafana Elasticsearch Dashboard](https://grafana.net/dashboards/878)
- mainly forked from [trevorndodds/elasticsearch-metrics](https://github.com/trevorndodds/elasticsearch-metrics)
- [detail](https://www.jianshu.com/p/df19477efa88)

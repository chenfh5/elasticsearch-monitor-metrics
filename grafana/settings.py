# -*- coding: utf-8 -*-
import os

# ElasticSearch Cluster to Monitor
# use a comma to split
# es_servers_to_monitor = os.environ.get('ES_METRICS_CLUSTER_URL', 'http://srcServer:9200')
# interval = int(os.environ.get('ES_METRICS_INTERVAL', '60'))
#
# # ElasticSearch Cluster to Send Metrics
# es_server_to_storage = os.environ.get('ES_METRICS_MONITORING_CLUSTER_URL', 'http://destServer:9200')
# es_index_to_storage = os.environ.get('ES_METRICS_INDEX_NAME', 'elasticsearch_metrics')

# Enable Elasticsearch Security
# read_username and read_password for read ES cluster information
# write_username and write_passowrd for write monitor metric to ES.
read_es_security_enable = False
read_username = "read_username"
read_password = "read_password"

write_es_security_enable = False
write_username = "write_username"
write_password = "write_password"

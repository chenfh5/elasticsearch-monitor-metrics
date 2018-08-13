# -*- coding: utf-8 -*-

import datetime
import json
import multiprocessing
import sys
import time

import own_settings
from own_log import LOG
from own_util import Util, DateUtil


class EsMonitorMetric(object):

    @staticmethod
    def create_index(es_host_port_to_monitor, index_name):
        # 1. check index exists or not
        url = "%s/_cat/indices/%s?h=index" % (es_host_port_to_monitor, index_name)
        response = Util.read_data_from_src(url)
        # 2. index not exists
        # TODO resp is None is not elegant here, should only != 200, use `request` to implement it
        if response is None or response.getcode() != 200:
            # 2-1. build mapping and setting
            index_mapping = {"mappings": {}}
            index_mapping["mappings"][own_settings.type_name] = {}
            mapping = dict(type='keyword', norms='false')
            strings_as_keywords = dict(match_mapping_type='string', mapping=mapping)
            strings_as_keywords = dict(strings_as_keywords=strings_as_keywords)
            dynamic_templates = [strings_as_keywords]
            index_mapping["mappings"][own_settings.type_name]["dynamic_templates"] = dynamic_templates
            index_mapping["settings"] = {}
            index_mapping["settings"]["index"] = {}
            index_mapping["settings"]["index"]["number_of_shards"] = 1
            index_mapping["settings"]["index"]["number_of_replicas"] = 0

            # 2-2. build url and
            url = "%s/%s" % (es_host_port_to_monitor, index_name)
            response = Util.send_data_to_dest(url, index_mapping, put_method=True)
            time.sleep(1)
            return response
        return response

    @staticmethod
    def fetch_cluster_health(es_host_port_to_monitor):
        """
        https://www.elastic.co/guide/en/elasticsearch/reference/current/cluster-health.html
        """
        try:
            endpoint = "_cluster/health"
            url = "%s/%s" % (es_host_port_to_monitor, endpoint)
            response = Util.read_data_from_src(url)
            jsondata = json.loads(response.read())
            cluster_name = jsondata['cluster_name']
            jsondata['@timestamp'] = DateUtil.get_current_time_str()
            if jsondata['status'] == 'green':
                jsondata['status_code'] = 0
            elif jsondata['status'] == 'yellow':
                jsondata['status_code'] = 1
            elif jsondata['status'] == 'red':
                jsondata['status_code'] = 2
            return cluster_name, jsondata
        except IOError:
            LOG.info("IOError: Maybe can't connect to elasticsearch.")
            cluster_name = "unknown"
            return cluster_name, "{}"

    @staticmethod
    def fetch_cluster_stats(es_host_port_to_monitor):
        """
        drop key(nodes, indices brief summary), since more detailed stats would be support in the next rest-ful API
        https://www.elastic.co/guide/en/elasticsearch/reference/current/cluster-stats.html
        """
        endpoint = "_cluster/stats"
        url = "%s/%s" % (es_host_port_to_monitor, endpoint)
        response = Util.read_data_from_src(url)
        jsondata = json.loads(response.read())
        jsondata['@timestamp'] = DateUtil.get_current_time_str()
        # drop key
        jsondata.pop("nodes")
        jsondata.pop("indices")
        return jsondata

    @staticmethod
    def fetch_node_stats(es_host_port_to_monitor, cluster_name):
        """
        monitor each node
        https://www.elastic.co/guide/en/elasticsearch/reference/current/cluster-nodes-stats.html
        """
        endpoint = "_cat/nodes?v&h=n"
        url = "%s/%s" % (es_host_port_to_monitor, endpoint)
        response = Util.read_data_from_src(url)
        nodes = response.read()[1:-1].strip().split('\n')
        new_jsondata_list = []
        #
        for node in nodes:
            endpoint = "_nodes/%s/stats" % node.rstrip()
            url = "%s/%s" % (es_host_port_to_monitor, endpoint)
            response = Util.read_data_from_src(url)
            jsondata = json.loads(response.read())
            nodeID = jsondata['nodes'].keys()
            try:
                jsondata['nodes'][nodeID[0]]['@timestamp'] = DateUtil.get_current_time_str()
                jsondata['nodes'][nodeID[0]]['cluster_name'] = cluster_name
                new_jsondata = jsondata['nodes'][nodeID[0]]
                new_jsondata_list.append(new_jsondata)
            except:
                continue
        return new_jsondata_list

    @staticmethod
    def fetch_index_stats(es_host_port_to_monitor, cluster_name):
        """
        not monitor each index, but the whole indices stats
        drop primary summary. To reduce the index schema count, only reserve total(primary + replica)
        https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-stats.html
        """
        endpoint = "_stats"
        url = "%s/%s" % (es_host_port_to_monitor, endpoint)
        response = Util.read_data_from_src(url)
        jsondata = json.loads(response.read())
        jsondata['_all']['@timestamp'] = DateUtil.get_current_time_str()
        jsondata['_all']['cluster_name'] = cluster_name
        jsondata['_all'].pop("primaries")  # drop key
        return jsondata['_all']


class EsMonitorTimer(multiprocessing.Process):

    def __init__(self, es_host_port_to_monitor, es_host_port_to_storage, es_index_to_storage, interval_in_second=60):
        super(EsMonitorTimer, self).__init__()
        self.es_host_port_to_monitor = es_host_port_to_monitor
        self.es_host_port_to_storage = es_host_port_to_storage
        self.es_index_to_storage = es_index_to_storage
        self.interval_in_second = interval_in_second

    def go(self):
        index_name = "%s_%s" % (self.es_index_to_storage, str(datetime.datetime.utcnow().strftime('%Y%m%d')))
        EsMonitorMetric.create_index(self.es_host_port_to_monitor, index_name)
        cluster_name, jsondata = EsMonitorMetric.fetch_cluster_health(self.es_host_port_to_monitor)
        if cluster_name != "unknown":
            # dict
            cluster_stats = EsMonitorMetric.fetch_cluster_stats(self.es_host_port_to_monitor)
            index_stats = EsMonitorMetric.fetch_index_stats(self.es_host_port_to_monitor, cluster_name)
            # dict list
            node_stats_list = EsMonitorMetric.fetch_node_stats(self.es_host_port_to_monitor, cluster_name)
            # send monitor data
            url = "%s/%s/%s" % (self.es_host_port_to_storage, index_name, own_settings.type_name)
            for one_jsondata in ([jsondata, cluster_stats, index_stats] + node_stats_list):
                Util.send_data_to_dest(url, one_jsondata, put_method=False)  # urllib default is get/post
        return cluster_name

    def run(self):
        next_run_in_second = 0
        while True:
            if time.time() >= next_run_in_second:
                now = time.time()
                next_run_in_second = now + self.interval_in_second
                # run here
                cluster_name = EsMonitorTimer.go(self)
                elapsed = time.time() - now
                print("this is the cluster_name=%s, now=%s, Total Elapsed Time: %s" % (cluster_name, datetime.datetime.now(), elapsed))
                LOG.info("this is the cluster_name=%s, now=%s, Total Elapsed Time: %s" % (cluster_name, datetime.datetime.now(), elapsed))
                time_diff = next_run_in_second - time.time()
                # Check timediff , if timediff >=0 sleep, if < 0 send metrics to es
                if time_diff >= 0:
                    time.sleep(time_diff)


def main(argv):
    es_host_port_list_to_monitor = argv[1]  # ElasticSearch Cluster to Monitor, use a comma to split
    es_host_port_to_storage = argv[2]  # ElasticSearch Cluster to Send Metrics
    es_index_to_storage = argv[3]  # ElasticSearch index to save Metrics && feed metric to Grafana Data Sources
    interval_in_second = int(argv[4])
    LOG.info("this is the es_host_port_list_to_monitor=%s, es_host_port_to_storage=%s, es_index_to_storage=%s, interval_in_second=%s" % (
        es_host_port_list_to_monitor, es_host_port_to_storage, es_index_to_storage, interval_in_second))

    # executor, need multiprocessing, since `while true`
    for es_host_port_to_monitor in es_host_port_list_to_monitor.split(","):
        EsMonitorTimer(es_host_port_to_monitor.strip(), es_host_port_to_storage.strip(), es_index_to_storage.strip(), interval_in_second).start()  # scheduler


def usage():
    print """usage end"""
    print """python collect_es_metric_to_grafana_esdb.py srcServer1:port,srcServer1:port,srcServer1:port destServer:port your_index_name 60"""
    print """python collect_es_metric_to_grafana_esdb.py localhost:9200,localhost:9202 localhost:9200 es_metric_collect 10"""
    print """usage end"""


if __name__ == '__main__':
    try:
        LOG.info("\n\n\n\n\n\n\n")
        LOG.info("----> Another new start <----")
        main(sys.argv)
    except Exception, e:
        usage()
        LOG.error(e)

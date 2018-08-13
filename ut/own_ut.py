# -*- coding: utf-8 -*-

import json
import time
import unittest

from grafana import own_settings
from grafana.own_util import DateUtil, Util


class UtilTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        print(">>>> Here is the begin at: %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
        print

    @classmethod
    def tearDownClass(self):
        print(">>>> Here is the   end at: %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
        # delete all the unittest_test_index index
        print

    def test_get_current_time_str(self):
        current_time_str = DateUtil.get_current_time_str()
        print("current_time_str=%s" % current_time_str)
        self.assertIsNotNone(current_time_str)

    def test_read_data_from_src(self):
        url = "localhost:9200/_cat/health"
        resp = Util.read_data_from_src(url)
        print(resp.getcode())
        self.assertTrue(resp.getcode() == 200)

    def test_send_data_to_dest(self):
        url = "%s/%s" % ("localhost:9200", own_settings.index_name + "t1")
        index_mapping = {"settings": {}}
        index_mapping["settings"]["index"] = {}
        index_mapping["settings"]["index"]["number_of_shards"] = 1
        index_mapping["settings"]["index"]["number_of_replicas"] = 0
        resp = Util.send_data_to_dest(url, index_mapping, put_method=True)
        print(resp.read())
        self.assertTrue(resp.getcode() == 200)


from grafana.collect_es_metric_to_grafana_esdb import EsMonitorMetric


class TestEsMonitorMetric(unittest.TestCase):

    def test_create_index(self):
        resp = EsMonitorMetric.create_index(own_settings.es_server_to_monitor, own_settings.index_name + "t2")
        print("resp.getcode=%s" % resp.getcode())
        self.assertTrue(resp.getcode() == 200)

    def test_fetch_cluster_health(self):
        resp = EsMonitorMetric.fetch_cluster_health(own_settings.es_server_to_monitor)
        print(json.dumps(resp))
        self.assertTrue(resp[1]["number_of_pending_tasks"] >= 0)

    def test_fetch_cluster_stats(self):
        resp = EsMonitorMetric.fetch_cluster_stats(own_settings.es_server_to_monitor)
        print(json.dumps(resp))
        self.assertTrue(resp["status"] in ["green", "yellow", "red"])

    def test_fetch_node_stats(self):
        resp = EsMonitorMetric.fetch_node_stats(own_settings.es_server_to_monitor, "c5-es-540")
        print(json.dumps(resp))
        self.assertTrue(resp[0]["thread_pool"]["force_merge"]["largest"] >= 0)

    def test_fetch_index_stats(self):
        resp = EsMonitorMetric.fetch_index_stats(own_settings.es_server_to_monitor, "c5-es-540")
        print(json.dumps(resp))
        self.assertTrue(resp["total"]["segments"]["count"] >= 0)

# -*- coding: utf-8 -*-

import time
import unittest

from grafana.collect_es_metric_to_grafana_esdb import EsMonitorUtil


class EsUtilTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        print(">>>> Here is the begin at: %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
        print

    @classmethod
    def tearDownClass(self):
        print(">>>> Here is the   end at: %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
        print

    def test_create_index(self):
        es_server_to_monitor, index_name, type_name = "localhost:9200", "es_metric_collect_2018-08-17", "msg"
        resp = EsMonitorUtil.create_index(es_server_to_monitor, index_name, type_name)
        print("resp.getcode=%s" % resp.getcode())
        self.assertTrue(resp.getcode() == 200)

    def test_fetch_clusterhealth(self):
        es_server_to_monitor = "http://localhost:9200"
        resp = EsMonitorUtil.fetch_clusterhealth(es_server_to_monitor)
        print(resp)
        print(type(resp))

    def test_fetch_clusterstats(self):
        """
        {u'status': u'green', u'cluster_name': u'c5-es-540', u'timestamp': 1534144552426L, '@timestamp': '2018-08-13T07:15:52.399', u'_nodes': {u'successful': 2, u'failed': 0, u'total': 2}, u'indices': {u'count': 9, u'completion': {u'size_in_bytes': 0}, u'fielddata': {u'evictions': 0, u'memory_size_in_bytes': 0}, u'docs': {u'count': 57, u'deleted': 0}, u'segments': {u'count': 20, u'max_unsafe_auto_id_timestamp': 1533991056898L, u'term_vectors_memory_in_bytes': 0, u'version_map_memory_in_bytes': 0, u'norms_memory_in_bytes': 1280, u'stored_fields_memory_in_bytes': 6240, u'file_sizes': {}, u'doc_values_memory_in_bytes': 2080, u'fixed_bit_set_memory_in_bytes': 0, u'points_memory_in_bytes': 26, u'terms_memory_in_bytes': 99126, u'memory_in_bytes': 108752, u'index_writer_memory_in_bytes': 0}, u'shards': {u'replication': 0.0, u'total': 27, u'primaries': 27, u'index': {u'replication': {u'max': 0.0, u'avg': 0.0, u'min': 0.0}, u'primaries': {u'max': 5, u'avg': 3.0, u'min': 1}, u'shards': {u'max': 5, u'avg': 3.0, u'min': 1}}}, u'query_cache': {u'miss_count': 0, u'total_count': 0, u'evictions': 0, u'memory_size_in_bytes': 0, u'hit_count': 0, u'cache_size': 0, u'cache_count': 0}, u'store': {u'size_in_bytes': 198862, u'throttle_time_in_millis': 0}}, u'nodes': {u'count': {u'master': 2, u'total': 2, u'data': 2, u'coordinating_only': 0, u'ingest': 2}, u'fs': {u'free_in_bytes': 315695865856L, u'total_in_bytes': 319446577152L, u'available_in_bytes': 315695865856L}, u'versions': [u'5.4.0'], u'process': {u'open_file_descriptors': {u'max': -1, u'avg': 0, u'min': -1}, u'cpu': {u'percent': 0}}, u'network_types': {u'transport_types': {u'netty4': 2}, u'http_types': {u'netty4': 2}}, u'jvm': {u'mem': {u'heap_used_in_bytes': 807355616, u'heap_max_in_bytes': 2075918336}, u'threads': 186, u'max_uptime_in_millis': 155504159, u'versions': [{u'vm_name': u'Java HotSpot(TM) 64-Bit Server VM', u'count': 2, u'version': u'10.0.1', u'vm_version': u'10.0.1+10', u'vm_vendor': u'"Oracle Corporation"'}]}, u'plugins': [], u'os': {u'mem': {u'free_in_bytes': 14461313024L, u'free_percent': 42, u'used_in_bytes': 19663527936L, u'total_in_bytes': 34124840960L, u'used_percent': 58}, u'allocated_processors': 16, u'names': [{u'count': 2, u'name': u'Windows 10'}], u'available_processors': 16}}}
        <type 'dict'>
        :return:
        """
        es_server_to_monitor = "http://localhost:9200"
        resp = EsMonitorUtil.fetch_clusterstats(es_server_to_monitor)
        print(resp)
        print(type(resp))

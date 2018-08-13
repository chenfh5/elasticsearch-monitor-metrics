# -*- coding: utf-8 -*-

import datetime
import json
import multiprocessing
import sys
import time
import urllib
import urllib2

import settings
from es_log import LOG


class EsMonitorUtil(object):

    @staticmethod
    def handle_urlopen(urldata, read_username, read_password):
        if settings.read_es_security_enable:
            try:
                password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                password_mgr.add_password(None, urldata, read_username, read_password)
                handler = urllib2.HTTPBasicAuthHandler(password_mgr)
                opener = urllib2.build_opener(handler)
                urllib2.install_opener(opener)
                response = urllib2.urlopen(urldata)
                return response
            except Exception as e:
                LOG.info("Error:  {0}".format(str(e)))
        else:
            try:
                response = urllib.urlopen(urldata)
                return response
            except Exception as e:
                LOG.info("Error:  {0}".format(str(e)))

    @staticmethod
    def create_index(es_server_to_monitor, es_index_to_storage):
        import requests
        index_mapping = {"mappings": {}}
        index_mapping["mappings"]["message"] = {}
        mapping = dict(type='keyword', norms='false')
        strings_as_keywords = dict(match_mapping_type='string', mapping=mapping)
        strings_as_keywords = dict(strings_as_keywords=strings_as_keywords)
        dynamic_templates = [strings_as_keywords]
        index_mapping["mappings"]["message"]["dynamic_templates"] = dynamic_templates
        index_mapping["settings"] = {}
        index_mapping["settings"]["index"] = {}
        index_mapping["settings"]["index"]["number_of_shards"] = 1
        index_mapping["settings"]["index"]["number_of_replicas"] = 0

        index_mapping_str = json.dumps(index_mapping)
        index_name = "%s-%s" % (es_index_to_storage, str(datetime.datetime.utcnow().strftime('%Y.%m.%d')))
        resp = requests.put(url="%s/%s" % (es_server_to_monitor, index_name), json=json.loads(index_mapping_str), headers={'Content-Type': 'application/json'})
        return resp.status_code

    @staticmethod
    def fetch_clusterhealth(es_server_to_monitor):
        try:
            utc_datetime = datetime.datetime.utcnow()
            endpoint = "/_cluster/health"
            urldata = es_server_to_monitor + endpoint
            response = EsMonitorUtil.handle_urlopen(urldata, settings.read_username, settings.read_password)
            jsondata = json.loads(response.read())
            cluster_name = jsondata['cluster_name']
            jsondata['@timestamp'] = str(utc_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3])
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
    def fetch_clusterstats(es_server_to_monitor):
        utc_datetime = datetime.datetime.utcnow()
        endpoint = "/_cluster/stats"
        urldata = es_server_to_monitor + endpoint
        response = EsMonitorUtil.handle_urlopen(urldata, settings.read_username, settings.read_password)
        jsondata = json.loads(response.read())
        jsondata['@timestamp'] = str(utc_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3])
        return jsondata

    @staticmethod
    def fetch_nodestats(es_server_to_monitor, cluster_name):
        utc_datetime = datetime.datetime.utcnow()
        endpoint = "/_cat/nodes?v&h=n"
        urldata = es_server_to_monitor + endpoint
        response = EsMonitorUtil.handle_urlopen(urldata, settings.read_username, settings.read_password)
        nodes = response.read()[1:-1].strip().split('\n')
        for node in nodes:
            endpoint = "/_nodes/%s/stats" % node.rstrip()
            urldata = es_server_to_monitor + endpoint
            response = EsMonitorUtil.handle_urlopen(urldata, settings.read_username, settings.read_password)
            jsondata = json.loads(response.read())
            nodeID = jsondata['nodes'].keys()
            try:
                jsondata['nodes'][nodeID[0]]['@timestamp'] = str(utc_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3])
                jsondata['nodes'][nodeID[0]]['cluster_name'] = cluster_name
                new_jsondata = jsondata['nodes'][nodeID[0]]
                return new_jsondata
            except:
                continue

    @staticmethod
    def fetch_indexstats(es_server_to_monitor, cluster_name):
        utc_datetime = datetime.datetime.utcnow()
        endpoint = "/_stats"
        urldata = es_server_to_monitor + endpoint
        response = EsMonitorUtil.handle_urlopen(urldata, settings.read_username, settings.read_password)
        jsondata = json.loads(response.read())
        jsondata['_all']['@timestamp'] = str(utc_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3])
        jsondata['_all']['cluster_name'] = cluster_name
        return jsondata['_all']

    @staticmethod
    def send_data_to_dest(es_server_to_storage, es_index_to_storage, data):
        utc_datetime = datetime.datetime.utcnow()
        url_parameters = {'cluster': es_server_to_storage, 'index': es_index_to_storage,
                          'index_period': utc_datetime.strftime("%Y.%m.%d"), }
        url = "%(cluster)s/%(index)s-%(index_period)s/message" % url_parameters
        headers = {'content-type': 'application/json'}
        try:
            req = urllib2.Request(url, headers=headers, data=json.dumps(data))
            if settings.write_es_security_enable:
                password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                password_mgr.add_password(None, url, settings.write_username, settings.write_password)
                handler = urllib2.HTTPBasicAuthHandler(password_mgr)
                opener = urllib2.build_opener(handler)
                urllib2.install_opener(opener)
                response = urllib2.urlopen(req)
            else:
                response = urllib2.urlopen(req)
        except Exception, e:
            LOG.info("Error:  {0}".format(str(e)))


class EsMonitor(multiprocessing.Process):
    def __init__(self, es_server_to_monitor, es_server_to_storage, es_index_to_storage, interval_in_second=60):
        super(EsMonitor, self).__init__()
        self.es_server_to_monitor = es_server_to_monitor
        self.es_server_to_storage = es_server_to_storage
        self.es_index_to_storage = es_index_to_storage
        self.interval_in_second = interval_in_second

    def go(self):
        EsMonitorUtil.create_index(self.es_server_to_monitor, self.es_index_to_storage)
        cluster_name, jsondata = EsMonitorUtil.fetch_clusterhealth(self.es_server_to_monitor)
        if cluster_name != "unknown":
            clusterstats = EsMonitorUtil.fetch_clusterstats(self.es_server_to_monitor)
            nodestats = EsMonitorUtil.fetch_nodestats(self.es_server_to_monitor, cluster_name)
            indexstats = EsMonitorUtil.fetch_indexstats(self.es_server_to_monitor, cluster_name)
            for one_jsondata in [jsondata, clusterstats, nodestats, indexstats]:
                EsMonitorUtil.send_data_to_dest(self.es_server_to_storage, self.es_index_to_storage, one_jsondata)
        return cluster_name

    def run(self):
        next_run_in_second = 0
        while True:
            if time.time() >= next_run_in_second:
                now = time.time()
                next_run_in_second = now + self.interval_in_second
                # run here
                cluster_name = EsMonitor.go(self)
                elapsed = time.time() - now
                print("this is the cluster_name=%s, now=%s, Total Elapsed Time: %s" % (cluster_name, datetime.datetime.now(), elapsed))
                LOG.info("this is the cluster_name=%s, now=%s, Total Elapsed Time: %s" % (cluster_name, datetime.datetime.now(), elapsed))
                time_diff = next_run_in_second - time.time()

                # Check timediff , if timediff >=0 sleep, if < 0 send metrics to es
                if time_diff >= 0:
                    time.sleep(time_diff)


def main(argv):
    # argparse would be better, but not the build-in module
    es_servers_to_monitor = argv[1]
    es_server_to_storage = argv[2]
    es_index_to_storage = argv[3]
    interval_in_second = int(argv[4])
    LOG.info("this is the es_servers_to_monitor=%s, es_server_to_storage=%s, es_index_to_storage=%s, interval_in_second=%s" % (
        es_servers_to_monitor, es_server_to_storage, es_index_to_storage, interval_in_second))

    # need multiprocessing, since `while true`
    # http://www.runoob.com/python/python-multithreading.html
    for es_server_to_monitor in es_servers_to_monitor.split(","):
        EsMonitor("http://" + es_server_to_monitor.strip(), "http://" + es_server_to_storage.strip(), es_index_to_storage.strip(), interval_in_second).start()  # scheduler


def usage():
    print """usage end"""
    print """not need http://, only host:port"""
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

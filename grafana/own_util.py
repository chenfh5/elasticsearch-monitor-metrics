# -*- coding: utf-8 -*-

import datetime
import json
import urllib2

from grafana import own_settings
from own_log import LOG


class Util(object):

    @staticmethod
    def read_data_from_src(url):
        url = "http://" + url
        if own_settings.read_es_security_enable:
            try:
                password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                password_mgr.add_password(None, url, own_settings.read_username, own_settings.read_password)
                handler = urllib2.HTTPBasicAuthHandler(password_mgr)
                opener = urllib2.build_opener(handler)
                urllib2.install_opener(opener)
                response = urllib2.urlopen(url)
                return response
            except Exception, e:
                LOG.info("Error:  {0}".format(str(e)))
        else:
            try:
                response = urllib2.urlopen(url)
                return response
            except Exception, e:
                LOG.info("Error:  {0}".format(str(e)))

    @staticmethod
    def send_data_to_dest(url, data, put_method):
        url = "http://" + url
        headers = {'content-type': 'application/json'}
        try:
            req = urllib2.Request(url, headers=headers, data=json.dumps(data))
            if put_method:
                req.get_method = lambda: "PUT"
            if own_settings.write_es_security_enable:
                password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                password_mgr.add_password(None, url, own_settings.write_username, own_settings.write_password)
                handler = urllib2.HTTPBasicAuthHandler(password_mgr)
                opener = urllib2.build_opener(handler)
                urllib2.install_opener(opener)
                response = urllib2.urlopen(req)
                return response
            else:
                response = urllib2.urlopen(req)
                return response
        except Exception, e:
            LOG.info("Error:  {0}".format(str(e)))


class DateUtil(object):

    @staticmethod
    def get_current_time_str():
        """
        https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-date-format.html
        """
        # Elasticsearch uses a set of preconfigured formats to recognize and parse these strings
        # into a long value representing milliseconds-since-the-epoch in UTC
        # Therefore, here we should use UTC, not your local time.
        # But in grafana, the filter use local time. And the filter would convert by es internal
        # And yes, you can use the build-in formats to special your `timestamp` field to match your local time
        return str(datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3])
        # return str(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3])

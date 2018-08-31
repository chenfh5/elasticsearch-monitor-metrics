# -*- coding: utf-8 -*-

# Enable Elasticsearch Security
# read_username and read_password for read ES cluster information
# write_username and write_passowrd for write monitor metric to ES.
import base64
import time

def encode(raw_str):
    return base64.b64encode(raw_str)  # b64encode vs b64decode


def decode(encode_str):
    return base64.b64decode(encode_str)  # b64encode vs b64decode


read_es_security_enable = False
read_username = decode("read_username_b64encode")
read_password = decode("read_password_b64encode")

write_es_security_enable = False
write_username = decode("write_username_b64encode")
write_password = decode("write_password_b64encode")

# es type setting (in 6.0+, type should be _doc)
type_name = "doc"

# unit test setting
es_server_to_monitor = "localhost:9200"
index_name = "%s_%s" % ("unittest_test_index", time.strftime("%Y-%m-%d-%H-%M-%S"))  # second precision

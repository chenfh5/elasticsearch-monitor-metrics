# -*- coding: utf-8 -*-

# Enable Elasticsearch Security
# read_username and read_password for read ES cluster information
# write_username and write_passowrd for write monitor metric to ES.
read_es_security_enable = False
read_username = "read_username"
read_password = "read_password"

write_es_security_enable = False
write_username = "write_username"
write_password = "write_password"

# es type setting (in 6.0+, type should be _doc)
type_name = "doc"

# unit test setting
es_server_to_monitor = "localhost:9200"
import time

index_name = "%s_%s" % ("unittest_test_index", time.strftime("%Y-%m-%d-%H-%M-%S"))  # second precision

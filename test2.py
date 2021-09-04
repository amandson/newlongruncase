import hmac
import json
import base64
import datetime
from hashlib import sha256
from collections import OrderedDict
import urllib.request, urllib.error, urllib.parse

class QingApi:
    def __init__(self):
        self.access_key_id = 'ILMCPQNSCKSXTFAAONCK'
        self.secret_access_key = 'YUCtLmWMVWHXosCFkRN8m1XyhphAQcRfaNob09li'
        self.time_stamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.url = "https://api.qingcloud.com/iaas/"
        self.url_path = '/iaas/'
        self.methods = 'GET'

    def postResust(self, iassurl):
        req = urllib.request.Request(iassurl)
        result = urllib.request.urlopen(req)
        response = json.loads(result.read().decode())
        print(response)

    def getVhost(self):
        od = OrderedDict()
        od['access_key_id'] = self.access_key_id
        od['action'] = "DescribeInstances"
        od['signature_method'] = "HmacSHA256"
        od['signature_version'] = 1
        od['time_stamp'] = self.time_stamp
        od['version'] = 1
        od['zone'] = "pek3"

        od['instances.1'] = "i-ut8tg89y"

        od = self.sort_value(od)
        data = urllib.parse.urlencode(od)
        string_to_sign = self.methods + "\n" + self.url_path + "\n" + data
        h = hmac.new(self.secret_access_key.encode(), digestmod=sha256)
        h.update(string_to_sign.encode())
        sign = base64.b64encode(h.digest()).strip()
        signature = urllib.parse.quote_plus(sign)
        print("signature是:"+signature)
        iaasUrl = self.url + "?" + data + "&signature=" + signature
        print(iaasUrl)
        self.postResust(iaasUrl)

    def create_robbitemq(self):
        cd = OrderedDict()
        cd['access_key_id'] = self.access_key_id
        cd['action'] = "DeployAppVersion"
        cd['signature_method'] = "HmacSHA256"
        cd['signature_version'] = 1
        cd['time_stamp'] = self.time_stamp
        cd['version'] = 1
        cd['zone'] = "pek3"

        cd['app_type'] = "cluster"
        cd['app_id'] = "app-n28v5lhg"
        cd['version_id'] = "appv-9lxsx5fi"
        cd['conf'] = "{\"cluster\":{\"name\":\"RabbitMQ\",\"description\":\"\",\"disc\":{\"cpu\":2,\"memory\":4096,\"instance_class\":202,\"volume_size\":10,\"count\":3},\"ram\":{\"cpu\":2,\"memory\":2048,\"instance_class\":202,\"volume_size\":10,\"count\":0},\"client\":{\"cpu\":1,\"memory\":1024,\"instance_class\":101,\"count\":1},\"haproxy\":{\"cpu\":2,\"memory\":2048,\"instance_class\":101,\"count\":2},\"vxnet\":\"vxnet-if6lpa8\",\"global_uuid\":\"82632219872695450\",\"add_port_to_sg\":1},\"version\":\"appv-9lxsx5fi\",\"resource_group\":\"Prod\",\"zone\":\"pek3\",\"vpc\":\"rtr-6oadkgh5\",\"env\":{\"rabbitmq_default_user\":\"guest\",\"rabbitmq_default_pass\":\"Zhu88jie\",\"haproxy_balance_policy\":\"roundrobin\",\"haproxy_web_port\":8100,\"haproxy_username\":\"haproxy\",\"haproxy_password\":\"haproxy\",\"num_tcp_acceptors\":10,\"handshake_timeout\":10000,\"vm_memory_high_watermark\":0.4,\"vm_memory_high_watermark_paging_ratio\":0.5,\"disk_free_limit\":50000000,\"frame_max\":131072,\"channel_max\":0,\"heartbeat\":60,\"collect_statistics\":\"none\",\"collect_statistics_interval\":5000,\"cluster_partition_handling\":\"pause_minority\",\"hipe_compile\":false,\"cluster_keepalive_interval\":10000,\"background_gc_target_interval\":60000,\"background_gc_enabled\":false,\"reverse_dns_lookups\":false,\"tracing_user\":\"guest\",\"proxy_protocol\":false,\"web_console_enabled\":false,\"web_console_username\":\"admin\"}}"
        cd['charge_mode'] ="elastic"
        cd['debug'] = 0
        cd['owner'] = "usr-JmZCZBRQ"

        cd = self.sort_value(cd)
        data = urllib.parse.urlencode(cd)
        string_to_sign = self.methods + "\n" + self.url_path + "\n" + data
        h = hmac.new(self.secret_access_key.encode(), digestmod=sha256)
        h.update(string_to_sign.encode())
        sign = base64.b64encode(h.digest()).strip()
        signature = urllib.parse.quote_plus(sign)
        print("signature是:" + signature)
        iaasUrl = self.url + "?" + data + "&signature=" + signature
        print(iaasUrl)
        self.postResust(iaasUrl)

    def sort_value(self, old_dict):
        items = sorted(old_dict.items())
        new_dict = OrderedDict()
        for item in items:
            new_dict[item[0]] = old_dict[item[0]]
        return new_dict

if __name__ == '__main__':
    x = QingApi()
    x.create_robbitemq()
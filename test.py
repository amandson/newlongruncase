import base64
import hmac
import urllib.request, urllib.parse, urllib.error
import urllib.parse
import time
import random
from hashlib import sha256
import sys
import json
import pytest
import allure
import requests


# test_conf = {}
# try:
#     conf_path = "createcluster.json"
#     with open(conf_path, "r") as f:
#         test_conf = json.load(f)
# except Exception() as e:
#     print(e)
#     sys.exit(1)


test_conf = {}
try:
    conf_path = "createcluster.json"
    with open(conf_path, "r",encoding='utf-8') as f:
        test_conf = json.load(f)
except Exception() as e:
    print(e)
    sys.exit(1)

name = str(test_conf['cluster']['name'])
description = str(test_conf['cluster']['description'])
cpu =test_conf['cluster']['disc']['cpu']
memory=test_conf['cluster']['disc']['memory']
instance_class=test_conf['cluster']['disc']['instance_class']
volume_size=test_conf['cluster']['disc']['volume_size']
count=test_conf['cluster']['disc']['count']
cpu=test_conf['cluster']['client']['cpu']
memory=test_conf['cluster']['client']['memory']
instance_class=test_conf['cluster']['client']['instance_class']
count=test_conf['cluster']['client']['count']
cpu=test_conf['cluster']['haproxy']['cpu']
memory=test_conf['cluster']['haproxy']['memory']
instance_class=test_conf['cluster']['haproxy']['instance_class']
volume_size=test_conf['cluster']['haproxy']['volume_size']
count=test_conf['cluster']['haproxy']['count']
vxnet=str(test_conf['cluster']['vxnet'])
etcd_service=str(test_conf['cluster']['etcd_service'])
global_uuid=str(test_conf['cluster']['global_uuid'])
version=str(test_conf['version'])
resource_group=str(test_conf['resource_group'])
vpc=str(test_conf['vpc'])
rabbitmq_default_user=str(test_conf['env']['rabbitmq_default_user'])
rabbitmq_default_pass=str(test_conf['env']['rabbitmq_default_pass'])
haproxy_balance_policy=str(test_conf['env']['haproxy_balance_policy'])
haproxy_web_port=test_conf['env']['haproxy_web_port']
haproxy_username=str(test_conf['env']['haproxy_username'])
haproxy_password=str(test_conf['env']['haproxy_password'])
num_tcp_acceptors=test_conf['env']['num_tcp_acceptors']
handshake_timeout=test_conf['env']['handshake_timeout']
vm_memory_high_watermark=test_conf['env']['vm_memory_high_watermark']
vm_memory_high_watermark_paging_ratio=test_conf['env']['vm_memory_high_watermark_paging_ratio']
disk_free_limit=test_conf['env']['disk_free_limit']
frame_max=test_conf['env']['frame_max']
channel_max=test_conf['env']['channel_max']
heartbeat=test_conf['env']['heartbeat']
collect_statistics=str(test_conf['env']['collect_statistics'])
collect_statistics_interval=test_conf['env']['collect_statistics_interval']
cluster_partition_handling=str(test_conf['env']['cluster_partition_handling'])
hipe_compile=test_conf['env']['hipe_compile']
cluster_keepalive_interval=test_conf['env']['cluster_keepalive_interval']
background_gc_target_interval=test_conf['env']['background_gc_target_interval']
background_gc_enabled=test_conf['env']['background_gc_enabled']
reverse_dns_lookups=test_conf['env']['reverse_dns_lookups']
tracing_user=test_conf['env']['tracing_user']
proxy_protocol=test_conf['env']['proxy_protocol']
web_console_enabled=test_conf['env']['web_console_enabled']

print(test_conf)
# test_conf=json.dumps(test_conf)
json_data=str(urllib.parse.urlencode(test_conf))
print(json_data)


# description =str(test_conf['cluster']['description'])
# listener =str(test_conf['cluster']['tomcat_nodes']['loadbalancer'][0]['listener'])
# port=test_conf['cluster']['tomcat_nodes']['loadbalancer'][0]['port']
# policy=str(test_conf['cluster']['tomcat_nodes']['loadbalancer'][0]['policy'])
# cpu=test_conf['cluster']['tomcat_nodes']['cpu']
# memory=test_conf['cluster']['tomcat_nodes']['memory']
# instance_class=test_conf['cluster']['tomcat_nodes']['instance_class']
# count=test_conf['cluster']['tomcat_nodes']['count']
# volume_size=test_conf['cluster']['tomcat_nodes']['count']
# cpu=test_conf['cluster']['log_node']['cpu']
# memory=test_conf['cluster']['log_node']['memory']
# instance_class=test_conf['cluster']['log_node']['instance_class']
# volume_size=test_conf['cluster']['log_node']['volume_size']
# vxnet=str(test_conf['cluster']['vxnet'])
# global_uuid=str(test_conf['cluster']['global_uuid'])
# version=str(test_conf['version'])
# tomcat_user=str(test_conf['env']['tomcat_user'])
# tomcat_pwd=str(test_conf['env']['tomcat_pwd'])
# tomcat_encoding=str(test_conf['env']['tomcat_encoding'])
# tomcat_log_level=str(test_conf['env']['tomcat_log_level'])
# threadpool_maxThreads=str(test_conf['env']['threadpool_maxThreads'])
# threadpool_minSpareThreads=str(test_conf['env']['threadpool_minSpareThreads'])
# threadpool_maxIdleTime=str(test_conf['env']['threadpool_maxIdleTime'])
# war_source=str(test_conf['env']['war_source'])
# tomcat_log_packages=str(test_conf['env']['tomcat_log_packages'])
# java_opts=str(test_conf['env']['java_opts'])
# redis_db_num=str(test_conf['env']['redis_db_num'])
# access_key_id=str(test_conf['env']['access_key_id'])
# zone=str(test_conf['env']['zone'])
# bucket=str(test_conf['env']['bucket'])
# war_name=str(test_conf['env']['war_name'])
# mysql_db_name=str(test_conf['env']['mysql_db_name'])
# jdbc_dsname=str(test_conf['env']['jdbc_dsname'])
# jdbc_maxActive=str(test_conf['env']['jdbc_maxActive'])
# jdbc_maxIdle=str(test_conf['env']['jdbc_maxIdle'])
# jdbc_maxWait=str(test_conf['env']['jdbc_maxWait'])

access_key_id = "HEHYLNIKVMQLUQMBBZYD"
secret_access_key ="AFt3dkVdmjpnb73VHA1erhF8hPjhAWagtqQ0qdFa"


def get_common_params():
    params = {"access_key_id": access_key_id,
              "limit": '100',
              "signature_method": 'HmacSHA256',
              "signature_version": '1',
              "version": "1",
              'expires': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() + 30)),
              'time_stamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time()))}
    # params['cluster'] = 'cl-v1dbfgum'
    return params


def wait_job_done(jod_id, cluster, timeout=600):
    params = get_common_params()
    params['action'] = "DescribeJobs"
    params['jobs.1'] = jod_id
    params['resource_ids'] = cluster
    print(jod_id, cluster)
    while timeout > 0:
        timeout -= 2

        params['expires'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() + 30))  # UTC
        params['time_stamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time()))  # UTC
        order_params = [(k, params[k]) for k in sorted(params.keys())]
        body = urllib.parse.urlencode(order_params)
        signature = generate_signature(body, secret_access_key)

        url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
        # print url
        res = requests.get(url)
        ret_json = res.json()
        if ('job_set' in ret_json) == False:
            print("error", ret_json)
            return -1
        else:
            if ret_json['job_set'][0]['status'] == "failed":
                return -1
            if ret_json['job_set'][0]['status'] == "successful":
                return 0
        time.sleep(3)
    print("wait_job_done timeout")
    return -1



def generate_signature(body, secret_access_key):
    string_to_sign = 'GET\n/iaas/\n' + body
    secret_access_key = bytes(secret_access_key, encoding='utf-8')
    h = hmac.new(secret_access_key, digestmod=sha256)
    h.update(string_to_sign.encode("utf-8"))
    sign = base64.b64encode(h.digest()).strip()
    signature = urllib.parse.quote_plus(sign)
    return signature


if __name__=="__main__":
    # params=get_common_params()
    # params['action'] = "DeployAppVersion"
    # params['conf']="{\"cluster\":{\"name\":\"RabbitMQ集群\",\"description\":\"测试测试不要删\",\"disc\":{\"cpu\":1,\"memory\":1024,\"instance_class\":101,\"volume_size\":10,\"count\":3},\"client\":{\"cpu\":1,\"memory\":1024,\"instance_class\":101,\"count\":1},\"haproxy\":{\"cpu\":1,\"memory\":1024,\"instance_class\":101,\"volume_size\":10,\"count\":2},\"vxnet\":\"vxnet-71dxram\",\"etcd_service\":\"cl-k1my87gj\",\"global_uuid\":\"08632219872689231\"},\"version\":\"appv-spejlhjj\",\"resource_group\":\"Test\",\"vpc\":\"rtr-m7nomv0c\",\"env\":{\"rabbitmq_default_user\":\"guest\",\"rabbitmq_default_pass\":\"Wm881011\",\"haproxy_balance_policy\":\"roundrobin\",\"haproxy_web_port\":8100,\"haproxy_username\":\"haproxy\",\"haproxy_password\":\"haproxy\",\"num_tcp_acceptors\":10,\"handshake_timeout\":10000,\"vm_memory_high_watermark\":0.4,\"vm_memory_high_watermark_paging_ratio\":0.5,\"disk_free_limit\":524288000,\"frame_max\":131072,\"channel_max\":0,\"heartbeat\":60,\"collect_statistics\":\"none\",\"collect_statistics_interval\":5000,\"cluster_partition_handling\":\"pause_minority\",\"hipe_compile\":false,\"cluster_keepalive_interval\":10000,\"background_gc_target_interval\":60000,\"background_gc_enabled\":false,\"reverse_dns_lookups\":false,\"tracing_user\":\"guest\",\"proxy_protocol\":false,\"web_console_enabled\":true}}"
    # params['app_type']="cluster"
    # params['app_id']="app-n28v5lhg"
    # params['version_id']="appv-spejlhjj"
    # params['zone']="pek3a"
    # params['debug']=1
    # params['version']=1

    params = get_common_params()
    params['action'] = "DeleteClusters"
    params['clusters.1'] = "cl-z7705e5b"
    params['zone'] = "pek3a"
    params['debug'] = 1




    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.parse.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)

    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature

    print(url)
    res = requests.get(url)
    ret_json = res.json()
    print(ret_json)

    # ret_json=json.dumps(ret_json,indent=4,ensure_ascii=False)
    # with open('createcluster.json','w',encoding='utf8') as f:
    #     f.write(ret_json)

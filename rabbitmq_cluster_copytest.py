#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import hmac
import urllib.request, urllib.parse, urllib.error
import urllib.parse
import time
import random
from hashlib import sha256
import sys
import json

import pika
import pytest
import allure
import requests
from yaml_util import yamlUtil
from rabbitmq_connect import RabbitMQ_Con

test_conf = {}
try:
    conf_path = "config.json"
    with open(conf_path, "r") as f:
        test_conf = json.load(f)
except Exception() as e:
    print(e)
    sys.exit(1)

access_key_id = str(test_conf['access_key_id'])
secret_access_key = str(test_conf['secret_access_key'])
zone = str(test_conf['zone'])
cluster_id = str(test_conf['cluster']['cluster-a'])
cluster_b_id = str(test_conf['cluster']['cluster-b'])
cluster_a_wvip = str(test_conf['cluster']['cluster-a-wvip'])
cluster_b_wvip = str(test_conf['cluster']['cluster-b-wvip'])
cluster_user = str(test_conf['cluster']['cluster_user'])
cluster_paawd = str(test_conf['cluster']['cluster_passwd'])
vxnet_a = str(test_conf['vpc']['vxnet']['vxnet-a'])
vxnet_b = str(test_conf['vpc']['vxnet']['vxnet-b'])



ri_node_ids = ['cln-3ojmilbm']
mi_node_ids = []
proxy_node_ids = []

access_key_id = "HEHYLNIKVMQLUQMBBZYD"
secret_access_key ="AFt3dkVdmjpnb73VHA1erhF8hPjhAWagtqQ0qdFa"
cluster=""

@pytest.fixture(scope='function')
def context():
    return {}


#

    # global cluster
    # print(cluster)
    # return cluster


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


def generate_signature_new(data, secret_access_key):
    string_to_sign = "GET" + "\n" + '/iaas/' + "\n" + data
    h = hmac.new(secret_access_key.encode(), digestmod=sha256)
    h.update(string_to_sign.encode())
    sign = base64.b64encode(h.digest()).strip()
    signature = urllib.parse.quote_plus(sign)
    iaasUrl = '/iaas/' + "?" + data + "&signature=" + signature
    return iaasUrl


def generate_signature(body, secret_access_key):
    string_to_sign = 'GET\n/iaas/\n' + body
    secret_access_key = bytes(secret_access_key, encoding='utf-8')
    h = hmac.new(secret_access_key, digestmod=sha256)
    h.update(string_to_sign.encode("utf-8"))
    sign = base64.b64encode(h.digest()).strip()
    signature = urllib.parse.quote_plus(sign)
    return signature


# def describle_cluster(cluster):
#     params = get_common_params()
#     params['action'] = "DescribeClusters"
#     params['clusters.1'] = cluster
#     params['zone'] ="pek3a"
#
#     order_params = [(k, params[k]) for k in sorted(params.keys())]
#     body = urllib.parse.urlencode(order_params)
#     signature = generate_signature(body, secret_access_key)
#
#     url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
#
#     res = requests.get(url)
#     ret_json = res.json()
#     print(ret_json)
#     # [0]['status']
#     status = ret_json['cluster_set'][0]['status']
#     print(status)
#     return status


# def describle_cluster_proxy_ip(cluster):
#     # {"status":{"add_port_to_sg":true,"protocol":"tcp","port":8100},"client":{"add_port_to_sg":true,"protocol":"tcp","port":5672},"reserved_ips":{"vip":{"value":"192.168.0.253"}}}
#
#     params = get_common_params()
#     params['action'] = "DescribeClusters"
#     params['clusters.1'] = cluster
#
#     order_params = [(k, params[k]) for k in sorted(params.keys())]
#     body = urllib.parse.urlencode(order_params)
#     signature = generate_signature(body, secret_access_key)
#
#     url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
#
#     res = requests.get(url)
#     ret_json = res.json()
#     # [0]['endpoints']
#     endpoints = ret_json['cluster_set'][0]['endpoints']
#     return endpoints


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


def setup_function(function):
    print("等待集群状态完全更新完毕")

    # 还原 time.sleep(60)


# def teardown_function():
#     print("测试rabbitMQ连通性")
#     # 还原 time.sleep(60)
#     clusters = cluster
#     for cluster_id in clusters:
#         status = describle_cluster(cluster_id)
#         if status == 'ceased' or status == 'stopped':
#             print("cluster_id:%s skip for cluster is stopped" % status)
#
#         else:
#             print("cluster_id:%s cluster is ok" % status)
#
#             node_ips = json.loads(describle_cluster_proxy_ip(cluster_id))
#             node_ip = node_ips["reserved_ips"]["vip"]["value"]
#             node_port = node_ips["status"]["port"]
#             is_rabbitMQ_ok = RabbitMQ_Con(node_ip, node_port)
#             assert is_rabbitMQ_ok == 0
#     time.sleep(20)


# def describle_cluster_nodes_config(cluster):
#     params = get_common_params()
#     params['action'] = "DescribeClusterNodes"
#     params['cluster'] = cluster
#
#     order_params = [(k, params[k]) for k in sorted(params.keys())]
#     body = urllib.parse.urlencode(order_params)
#     signature = generate_signature(body, secret_access_key)
#
#     url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
#     print(url)
#
#     res = requests.get(url)
#     ret_json = res.json()
#     # print ret_json
#     config_dict = {}
#     for node_set in ret_json['node_set']:
#         role = node_set['role']
#         cpu = node_set['cpu']
#         memory = node_set['memory']
#         storage_size = node_set['storage_size']
#         temp_dict = {}
#         temp_dict['cpu'] = cpu
#         temp_dict['memory'] = memory
#         temp_dict['storage_size'] = storage_size
#         config_dict[role] = temp_dict
#
#     return config_dict


# def describle_cluster_nodes_ip_port(cluster):
#     params = get_common_params()
#     params['action'] = "DescribeClusterNodes"
#     params['cluster'] = cluster
#
#     order_params = [(k, params[k]) for k in sorted(params.keys())]
#     body = urllib.parse.urlencode(order_params)
#     signature = generate_signature(body, secret_access_key)
#
#     url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
#     print(url)
#
#     res = requests.get(url)
#     ret_json = res.json()
#     # print ret_json
#     repica_rabbitMQ_pair = [node_set['private_ip'] for node_set in ret_json['node_set']]
#
#     return repica_rabbitMQ_pair


# def describle_cluster_vxnet(cluster):
#     params = get_common_params()
#     params['action'] = "DescribeClusters"
#     params['cluster.1'] = cluster
#
#     order_params = [(k, params[k]) for k in sorted(params.keys())]
#     body = urllib.parse.urlencode(order_params)
#     signature = generate_signature(body, secret_access_key)
#
#     url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
#     print(url)
#
#     res = requests.get(url)
#     ret_json = res.json()
#     repica_rabbitMQ_pair = ret_json['cluster_set'][0]['vxnet']
#     print(repica_rabbitMQ_pair)
#
#     return repica_rabbitMQ_pair


# def describle_cluster_proxy_nodes(cluster):
#     nodes = describle_cluster_nodes(cluster)
#     return [node_id for node_id in list(nodes.keys()) if nodes[node_id] == 'haproxy']


# def describle_cluster_client_nodes(cluster):
#     nodes = describle_cluster_nodes(cluster)
#     return [node_id for node_id in list(nodes.keys()) if nodes[node_id] == 'client']


# def describle_cluster_disk_nodes(cluster):
#     nodes = describle_cluster_nodes(cluster)
#     return [node_id for node_id in list(nodes.keys()) if nodes[node_id] == 'disc']


# def describle_cluster_nodes(cluster):
#     params = get_common_params()
#     params['action'] = "DescribeClusterNodes"
#     params['cluster'] = cluster
#     order_params = [(k, params[k]) for k in sorted(params.keys())]
#     body = urllib.parse.urlencode(order_params)
#     signature = generate_signature(body, secret_access_key)
#     url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
#     print(url)
#     res = requests.get(url)
#     ret_json = res.json()
#     print(ret_json)
#     repica_rabbitMQ_pair = {node_set['node_id']: node_set['role'] for node_set in ret_json['node_set']}
#     print(repica_rabbitMQ_pair)
#     return repica_rabbitMQ_pair


# def describle_cluster_nodes_env(cluster):
#     params = get_common_params()
#     params['action'] = "DescribeClusterNodes"
#     params['cluster'] = cluster
#     order_params = [(k, params[k]) for k in sorted(params.keys())]
#     body = urllib.parse.urlencode(order_params)
#     signature = generate_signature(body, secret_access_key)
#     url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
#     print(url)
#     res = requests.get(url)
#     ret_json = res.json()
#     # print(ret_json)
#     for i in ret_json['node_set']:
#         if (i['role'] == 'disc'):
#             envs = json.loads(i['env'])
#             break
#     return envs


# @pytest.mark.parametrize('cluster')
@allure.title('测试新增RabbitmqCluster集群')  # 设置用例标题
@allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
@pytest.mark.run(order=1)
@pytest.mark.rabbitMQ5
@pytest.mark.rabbitMQ4
def test_add_cluster():
    params = get_common_params()
    params['action'] = "DeployAppVersion"
    params['conf'] = "{\"cluster\":{\"name\":\"RabbitMQ集群\",\"description\":\"测试测试不要删\",\"disc\":{\"cpu\":1,\"memory\":1024,\"instance_class\":101,\"volume_size\":10,\"count\":3},\"client\":{\"cpu\":1,\"memory\":1024,\"instance_class\":101,\"count\":1},\"haproxy\":{\"cpu\":1,\"memory\":1024,\"instance_class\":101,\"volume_size\":10,\"count\":2},\"vxnet\":\"vxnet-71dxram\",\"etcd_service\":\"cl-k1my87gj\",\"global_uuid\":\"08632219872689231\"},\"version\":\"appv-spejlhjj\",\"resource_group\":\"Test\",\"vpc\":\"rtr-m7nomv0c\",\"env\":{\"rabbitmq_default_user\":\"guest\",\"rabbitmq_default_pass\":\"Wm881011\",\"haproxy_balance_policy\":\"roundrobin\",\"haproxy_web_port\":8100,\"haproxy_username\":\"haproxy\",\"haproxy_password\":\"haproxy\",\"num_tcp_acceptors\":10,\"handshake_timeout\":10000,\"vm_memory_high_watermark\":0.4,\"vm_memory_high_watermark_paging_ratio\":0.5,\"disk_free_limit\":524288000,\"frame_max\":131072,\"channel_max\":0,\"heartbeat\":60,\"collect_statistics\":\"none\",\"collect_statistics_interval\":5000,\"cluster_partition_handling\":\"pause_minority\",\"hipe_compile\":false,\"cluster_keepalive_interval\":10000,\"background_gc_target_interval\":60000,\"background_gc_enabled\":false,\"reverse_dns_lookups\":false,\"tracing_user\":\"guest\",\"proxy_protocol\":false,\"web_console_enabled\":true}}"
    params['app_type'] = "cluster"
    params['app_id'] = "app-n28v5lhg"
    params['version_id'] = "appv-spejlhjj"
    params['zone'] = "pek3a"
    params['debug'] = 1
    params['version'] = 1
    # print(urllib.parse.unquote(testConf))
    # print(json.loads(urllib.parse.unquote(ret)))
    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.parse.urlencode(order_params)
    # bodySplit = body.split("app_type=cluster")
    # body = bodySplit[0] + "app_type=cluster" + "&conf=" + paramsConf + bodySplit[1]
    # print(body)
    signature = generate_signature(body,secret_access_key)

    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
    print(url)
    res = requests.get(url)
    print(res.json())

    assert res.json()['ret_code'] == 0
    # job_id = res.json()['job_id'][cluster]
    # assert wait_job_done(job_id,cluster, timeout=600) == 0
    global cluster
    cluster=res.json()['cluster_id']
    print(cluster)

#
# @allure.title('测试停止RabbitmqCluster集群')  # 设置用例标题
# @allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
# @pytest.mark.run(order=2)
# @pytest.mark.rabbitMQ5
# @pytest.mark.rabbitMQ4
# def test_stop_cluster(cluster):
#     params = get_common_params()
#     params['action'] = "StopClusters"
#     params['clusters.1'] = cluster
#
#     order_params = [(k, params[k]) for k in sorted(params.keys())]
#     body = urllib.parse.urlencode(order_params)
#     signature = generate_signature(body, secret_access_key)
#
#     url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
#     print(url)
#     res = requests.get(url)
#     print(res.json())
#     assert res.json()['ret_code'] == 0
#     job_id = res.json()['job_ids'][cluster]
#     assert wait_job_done(job_id, cluster, timeout=600) == 0


# @pytest.mark.parametrize('cluster', get_rabbitMQ_cluster_ids())
# @allure.title('测试启动RabbitMQCluster集群')  # 设置用例标题
# @allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
# @pytest.mark.run(order=3)
# @pytest.mark.rabbitMQ5
# @pytest.mark.rabbitMQ4
# def test_start_cluster(cluster):
#     params = get_common_params()
#     params['action'] = "StartClusters"
#     params['clusters.1'] = cluster
#
#     order_params = [(k, params[k]) for k in sorted(params.keys())]
#     body = urllib.parse.urlencode(order_params)
#     signature = generate_signature(body, secret_access_key)
#
#     url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
#     res = requests.get(url)
#     print(res.json())
#
#     assert res.json()['ret_code'] == 0
#     job_id = res.json()['job_ids'][cluster]
#     assert wait_job_done(job_id, cluster, timeout=600) == 0


# @pytest.mark.parametrize('cluster', get_rabbitMQ_cluster_ids())
# @pytest.mark.run(order=4)
# @allure.title('测试增加rabbit Cluster集群磁盘节点')  # 设置用例标题
# @allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
# @pytest.mark.rabbitMQ5
# @pytest.mark.rabbitMQ4
# @pytest.mark.dependency(name='add_disk_nodes')
# def test_add_cluster_disk_nodes(context, cluster):
#     params = get_common_params()
#     params['action'] = "AddClusterNodes"
#     params['cluster'] = cluster
#     params['node_count'] = random.choice([1, 3, 5])
#     params['node_role'] = "disc"
#     params['double_check'] = 1
#     params['confirm'] = 0
#
#     order_params = [(k, params[k]) for k in sorted(params.keys())]
#     body = urllib.parse.urlencode(order_params)
#     signature = generate_signature(body, secret_access_key)
#
#     url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
#     print(url)
#
#     res = requests.get(url)
#     print(res.json())
#
#     assert res.json()['ret_code'] == 0
#     ret_json = res.json()
#     if 'job_ids' in ret_json:
#         job_id = ret_json['job_ids'][cluster]
#     elif 'job_id' in ret_json:
#         job_id = ret_json['job_id']
#     else:
#         assert False, ret_json
#
#     assert wait_job_done(job_id, cluster, timeout=600) == 0
#     # {u'action': u'AddClusterNodesResponse', u'cluster_id': u'cl-k8vqgxhq', u'job_id': u'j-biqcrpvchi0', u'new_node_ids': [u'cln-vgw7of69', u'cln-a8tmhpay', u'cln-9naqonor'], u'ret_code': 0}
#     context['new_node_ids'] = ret_json['new_node_ids']


# @pytest.mark.parametrize('cluster', get_rabbitMQ_cluster_ids())
# @pytest.mark.smoketest
# @allure.title('删除Rabbitmq CLuster的磁盘节点')  # 设置用例标题
# @allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
# @pytest.mark.rabbitMQ5
# @pytest.mark.rabbitMQ4
# @pytest.mark.run(order=5)
# @pytest.mark.dependency(depends=['add_disk_nodes'], scope="module")
# def test_delete_rabbit_cluster_disk_nodes(cluster):
#     nodes = describle_cluster_disk_nodes(cluster)
#     envs = describle_cluster_nodes_env(cluster)
#     params = get_common_params()
#     params['action'] = "DeleteClusterNodes"
#     params['cluster'] = cluster
#     nodes_num = len(nodes)
#     assertFlag = True
#     if nodes_num == 3:
#         assert True, "disc nodes number == 3,skip delete"
#         return
#     else:
#         if (envs['cluster_partition_handling'] == "pause_minority"):
#             if (random.random() < 0.5):
#                 for i in range(random.randint(1, int((nodes_num + 1) / 2 - 1))):
#                     params['nodes.' + str(i + 1)] = nodes[i]
#             else:
#                 for i in range(random.randint(int((nodes_num + 1) / 2 - 1), nodes_num)):
#                     params['nodes.' + str(i + 1)] = nodes[i]
#                 assertFlag = False
#         else:
#             for i in range(random.randint(1, nodes_num - 3)):
#                 params['nodes.' + str(i + 1)] = nodes[i]
#     order_params = [(k, params[k]) for k in sorted(params.keys())]
#     body = urllib.parse.urlencode(order_params)
#     signature = generate_signature(body, secret_access_key)
#     url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
#     print(url)
#     res = requests.get(url)
#
#     assert (res.json()['ret_code'] == 0) if assertFlag else (res.json()['ret_code'] != 0)
#     ret_json = res.json()
#     # print(ret_json,type(ret_json))
#     if 'job_ids' in ret_json:
#         job_id = ret_json['job_ids'][cluster]
#     elif 'job_id' in ret_json:
#         job_id = ret_json['job_id']
#     elif ret_json['ret_code'] == 8000:
#         print(ret_json['message'])
#         if assertFlag:
#             assert False
#         else:
#             return
#     else:
#         assert False, ret_json
#     assert (wait_job_done(job_id, cluster, timeout=600) == 0) if assertFlag else (
#                 wait_job_done(job_id, cluster, timeout=600) != 0)


# @pytest.mark.parametrize('cluster', get_rabbitMQ_cluster_ids())
# @pytest.mark.run(order=3)
# @allure.title('测试增加rabbit Cluster集群proxy节点')  # 设置用例标题
# @allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
# @pytest.mark.rabbitMQ5
# @pytest.mark.rabbitMQ4
# @pytest.mark.dependency(name='add_proxy_nodes')
# def test_add_cluster_proxy_nodes(context, cluster):
#     nodes = describle_cluster_proxy_nodes(cluster)
#     print(nodes)
#     params = get_common_params()
#     if len(nodes) == 100:
#         # 已经达到了proxy节点的上限
#         assert True, "proxy nodes number equals two"
#         return
#     params['node_count'] = random.choice(1, 2)
#     # elif len(nodes) == 1:
#     #     params['node_count'] = 1
#     # elif len(nodes) == 0:
#     #     params['node_count'] = 2
#     # else:
#     #     assert True, "proxy nodes number excetpion:" + str(len(nodes))
#     params['action'] = "AddClusterNodes"
#     params['cluster'] = cluster
#     params['node_role'] = "haproxy"
#     params['double_check'] = 1
#     params['confirm'] = 0
#     print(params)
#     order_params = [(k, params[k]) for k in sorted(params.keys())]
#     body = urllib.parse.urlencode(order_params)
#     signature = generate_signature(body, secret_access_key)
#     url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
#     print(url)
#     res = requests.get(url)
#     print(res.json())
#     assert res.json()['ret_code'] == 0
#     ret_json = res.json()
#     if 'job_ids' in ret_json:
#         job_id = ret_json['job_ids'][cluster]
#     elif 'job_id' in ret_json:
#         job_id = ret_json['job_id']
#     else:
#         assert False, ret_json
#     assert wait_job_done(job_id, cluster, timeout=600) == 0
#     # {u'action': u'AddClusterNodesResponse', u'cluster_id': u'cl-k8vqgxhq', u'job_id': u'j-biqcrpvchi0', u'new_node_ids': [u'cln-vgw7of69', u'cln-a8tmhpay', u'cln-9naqonor'], u'ret_code': 0}
#     context['new_node_ids'] = ret_json['new_node_ids']


# @pytest.mark.parametrize('cluster', get_rabbitMQ_cluster_ids())
# @pytest.mark.smoketest2
# @allure.title('resize RedisCLuster的haproxy节点')  # 设置用例标题
# @allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
# @pytest.mark.run(order=7)
# @pytest.mark.rabbitMQ5
# def test_resize_rabbitMQ_cluster_proxy_nodes(cluster):
#     nodes_config = describle_cluster_nodes_config(cluster)
#
#     params = get_common_params()
#     if 'haproxy' in nodes_config:
#         params['node_role'] = 'haproxy'
#     else:
#         assert True, "cluster %s 没有haproxy节点" % cluster
#         return
#     config = nodes_config['disc']
#     params['action'] = "ResizeCluster"
#     params['cluster'] = cluster
#     cpu = random.choice([1, 2])
#     while cpu == config['cpu']:
#         cpu = random.choice([1, 2, 4])
#
#     memory = random.choice([2048, 4096, 8192])
#     while memory == config['memory']:
#         memory = random.choice([2048, 4096, 8192])
#
#     storage_size = random.choice([10, 200, 500, 1000])
#     while storage_size == config['storage_size']:
#         storage_size = random.choice([10, 200, 500, 1000])
#     params['cpu'] = cpu
#     params['memory'] = memory
#     params['storage'] = storage_size
#
#     # params['node_role'] = "'[" + ','.join(params['node_role']) + "]'"
#     print("resized:", params)
#
#     order_params = [(k, params[k]) for k in sorted(params.keys())]
#     body = urllib.parse.urlencode(order_params)
#     # signature = generate_signature(body, secret_access_key)
#     signature = generate_signature(body, secret_access_key)
#
#     url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
#     print(url)
#
#     res = requests.get(url)
#     print(res.json())
#     assert res.json()['ret_code'] == 0
#     ret_json = res.json()
#     print(ret_json)
#     if 'job_ids' in ret_json:
#         job_id = ret_json['job_ids'][cluster]
#     elif 'job_id' in ret_json:
#         job_id = ret_json['job_id']
#     else:
#         assert False, ret_json
#
#     assert wait_job_done(job_id, cluster, timeout=600) == 0


# @pytest.mark.parametrize('cluster', get_rabbitMQ_cluster_ids())
# @pytest.mark.smoketest2
# @allure.title('resize RedisCLuster的disc节点')  # 设置用例标题
# @allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
# @pytest.mark.run(order=7)
# @pytest.mark.rabbitMQ5
# def test_resize_rabbitMQ_cluster_disc_nodes(cluster):
#     nodes_config = describle_cluster_nodes_config(cluster)
#
#     params = get_common_params()
#     if 'disc' in nodes_config:
#         params['node_role'] = 'disc'
#     else:
#         assert True, "cluster %s 没有disc节点" % cluster
#         return
#     config = nodes_config['disc']
#     params['action'] = "ResizeCluster"
#     params['cluster'] = cluster
#     cpu = random.choice([1, 2])
#     while cpu == config['cpu']:
#         cpu = random.choice([1, 2])
#
#     memory = random.choice([2048, 4096, 8192])
#     while memory == config['memory']:
#         memory = random.choice([2048, 4096, 8192])
#
#     storage_size = random.choice([10, 200, 500, 1000])
#     while storage_size == config['storage_size']:
#         storage_size = random.choice([10, 200, 500, 1000])
#     params['cpu'] = cpu
#     params['memory'] = memory
#     params['storage'] = storage_size
#     # params['node_role'] = "'[" + ','.join(params['node_role']) + "]'"
#     print("resized:", params)
#     order_params = [(k, params[k]) for k in sorted(params.keys())]
#     body = urllib.parse.urlencode(order_params)
#     # signature = generate_signature(body, secret_access_key)
#     signature = generate_signature(body, secret_access_key)
#     url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
#     print(url)
#     res = requests.get(url)
#     print(res.json())
#     assert res.json()['ret_code'] == 0
#     ret_json = res.json()
#     print(ret_json)
#     if 'job_ids' in ret_json:
#         job_id = ret_json['job_ids'][cluster]
#     elif 'job_id' in ret_json:
#         job_id = ret_json['job_id']
#     else:
#         assert False, ret_json
#
#     assert wait_job_done(job_id, cluster, timeout=600) == 0




@allure.title('测试删除RabbitmqCluster集群')  # 设置用例标题
@allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
@pytest.mark.run(order=10)
@pytest.mark.rabbitMQ5
@pytest.mark.rabbitMQ4
def test_delete_cluster(cluster):
    params = get_common_params()
    params['action'] = "DeleteClusters"
    params['clusters.1'] = cluster
    params['zone'] = "pek3a"
    params['debug'] = 1
    # paramsConf = "%7B%22cluster%22%3A%7B%22name%22%3A%22RabbitMQ%22%2C%22description%22%3A%22%22%2C%22disc%22%3A%7B%22cpu%22%3A2%2C%22memory%22%3A4096%2C%22instance_class%22%3A202%2C%22volume_size%22%3A10%2C%22count%22%3A3%7D%2C%22client%22%3A%7B%22cpu%22%3A1%2C%22memory%22%3A1024%2C%22instance_class%22%3A101%2C%22count%22%3A1%7D%2C%22haproxy%22%3A%7B%22cpu%22%3A2%2C%22memory%22%3A2048%2C%22instance_class%22%3A101%2C%22volume_size%22%3A10%2C%22count%22%3A2%7D%2C%22vxnet%22%3A%22vxnet-71dxram%22%2C%22etcd_service%22%3A%22cl-k1my87gjww%22%2C%22global_uuid%22%3A%2295682219872254169%22%2C%22add_port_to_sg%22%3A1%7D%2C%22version%22%3A%22appv-2uvgt1g3%22%2C%22resource_group%22%3A%22Prod%22%2C%22vpc%22%3A%22rtr-m7nomv0c%22%2C%22env%22%3A%7B%22rabbitmq_default_user%22%3A%22guest%22%2C%22rabbitmq_default_pass%22%3A%22guest%22%2C%22haproxy_balance_policy%22%3A%22roundrobin%22%2C%22haproxy_web_port%22%3A8100%2C%22haproxy_username%22%3A%22haproxy%22%2C%22haproxy_password%22%3A%22haproxy%22%2C%22num_tcp_acceptors%22%3A10%2C%22handshake_timeout%22%3A10000%2C%22vm_memory_high_watermark%22%3A0.4%2C%22vm_memory_high_watermark_paging_ratio%22%3A0.5%2C%22disk_free_limit%22%3A524288000%2C%22frame_max%22%3A131072%2C%22channel_max%22%3A0%2C%22heartbeat%22%3A60%2C%22collect_statistics%22%3A%22none%22%2C%22collect_statistics_interval%22%3A5000%2C%22cluster_partition_handling%22%3A%22pause_minority%22%2C%22hipe_compile%22%3Afalse%2C%22cluster_keepalive_interval%22%3A10000%2C%22background_gc_target_interval%22%3A60000%2C%22background_gc_enabled%22%3Afalse%2C%22reverse_dns_lookups%22%3Afalse%2C%22tracing_user%22%3A%22guest%22%2C%22proxy_protocol%22%3Afalse%2C%22web_console_enabled%22%3Atrue%7D%7D"
    # paramsConf = "%7B%22cluster%22%3A%7B%22name%22%3A%22RabbitMQ%22%2C%22description%22%3A%22%22%2C%22disc%22%3A%7B%22cpu%22%3A2%2C%22memory%22%3A4096%2C%22instance_class%22%3A202%2C%22volume_size%22%3A10%2C%22count%22%3A3%7D%2C%22client%22%3A%7B%22cpu%22%3A1%2C%22memory%22%3A1024%2C%22instance_class%22%3A101%2C%22count%22%3A1%7D%2C%22haproxy%22%3A%7B%22cpu%22%3A2%2C%22memory%22%3A2048%2C%22instance_class%22%3A101%2C%22volume_size%22%3A10%2C%22count%22%3A2%7D%2C%22vxnet%22%3A%22vxnet-71dxram%22%2C%22etcd_service%22%3A%22cl-p3j690ww%22%2C%22global_uuid%22%3A%2295682219872254169%22%2C%22add_port_to_sg%22%3A1%7D%2C%22version%22%3A%22appv-2uvgt1g3%22%2C%22resource_group%22%3A%22Prod%22%2C%22vpc%22%3A%22rtr-m7nomv0c%22%2C%22env%22%3A%7B%22rabbitmq_default_user%22%3A%22guest%22%2C%22rabbitmq_default_pass%22%3A%22guest%22%2C%22haproxy_balance_policy%22%3A%22roundrobin%22%2C%22haproxy_web_port%22%3A8100%2C%22haproxy_username%22%3A%22haproxy%22%2C%22haproxy_password%22%3A%22haproxy%22%2C%22num_tcp_acceptors%22%3A10%2C%22handshake_timeout%22%3A10000%2C%22vm_memory_high_watermark%22%3A0.4%2C%22vm_memory_high_watermark_paging_ratio%22%3A0.5%2C%22disk_free_limit%22%3A524288000%2C%22frame_max%22%3A131072%2C%22channel_max%22%3A0%2C%22heartbeat%22%3A60%2C%22collect_statistics%22%3A%22none%22%2C%22collect_statistics_interval%22%3A5000%2C%22cluster_partition_handling%22%3A%22pause_minority%22%2C%22hipe_compile%22%3Afalse%2C%22cluster_keepalive_interval%22%3A10000%2C%22background_gc_target_interval%22%3A60000%2C%22background_gc_enabled%22%3Afalse%2C%22reverse_dns_lookups%22%3Afalse%2C%22tracing_user%22%3A%22guest%22%2C%22proxy_protocol%22%3Afalse%2C%22web_console_enabled%22%3Atrue%7D%7D"
    #
    # params['version_id'] = "appv-2uvgt1g3"
    # params['app_id'] = "app-n28v5lhg"
    # params['app_type'] = "cluster"
    # params['debug'] = 1
    # testConf = "%7B%22cluster%22%3A%7B%22name%22%3A%22Tomcat_Cluster%22%2C%22description%22%3A%22%22%2C%22tomcat_nodes%22%3A%7B%22loadbalancer%22%3A%5B%7B%22listener%22%3A%22lbl-wdplf9gh%22%2C%22port%22%3A8080%2C%22policy%22%3A%22%22%7D%5D%2C%22cpu%22%3A1%2C%22memory%22%3A2048%2C%22instance_class%22%3A0%2C%22count%22%3A2%2C%22volume_size%22%3A10%7D%2C%22log_node%22%3A%7B%22cpu%22%3A1%2C%22memory%22%3A2048%2C%22instance_class%22%3A0%2C%22volume_size%22%3A10%7D%2C%22vxnet%22%3A%22vxnet-iuy3lnd%22%2C%22global_uuid%22%3A%2293242219542648944%22%7D%2C%22version%22%3A%22appv-gva21mw0%22%2C%22env%22%3A%7B%22tomcat_user%22%3A%22qingAdmin%22%2C%22tomcat_pwd%22%3A%22qing0pwd%22%2C%22tomcat_encoding%22%3A%22UTF-8%22%2C%22tomcat_log_level%22%3A%22INFO%22%2C%22threadpool_maxThreads%22%3A%22200%22%2C%22threadpool_minSpareThreads%22%3A%2225%22%2C%22threadpool_maxIdleTime%22%3A%2260000%22%2C%22war_source%22%3A%22tomcat_manager%22%2C%22tomcat_log_packages%22%3A%22%22%2C%22java_opts%22%3A%22%22%2C%22redis_db_num%22%3A%220%22%2C%22access_key_id%22%3A%22%22%2C%22zone%22%3A%22pek3a%22%2C%22bucket%22%3A%22%22%2C%22war_name%22%3A%22%22%2C%22mysql_db_name%22%3A%22mysql%22%2C%22jdbc_dsname%22%3A%22TestDB%22%2C%22jdbc_maxActive%22%3A%22100%22%2C%22jdbc_maxIdle%22%3A%2230%22%2C%22jdbc_maxWait%22%3A%2230000%22%7D%7D"
    # ret = urllib.parse.unquote(paramsConf)
    # print(ret)
    # print(urllib.parse.unquote(testConf))
    # print(json.loads(urllib.parse.unquote(ret)))
    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.parse.urlencode(order_params)
    # bodySplit = body.split("app_type=cluster")
    # body = bodySplit[0] + "app_type=cluster" + "&conf=" + paramsConf + bodySplit[1]
    # print(body)
    signature = generate_signature(body,secret_access_key)

    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature


    print(url)
    res = requests.get(url)
    print(res.json())
    assert res.json()['ret_code'] == 0


# @pytest.mark.skip(reason='跳过Test类，会跳过类中所有方法')
# @pytest.mark.smoketest2
# @allure.title('发送消息')  # 设置用例标题
# @allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
# @pytest.mark.run(order=8)
# @pytest.mark.rabbitMQ5
# def test_send():
#     cluster_id = get_rabbitMQ_cluster_ids()[0]
#     node_ips = json.loads(describle_cluster_proxy_ip(cluster_id))
#     vip = node_ips["reserved_ips"]["vip"]["value"]
#     port = node_ips["client"]["port"]
#     host = str(vip) + ":" + str(port)
#     print("host = " + host)
#     connection = pika.BlockingConnection(pika.ConnectionParameters(host=vip, port=port))
#     channel = connection.channel()
#     channel.queue_declare(queue='hello')
#     for i in (0, 10000):
#         channel.basic_publish(exchange='',
#                               routing_key='hello',
#                               body=str(i))
#     connection.close()

    # @pytest.mark.skip(reason='跳过Test类，会跳过类中所有方法')


# @pytest.mark.skip(reason='跳过Test类，会跳过类中所有方法')
@pytest.mark.smoketest2
@allure.title('接受消息')  # 设置用例标题
@allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
@pytest.mark.run(order=9)
@pytest.mark.rabbitMQ5
def test_receive():
    pass
    # cluster_id = get_rabbitMQ_cluster_ids()[0]
    # node_ips = json.loads(describle_cluster_proxy_ip(cluster_id))
    # vip = node_ips["reserved_ips"]["vip"]["value"]
    # port = node_ips["client"]["port"]
    # host = str(vip) + ":" + str(port)
    # print("host = " + host)
    # connection = pika.BlockingConnection(pika.ConnectionParameters(host=vip, port=port))
    # channel = connection.channel()
    #
    # # channel.queue_declare(queue='hello')
    #
    # def callback(ch, method, properties, body):
    #     print(" [x] Received %r" % body)
    #
    # channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)
    #
    # print(' [*] s.Waiting for message To exit press CTRL+C')
    # channel.start_consuming()
    # time.sleep(5)
    # connection.close()
if __name__ == "__main__":
   test_add_cluster()
   test_delete_cluster(cluster)
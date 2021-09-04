#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import hmac
import urllib
import time
import random
from hashlib import sha256
import os,sys
import json
import pytest
import allure
import requests
import copy
from yaml_util import yamlUtil
from redis_connect import Redis_Con
import inspect 

test_conf = {}
try:
    conf_path = "config.json"
    with open(conf_path, "r") as f:
        test_conf = json.load(f)
except Exception, e:
    print e
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

common_params = {
    "zone": zone,
    "access_key_id": access_key_id,
    "limit": '20',
    "signature_method": 'HmacSHA256',
    "signature_version": '1',
    #"status.1": "working",
    "version": "1"
}

ri_node_ids = ['cln-3ojmilbm']
mi_node_ids = []
proxy_node_ids = []


def get_redis_cluster_ids():
    yml_info = yamlUtil("./cluster.yaml").read_yaml()
    print yml_info
    return yml_info['redis_cluster']['id']

def get_common_params():
    params = {}
    params.update(common_params)
    params['expires'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() + 30))  # UTC
    params['time_stamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time()))  # UTC
    #params['cluster'] = 'cl-v1dbfgum'
    return params

def generate_signature(body, secret_access_key):
    string_to_sign = 'GET\n/iaas/\n' + body
    h = hmac.new(secret_access_key, digestmod=sha256)
    h.update(string_to_sign)
    sign = base64.b64encode(h.digest()).strip()
    signature = urllib.quote_plus(sign)
    return signature

def describle_cluster(cluster):
    params = get_common_params()
    params['action'] = "DescribeClusters"
    params['cluster.1'] = cluster

    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)

    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
    res = requests.get(url)
    ret_json = res.json()
    status = ret_json['cluster_set'][0]['status']
    return status



def wait_job_done(jod_id, cluster, timeout=600):
    params = get_common_params()
    params['action'] = "DescribeJobs"
    params['jobs.1'] = jod_id
    params['resource_ids'] = cluster
    print jod_id,cluster
    while timeout > 0:
        timeout -= 2

        params['expires'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() + 30))  # UTC
        params['time_stamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time()))  # UTC
        order_params = [(k, params[k]) for k in sorted(params.keys())]
        body = urllib.urlencode(order_params)
        signature = generate_signature(body, secret_access_key)

        url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
        #print url
        res = requests.get(url)
        #print res.json()
        if res.json()['job_set'][0]['status'] == "failed":
            return -1
        if res.json()['job_set'][0]['status'] == "successful":
            return 0
        time.sleep(2)
    print "wait_job_done timeout"
    return -1

def setup_function(function):
    print "等待集群状态完全更新完毕"
    time.sleep(20)

def teardown_function():
    print "测试redis连通性"
    time.sleep(30)
    clusters = get_redis_cluster_ids()
    for cluster_id in clusters:
        status = describle_cluster(cluster_id)
        if status == 'ceased' or status == 'stopped':
            print "cluster_id:%s skip for cluster is stopped" % status
        else:
            print "cluster_id:%s cluster is ok" % status
            node_ips= describle_cluster_nodes_ip(cluster_id)
            for node_ip in node_ips:
                is_redis_ok = Redis_Con(node_ip)
                assert is_redis_ok == 0
    time.sleep(20)


@pytest.mark.parametrize('cluster',get_redis_cluster_ids())
@allure.title('测试停止RedisCluster集群')  # 设置用例标题
@allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
@pytest.mark.run(order=1)
def test_stop_cluster(cluster):
    params = get_common_params()
    params['action'] = "StopClusters"
    params['clusters.1'] = cluster

    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)

    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
    print url
    res = requests.get(url)
    print res.json()
    assert res.json()['ret_code'] == 0
    job_id = res.json()['job_ids'][cluster]
    assert wait_job_done(job_id, cluster, timeout=600) == 0
    
@pytest.mark.parametrize('cluster',get_redis_cluster_ids())
@allure.title('测试启动RedisCluster集群')  # 设置用例标题
@allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
@pytest.mark.run(order=2)
def test_start_cluster(cluster):
    params = get_common_params()
    params['action'] = "StartClusters"
    params['clusters.1'] = cluster

    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)

    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
    res = requests.get(url)
    print res.json()
    assert res.json()['ret_code'] == 0
    job_id = res.json()['job_ids'][cluster]
    assert wait_job_done(job_id, cluster, timeout=600) == 0

@pytest.mark.parametrize('cluster',get_redis_cluster_ids())
@pytest.mark.run(order=3)
@allure.title('测试增加RedisCluster集群主节点')  # 设置用例标题
@allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
#@pytest.mark.smoketest
def test_add_cluster_master_nodes(cluster):
    params = get_common_params()
    params['action'] = "AddClusterNodes"
    params['cluster'] = cluster
    params['node_count'] = 1
    params['node_role'] = "master"
    params['double_check'] = 1
    params['confirm'] = 0

    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)

    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
    print url
    res = requests.get(url)
    print res.json()
    assert res.json()['ret_code'] == 0
    ret_json = res.json()
    if ret_json.has_key('job_ids'):
        job_id = ret_json['job_ids'][cluster]
    elif ret_json.has_key('job_id'):
        job_id = ret_json['job_id']
    else:
        assert False,ret_json

    assert wait_job_done(job_id, cluster, timeout=600) == 0

@pytest.mark.parametrize('cluster',get_redis_cluster_ids())
@pytest.mark.run(order=4)
@allure.title('测试增加RedisCluster集群副本节点')  # 设置用例标题
@allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
@pytest.mark.smoketest
def test_add_cluster_master_replica_nodes(cluster):
    params = get_common_params()
    params['action'] = "AddClusterNodes"
    params['cluster'] = cluster
    params['node_count'] = 1
    params['node_role'] = "master-replica"
    params['double_check'] = 1
    params['confirm'] = 0

    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)

    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
    print url
    res = requests.get(url)
    print res.json()
    assert res.json()['ret_code'] == 0
    ret_json = res.json()
    if ret_json.has_key('job_ids'):
        job_id = ret_json['job_ids'][cluster]
    elif ret_json.has_key('job_id'):
        job_id = ret_json['job_id']
    else:
        assert False,ret_json

    assert wait_job_done(job_id, cluster, timeout=600) == 0

def describle_cluster_nodes_config(cluster):
    params = get_common_params()
    params['action'] = "DescribeClusterNodes"
    params['cluster'] = cluster

    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)
    
    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
    print url
    res = requests.get(url)
    ret_json = res.json()
    #print ret_json
    config_dict = {}
    for node_set in ret_json['node_set']:
        cpu = node_set['cpu']
        memory = node_set['memory']
        storage_size = node_set['storage_size']
        config_dict['cpu'] = cpu
        config_dict['memory'] = memory
        config_dict['storage_size'] = storage_size

    return config_dict


def describle_cluster_nodes_ip(cluster):
    params = get_common_params()
    params['action'] = "DescribeClusterNodes"
    params['cluster'] = cluster

    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)
    
    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
    print url
    res = requests.get(url)
    ret_json = res.json()
    #print ret_json
    repica_redis_pair =[node_set['private_ip'] for node_set in ret_json['node_set']]

    return repica_redis_pair


def describle_cluster_vxnet(cluster):
    params = get_common_params()
    params['action'] = "DescribeClusters"
    params['cluster.1'] = cluster

    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)

    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
    print url
    res = requests.get(url)
    ret_json = res.json()
    repica_redis_pair = ret_json['cluster_set'][0]['vxnet']
    print(repica_redis_pair)

    return repica_redis_pair


def describle_cluster_nodes(cluster):
    params = get_common_params()
    params['action'] = "DescribeClusterNodes"
    params['cluster'] = cluster

    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)
    
    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
    print url
    res = requests.get(url)
    ret_json = res.json()
    print ret_json
    repica_redis_pair ={node_set['node_id']:node_set['replica_master'] for node_set in ret_json['node_set'] if node_set.has_key('replica_master')}
    print repica_redis_pair
    if not repica_redis_pair:
        repica_redis_pair ={node_set['node_id']:node_set['node_id'] for node_set in ret_json['node_set'] }
    print repica_redis_pair

    return repica_redis_pair


@pytest.mark.parametrize('cluster',get_redis_cluster_ids())
@pytest.mark.smoketest
@allure.title('删除RedisCLuster的所有副本节点')  # 设置用例标题
@allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
@pytest.mark.run(order=5)
def test_delete_cluster_replica_nodes(cluster):
    nodes = describle_cluster_nodes(cluster)
    params = get_common_params()
    params['action'] = "DeleteClusterNodes"
    params['cluster'] = cluster
    replica_node_ids = nodes.keys()
    for i in range(len(replica_node_ids)):
        params['nodes.'+str(i+1)] = replica_node_ids[i]

    #node1,node2 = random.choice(nodes.items())
    #params['nodes.1'] = node1
    #params['nodes.2'] = node2

    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)
    
    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
    print url
    res = requests.get(url)
    #print res.json()
    assert res.json()['ret_code'] == 0
    ret_json = res.json()
    print ret_json
    if ret_json.has_key('job_ids'):
        job_id = ret_json['job_ids'][cluster]
    elif ret_json.has_key('job_id'):
        job_id = ret_json['job_id']
    else:
        assert False,ret_json

    assert wait_job_done(job_id, cluster, timeout=600) == 0


@pytest.mark.parametrize('cluster',get_redis_cluster_ids())
@pytest.mark.smoketest2
@allure.title('删除RedisCLuster的一个主节点')  # 设置用例标题
@allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
@pytest.mark.run(order=6)
def test_delete_cluster_master_nodes(cluster):
    nodes = describle_cluster_nodes(cluster)
    print nodes
    params = get_common_params()
    params['action'] = "DeleteClusterNodes"
    params['cluster'] = cluster
    node1,node2 = random.choice(nodes.items())
    params['nodes.1'] = node2

    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)
    
    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
    print url
    res = requests.get(url)
    #print res.json()
    assert res.json()['ret_code'] == 0
    ret_json = res.json()
    print ret_json
    if ret_json.has_key('job_ids'):
        job_id = ret_json['job_ids'][cluster]
    elif ret_json.has_key('job_id'):
        job_id = ret_json['job_id']
    else:
        assert False,ret_json

    assert wait_job_done(job_id, cluster, timeout=600) == 0

@pytest.mark.parametrize('cluster',get_redis_cluster_ids())
@pytest.mark.smoketest2
@allure.title('resize RedisCLuster的一个主节点')  # 设置用例标题
@allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
@pytest.mark.run(order=7)
def test_resize_redis_cluster_master_nodes(cluster):
    config = describle_cluster_nodes_config(cluster)

    print "origin:",config

    params = get_common_params()
    params['action'] = "ResizeCluster"
    params['cluster'] = cluster
 
    cpu = random.choice([1,2])
    while cpu == config['cpu']:
        cpu = random.choice([1,2])

    memory = random.choice([2048,4096,8192])
    while memory == config['memory']:
        memory = random.choice([2048,4096,8192])

    storage_size = random.choice([10,200,500,1000])
    while storage_size == config['storage_size']:
        storage_size = random.choice([10,200,500,1000])


    params['cpu'] = cpu
    params['memory'] = memory
    params['storage'] = storage_size
    params["node_role"] = "master"

    print "resized:",params

    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)
    
    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
    print url
    res = requests.get(url)
    print res.json()
    assert res.json()['ret_code'] == 0
    ret_json = res.json()
    print ret_json
    if ret_json.has_key('job_ids'):
        job_id = ret_json['job_ids'][cluster]
    elif ret_json.has_key('job_id'):
        job_id = ret_json['job_id']
    else:
        assert False,ret_json

    assert wait_job_done(job_id, cluster, timeout=600) == 0

@pytest.mark.parametrize('cluster',get_redis_cluster_ids())
@pytest.mark.smoketest2
@allure.title('切换 RedisCLuster的vxnet')  # 设置用例标题
@allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
@pytest.mark.run(order=8)
@pytest.mark.repeat(3)
def test_change_vxnet_redis_cluster(cluster):
    vxnet = describle_cluster_vxnet(cluster)
    # s.encode('utf8').decode('unicode_escape').encode('utf8') 
    vxnet_id = vxnet['vxnet_id'].encode('utf8').decode('unicode_escape').encode('utf8')
    print(vxnet_id,vxnet_a,vxnet_b)

    params = get_common_params()
    params['action'] = "ChangeClusterVxnet"
    params['cluster'] = cluster
    params['vxnet'] = vxnet_a if vxnet_id == vxnet_b else vxnet_b
    print(params)
    #params['roles'] = ['master']
    #{"action":"ChangeClusterVxnet","cluster":"cl-qwatamn7","roles":["master"],"vxnet":"vxnet-6350yyd","owner":"usr-GuK21Csb","zone":"pek3a"}

    order_params = [(k, params[k]) for k in sorted(params.keys())]
    body = urllib.urlencode(order_params)
    signature = generate_signature(body, secret_access_key)
    
    url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
    print url
    res = requests.get(url)
    print res.json()
    assert res.json()['ret_code'] == 0
    ret_json = res.json()
    print ret_json
    if ret_json.has_key('job_ids'):
        job_id = ret_json['job_ids'][cluster]
    elif ret_json.has_key('job_id'):
        job_id = ret_json['job_id']
    else:
        assert False,ret_json

    assert wait_job_done(job_id, cluster, timeout=600) == 0



#describle_cluster('cl-v1dbfgum')
print describle_cluster_nodes_config('cl-qwatamn7')


#describle_cluster_vxnet('cl-qwatamn7')

#wait_job_done('j-h3lkhb6xw6z', 'cl-a8op3s8k',  timeout=600)


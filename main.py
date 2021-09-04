# import requests
# import json
# import time
# import urllib.request, urllib.parse, urllib.error
# import urllib.parse
# import hmac
# import base64
# from hashlib import sha256

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
from yaml_util import yamlUtil
from rabbitmq_connect import RabbitMQ_Con
import re


# test_conf = {}
# try:
#     conf_path = "config.json"
#     with open(conf_path, "r") as f:
#         test_conf = json.load(f)
# except Exception() as e:
#     print(e)
#     sys.exit(1)

# access_key_id = str(test_conf['access_key_id'])
# secret_access_key = str(test_conf['secret_access_key'])
# zone = str(test_conf['zone'])
# cluster_id = str(test_conf['cluster']['cluster-a'])
# cluster_b_id = str(test_conf['cluster']['cluster-b'])
# cluster_a_wvip = str(test_conf['cluster']['cluster-a-wvip'])
# cluster_b_wvip = str(test_conf['cluster']['cluster-b-wvip'])
# cluster_user = str(test_conf['cluster']['cluster_user'])
# cluster_paawd = str(test_conf['cluster']['cluster_passwd'])
# vxnet_a = str(test_conf['vpc']['vxnet']['vxnet-a'])
# vxnet_b = str(test_conf['vpc']['vxnet']['vxnet-b'])


# with open('createcluster.json','r',encoding='utf8')as fp:
#     json_data = json.load(fp)
#
#     print(type(json_data))
#     json_data=json.dumps(json_data,ensure_ascii=False)
#     print(type(json_data))
#     json_data=json_data.replace("\n","")
#     res = re.sub("\n", "", json_data)
#     print(json_data)
#     json_data = json.load(fp)
# json_data=urllib.parse.urlencode(json_data)
# print(json_data)





# create_path = "createcluster.json"
# with open(create_path, "r") as f1:
#     f1.read()
    # create_conf = json.load(f)
    # print(create_conf)

access_key_id = "HEHYLNIKVMQLUQMBBZYD"
secret_access_key ="AFt3dkVdmjpnb73VHA1erhF8hPjhAWagtqQ0qdFa"




# common_params = {
#     "zone": "pek3a",
#     "access_key_id": access_key_id,
#     "limit": '200',
#     "signature_method": 'HmacSHA256',
#     "signature_version": '1',
#     "version": "1"
# }

cluster=""

# def get_common_params():
#     params = {}
#     params.update(common_params)
#     params['expires'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() + 30))  # UTC
#     params['time_stamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time()))  # UTC
#     # params['cluster'] = 'cl-v1dbfgum'
#     return params

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

# ="iMnibAmXEoaz8xk8yH6A5PG6WmccPxJQG7YXN01U"
def generate_signature(body, secret_access_key):
    string_to_sign = 'GET\n/iaas/\n' + body
    secret_access_key = bytes(secret_access_key, encoding='utf-8')
    h = hmac.new(secret_access_key, digestmod=sha256)
    h.update(string_to_sign.encode("utf-8"))
    sign = base64.b64encode(h.digest()).strip()
    signature = urllib.parse.quote_plus(sign)
    return signature

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





# if __name__ == "__main__":
#     otherParam = json.dumps({"action": "DeployAppVersion", "app_type": "cluster", "app_id": "app-n28v5lhg", "version_id": "appv-2uvgt1g3",
#                             "charge_mode": "elastic", "debug": 1, "zone": "pek3a", "owner": "usr-hRAmdSn6"})
#
#     params = get_common_params()
#     params['action'] = "DeployAppVersion"
#     paramsConf = "%7B%22cluster%22%3A%7B%22name%22%3A%22RabbitMQ%22%2C%22description%22%3A%22%22%2C%22disc%22%3A%7B%22cpu%22%3A2%2C%22memory%22%3A4096%2C%22instance_class%22%3A202%2C%22volume_size%22%3A10%2C%22count%22%3A3%7D%2C%22client%22%3A%7B%22cpu%22%3A1%2C%22memory%22%3A1024%2C%22instance_class%22%3A101%2C%22count%22%3A1%7D%2C%22haproxy%22%3A%7B%22cpu%22%3A2%2C%22memory%22%3A2048%2C%22instance_class%22%3A101%2C%22volume_size%22%3A10%2C%22count%22%3A2%7D%2C%22vxnet%22%3A%22vxnet-71dxram%22%2C%22etcd_service%22%3A%22cl-p3j690ww%22%2C%22global_uuid%22%3A%2295682219872254169%22%2C%22add_port_to_sg%22%3A1%7D%2C%22version%22%3A%22appv-2uvgt1g3%22%2C%22resource_group%22%3A%22Prod%22%2C%22vpc%22%3A%22rtr-m7nomv0c%22%2C%22env%22%3A%7B%22rabbitmq_default_user%22%3A%22guest%22%2C%22rabbitmq_default_pass%22%3A%22guest%22%2C%22haproxy_balance_policy%22%3A%22roundrobin%22%2C%22haproxy_web_port%22%3A8100%2C%22haproxy_username%22%3A%22haproxy%22%2C%22haproxy_password%22%3A%22haproxy%22%2C%22num_tcp_acceptors%22%3A10%2C%22handshake_timeout%22%3A10000%2C%22vm_memory_high_watermark%22%3A0.4%2C%22vm_memory_high_watermark_paging_ratio%22%3A0.5%2C%22disk_free_limit%22%3A524288000%2C%22frame_max%22%3A131072%2C%22channel_max%22%3A0%2C%22heartbeat%22%3A60%2C%22collect_statistics%22%3A%22none%22%2C%22collect_statistics_interval%22%3A5000%2C%22cluster_partition_handling%22%3A%22pause_minority%22%2C%22hipe_compile%22%3Afalse%2C%22cluster_keepalive_interval%22%3A10000%2C%22background_gc_target_interval%22%3A60000%2C%22background_gc_enabled%22%3Afalse%2C%22reverse_dns_lookups%22%3Afalse%2C%22tracing_user%22%3A%22guest%22%2C%22proxy_protocol%22%3Afalse%2C%22web_console_enabled%22%3Atrue%7D%7D"
#
#     params['version_id'] = "appv-2uvgt1g3"
#     params['app_id'] = "app-n28v5lhg"
#     params['app_type'] = "cluster"
#     params['debug'] = 1
#     # testConf = "%7B%22cluster%22%3A%7B%22name%22%3A%22Tomcat_Cluster%22%2C%22description%22%3A%22%22%2C%22tomcat_nodes%22%3A%7B%22loadbalancer%22%3A%5B%7B%22listener%22%3A%22lbl-wdplf9gh%22%2C%22port%22%3A8080%2C%22policy%22%3A%22%22%7D%5D%2C%22cpu%22%3A1%2C%22memory%22%3A2048%2C%22instance_class%22%3A0%2C%22count%22%3A2%2C%22volume_size%22%3A10%7D%2C%22log_node%22%3A%7B%22cpu%22%3A1%2C%22memory%22%3A2048%2C%22instance_class%22%3A0%2C%22volume_size%22%3A10%7D%2C%22vxnet%22%3A%22vxnet-iuy3lnd%22%2C%22global_uuid%22%3A%2293242219542648944%22%7D%2C%22version%22%3A%22appv-gva21mw0%22%2C%22env%22%3A%7B%22tomcat_user%22%3A%22qingAdmin%22%2C%22tomcat_pwd%22%3A%22qing0pwd%22%2C%22tomcat_encoding%22%3A%22UTF-8%22%2C%22tomcat_log_level%22%3A%22INFO%22%2C%22threadpool_maxThreads%22%3A%22200%22%2C%22threadpool_minSpareThreads%22%3A%2225%22%2C%22threadpool_maxIdleTime%22%3A%2260000%22%2C%22war_source%22%3A%22tomcat_manager%22%2C%22tomcat_log_packages%22%3A%22%22%2C%22java_opts%22%3A%22%22%2C%22redis_db_num%22%3A%220%22%2C%22access_key_id%22%3A%22%22%2C%22zone%22%3A%22pek3a%22%2C%22bucket%22%3A%22%22%2C%22war_name%22%3A%22%22%2C%22mysql_db_name%22%3A%22mysql%22%2C%22jdbc_dsname%22%3A%22TestDB%22%2C%22jdbc_maxActive%22%3A%22100%22%2C%22jdbc_maxIdle%22%3A%2230%22%2C%22jdbc_maxWait%22%3A%2230000%22%7D%7D"
#     ret = urllib.parse.unquote(paramsConf)
#     print(ret)
#     # print(urllib.parse.unquote(testConf))
#     # print(json.loads(urllib.parse.unquote(ret)))
#     order_params = [(k, params[k]) for k in sorted(params.keys())]
#     body = urllib.parse.urlencode(order_params)
#     bodySplit = body.split("app_type=cluster")
#     body = bodySplit[0] + "app_type=cluster" + "&conf=" + paramsConf + bodySplit[1]
#     print(body)
#     signature = generate_signature(body)
#
#     url = 'https://api.qingcloud.com/iaas/?' + body + '&signature=' + signature
#
#     res = requests.get(url)
#     ret_json = res.json()
#     print(ret_json)

def get_rabbitMQ_cluster_ids():
    # yml_info = yamlUtil("./cluster.yaml").read_yaml()
    # print(yml_info)
    # return yml_info['rabbimq_cluster']['id']
    global cluster
    print(cluster)
    return cluster

@pytest.mark.parametrize('cluster')
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




# @pytest.mark.parametrize('cluster', get_rabbitMQ_cluster_ids())
# @pytest.mark.smoketest2
# @allure.title('resize RrabbitMQCLuster的haproxy节点')  # 设置用例标题
# @allure.severity(allure.severity_level.CRITICAL)  # 设置用例优先级
# @pytest.mark.run(order=8)
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



@pytest.mark.parametrize('cluster', get_rabbitMQ_cluster_ids())
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
    # job_id = res.json()['job_ids'][cluster]
    # assert wait_job_done(job_id, cluster, timeout=600) == 0

if __name__ == "__main__":
    test_add_cluster()
    test_delete_cluster(cluster)



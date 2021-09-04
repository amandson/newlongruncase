## 说明
1. 本代码实例用跑redis_cluster(5.0.8和4.0.6)以及Rabbitmq(RabbitMQ 3.7.27)的longrun
2. 目录结果  


```
.
├── cluster.yaml                 #定义了要测试的集群id
├── config.json                  #定义了"access_key_id" "secret_access_key" "vpc" 相关的资源信息
├── rabbit_cluster_test.py       #rabbitmq的case
├── rabbitmq_connect.py          
├── README.md
├── redis_cluster_test.py        #redis的case
├── redis_connect.py
├── requirements.txt
└── yaml_util.py

```  


  
## 安装&运行

### 前置
1. AppCenter API 参考
	- https://docs.qingcloud.com/product/api/action/appcenter2/

2. 测试前置环境
	- 创建好一个vpc
	- 在vpc中创建好两个vxnet，在vxnet中创建对应的cluster集群
    - 在vpc中创建某虚机	

### 安装
在vpc上的某台主机上安装python以及相关的包
1. 安装pip包 （注意pip版本，测试代码基于 Python2.7 ）  
```
	pip install -r requirements.txt
```

### 运行
1. 在vpc的某台主机上运行测试
	- 测试case
        pytest rabbit_cluster_test.py -xvs   --alluredir Outputs/allure_report
	- 生成报告
        allure generate report/ -o report/html

2. 在jenkins上配置allrure
   参考对应对应文档# rabbitmqlongruncase-

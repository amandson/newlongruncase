#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import socket,sys
 
def RabbitMQ_Con(RabbitMQ_ip, RabbitMQ_port):
    RabbitMQ_sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    RabbitMQ_Result=RabbitMQ_sk.connect_ex((RabbitMQ_ip,RabbitMQ_port))
    if RabbitMQ_Result == 0:
        print('RabbitMQ Port is Open')
        return 0
    else:
        print('RabbitMQ Port is Not Open')
        return 1
 
if __name__ == '__main__':
    RabbitMQ_Con('192.168.0.253',8100)

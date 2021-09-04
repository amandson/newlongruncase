#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import socket,sys
 
def Redis_Con(Redis_ip):
    Redis_sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    Redis_Result=Redis_sk.connect_ex((Redis_ip,6379))
    if Redis_Result == 0:
        print('Redis Port is Open')
        return 0
    else:
        print('Redis Port is Not Open')
        return 1
 
if __name__ == '__main__':
    Redis_Con('192.168.0.14')

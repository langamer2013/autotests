
import paramiko
import pytest
import re
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor
import sys
import time
import concurrent.futures
import socket

server_ip = '192.168.50.251'
server_dport = 80
cont = '123'
cont = cont.encode("utf-8")

#Задаем параметры для подключения к VPP
vpp_serv = [
    ['root',
    'tester',
    '192.168.50.251']
]

vpp_client = [
    ['root',
    'tester',
    '192.168.50.252']
]

list_commands = [
    'date',
    'sleep 5',
    'date'
]

def start_client(creds, d_ip, dport, sport):
    for user, passwd, ip in creds:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ip, username=user, password=passwd)
        command = f'python3 /root/scripts/socket_client.py {d_ip} {dport} {sport} '
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        print(output)
        print(error)

start_client(vpp_client, '192.168.50.251', 80, 666)




# Запуск функций параллельно в разных процессах
#with concurrent.futures.ThreadPoolExecutor() as executor:
#    future1 = executor.submit(vpp_configuring, vpp_cred1, list_commands)
#    future2 = executor.submit(vpp_configuring, vpp_cred2, list_commands)
#
#    result1 = future1.result()
#    result2 = future2.result()
#
#print(result1)
#print(result2)



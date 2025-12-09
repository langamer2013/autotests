
import paramiko
import pytest
import re
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor
import sys
import time
import concurrent.futures
import socket
import working_func

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

dump = working_func.get_tcpdump(vpp_serv)
pprint(dump)



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



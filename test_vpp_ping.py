
import pytest
import sys
from pprint import pprint
import concurrent.futures
import working_func
import paramiko
import time

#Задаем параметры для подключения к окружению
vpp_client = [
    ['user1',
    '!2345Qwert',
    '192.168.255.52']
]

vpp_serv = [
    ['user1',
    '!2345Qwert',
    '192.168.255.51']
]

vpp = [
    ['user1',
    '!2345Qwert',
    '192.168.255.1']
]

vpp_config_commands = [
    'date',
    'sleep 5',
    'date'
]

#Задаем параметры генерации трафика

#Задаем параметры поиска трафика
parce_sip = '172.16.200.2'
parce_sport = '12345'
parce_dip = '172.16.100.2'
parce_dport = '54321'

#Проверяем статус впп
#if working_func.vpp_check_status(vpp):
#    pass
#else:
#    print('VPP не запущен на сервере!')
#    sys.exit()

#working_func.vpp_stop_start(vpp)

#working_func.vpp_configuring(vpp, vpp_config_commands)

# Запуск функций параллельно в разных процессах
with concurrent.futures.ThreadPoolExecutor() as executor:
    future_server = executor.submit(working_func.start_server, vpp_serv, parce_dport)
    future_client = executor.submit(working_func.start_client, vpp_client, parce_dip, parce_dport, parce_sport)
    future_dump_collector = executor.submit(working_func.get_tcpdump, vpp_serv)

    result_dump = future_dump_collector.result()

#print(result_dump)

#print(working_func.parce_dump(parce_sip, parce_dip, parce_dport, result_dump, parce_sport))



def test_status(status=False):
    assert working_func.parce_dump(parce_sip, parce_dip, parce_dport, result_dump, parce_sport) == True
#print(test_status(working_func.parce_dump(parce_sip, parce_dip, parce_dport, result_dump, parce_sport)))


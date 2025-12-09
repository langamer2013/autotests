
import pytest
import sys
from pprint import pprint
import concurrent.futures
import working_func
import paramiko
import time

#Задаем параметры для подключения к окружению
vpp_client = [
    ['root',
    'tester',
    '192.168.50.252']
]

vpp_serv = [
    ['root',
    'tester',
    '192.168.50.251']
]

vpp = [
    ['root',
    'tester',
    '192.168.50.252']
]

vpp_config_commands = [
    'date',
    'sleep 5',
    'date'
]

#Задаем параметры генерации трафика

#Задаем параметры поиска трафика
parce_sip = '192.168.50.252'
parce_sport = '12345'
parce_dip = '192.168.50.251'
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
    #future_server = executor.submit(working_func.start_server, vpp_serv, parce_dport)
    time.sleep(1)
    future_client = executor.submit(working_func.start_client, vpp_client, parce_dip, parce_dport, parce_sport)
    future_dump_collector = executor.submit(working_func.get_tcpdump, vpp_serv)

    result_dump = future_dump_collector.result()



print(working_func.parce_dump(parce_sip, parce_dip, parce_dport, result_dump, parce_sport))



def test_status(status=False):
    if status == True:
        return True
       
print(test_status(working_func.parce_dump(parce_sip, parce_dip, parce_dport, result_dump, parce_sport)))



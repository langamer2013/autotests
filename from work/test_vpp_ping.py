
import pytest
import sys
from pprint import pprint
import concurrent.futures
import working_func
import paramiko
import time

traffic_must_be_found = True

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
    '192.168.255.1',
    '5002'
    ]
]

vpp_config_commands = [
    'set acl-plugin acl permit',
    'set acl-plugin acl permit'
] 

vpp_clear_config_commands = [
    'del acl-plugin acl index 0',
    'del acl-plugin acl index 1'
]

#Задаем параметры генерации трафика

#Задаем параметры поиска трафика
parce_sip = '172.16.200.2'
parce_sport = '12345'
parce_dip = '172.16.100.2'
parce_dport = '54321'

#Проверяем статус впп
if working_func.vpp_check_status(vpp):
    print('VPP работает!')
else:
    print('VPP не запущен на сервере!')
    sys.exit()

#working_func.vpp_stop_start(vpp)


print('Настраиваем VPP')
working_func.vpp_configuring(vpp[0][2], vpp[0][3], vpp_config_commands)
print('Vpp configured!')

# Запуск функций параллельно в разных процессах
with concurrent.futures.ThreadPoolExecutor() as executor:
    future_dump_collector = executor.submit(working_func.get_tcpdump, vpp_serv)
    future_server = executor.submit(working_func.start_server_curl, vpp_serv, parce_dport)
    future_client = executor.submit(working_func.start_client_curl, vpp_client, parce_dip, parce_dport, parce_sport)
    result_dump = future_dump_collector.result()

#Удаляем конфигурацию в впп
working_func.vpp_configuring(vpp[0][2], vpp[0][3], vpp_clear_config_commands)

#Успешность теста
def test_status(status=False):
    assert working_func.parce_dump(parce_sip, parce_dip, parce_dport, result_dump, parce_sport) == traffic_must_be_found



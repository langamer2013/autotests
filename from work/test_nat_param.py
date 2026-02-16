
import pytest
import sys
from pprint import pprint
import concurrent.futures
import working_func
import paramiko
import time
import sys
traffic_must_be_found = True

#Задаем параметры для подключения к окружению
client = [
    'user1',
    '!2345Qwert',
    '192.168.255.52',
    '22'
]

server = [
    'user1',
    '!2345Qwert',
    '192.168.255.51',
    '22'
]

vpp_ssh = [
    'user1',
    '!2345Qwert',
    '192.168.255.1',
    '22'
]

vpp_telnet = [
    '192.168.255.1',
    '5050'
]

vpp_config_commands = [
    'set acl-plugin acl permit',
    'set acl-plugin acl permit'
] 

vpp_clear_config_commands = [
    'del acl-plugin acl index 0',
    'del acl-plugin acl index 1'
]

#Задаем параметры поиска трафика
#Задаем параметры генерации трафика
traffic_parameters = [
    '172.16.200.2',
    '12345',
    '172.16.100.2',
    '54321'
]

def check_nat(make_config, del_config, vpp_ssh_cred, vpp_telnet_cred, vpp_client_cred, vpp_server_cred, traffic, proto_type='tcp'):
    #Проверяем статус впп
    if working_func.vpp_check_status(vpp_ssh_cred):
        print('VPP работает!')
    else:
        print('VPP не запущен на сервере!')
        sys.exit()
    #Настраиваем впп перед тестом
    working_func.vpp_configuring(vpp_telnet_cred, make_config)
    #Запускаем параллельно 3 сессии запуск трафика, прием трафика, захват трафика на сервере
    if proto_type == 'tcp':
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_dump_collector = executor.submit(working_func.get_tcpdump, vpp_server_cred)
            future_server = executor.submit(working_func.start_server, vpp_server_cred, traffic)
            future_client = executor.submit(working_func.start_client, vpp_client_cred, traffic)
            result_dump = future_dump_collector.result()
    elif proto_type == 'udp':
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_dump_collector = executor.submit(working_func.get_tcpdump, vpp_server_cred)
            future_client = executor.submit(working_func.start_client, vpp_client_cred, traffic, proto=proto_type)
            result_dump = future_dump_collector.result()
    elif proto_type == 'icmp':
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_dump_collector = executor.submit(working_func.get_tcpdump, vpp_server_cred)
            future_client = executor.submit(working_func.start_client, vpp_client_cred, traffic, proto=proto_type)
            result_dump = future_dump_collector.result()
    #Чистим конфигурацию
    working_func.vpp_configuring(vpp_telnet_cred, del_config)
    #Проверяем были ли в захваченном трафике нужные нам пакеты
    if working_func.parce_dump(traffic, result_dump, proto_type):
        return True
    else:
        return False

@pytest.mark.parametrize("vpp_comm, vpp_clear_comm, expected, protocol", [
    ([
    'set acl-plugin acl permit',
    'set acl-plugin acl permit'
    ],
    [
    'del acl-plugin acl index 0',
    'del acl-plugin acl index 1'
    ],
    True,
    'tcp'
    ),
    ([
    'set acl-plugin acl permit',
    'set acl-plugin acl permit'
    ],
    [
    'del acl-plugin acl index 0',
    'del acl-plugin acl index 1'
    ],
    True,
    'icmp'
    ),
    ([
    'set acl-plugin acl permit',
    'set acl-plugin acl permit'
    ],
    [
    'del acl-plugin acl index 0',
    'del acl-plugin acl index 1'
    ],
    True,
    'udp'
    ),
    ([
    'set acl-plugin acl permit',
    'set acl-plugin acl permit'
    ],
    [
    'del acl-plugin acl index 0',
    'del acl-plugin acl index 1'
    ],
    True,
    'icmp'
    ),
])
def test_check_nat(vpp_comm, vpp_clear_comm, expected, protocol):
    assert check_nat(vpp_comm, vpp_clear_comm, vpp_ssh, vpp_telnet, client, server, traffic_parameters, proto_type=protocol)  == expected


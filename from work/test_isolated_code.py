import paramiko
import time
import pytest
import working_func
import re
import pexpect


vpp_user = 'root'
vpp_passwd = 'tester'
vpp_ip = '192.168.50.252'
vpp_config = [
      'cd /home/tester/\n'
      'touch 123\n'
      'touch 456\n'
      
]
vpp_config_del = [
      'cd /home/tester/\n'
      'rm 123\n'
      'rm 456\n'
]

check_vpp_config = [
      'ls -l /home/tester/123\n'
      'ls -l /home/tester/456\n'

]

def prepare_vpp(ip, user, passwd, commands):
       # Создаем SSH клиент
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Подключаемся к удаленной машине
        client.connect(hostname=ip, username=user, password=passwd)
        for command in commands:
            # Выполняем команду
            client.exec_command(command)
            #time.sleep(1)
        client.close()

#prepare_vpp(vpp_ip, vpp_user, vpp_passwd, vpp_config)

def check_prepare_vpp(ip, user, passwd, commands):
    file = True
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())   
        # Подключаемся к удаленной машине
    client.connect(hostname=ip, username=user, password=passwd)
    for command in commands:
            # Выполняем команду
        stdin, stdout, stderr = client.exec_command(command)
        #print(stdout.read().decode())
        error = stderr.read().decode().strip()
        if error:
             file = False
    client.close()
    return file
#check_prepare_vpp(vpp_ip, vpp_user, vpp_passwd, check_vpp_config)
#def test_check():
#     assert check_prepare_vpp(vpp_ip, vpp_user, vpp_passwd, check_vpp_config) == True


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
    'user1',
    '!2345Qwert',
    '10.199.28.53',
    '2201'
]

vpp_config_commands = [
    'set acl-plugin acl permit',
    'set acl-plugin acl permit'
] 

vpp_clear_config_commands = [
    'del acl-plugin acl index 0',
    'del acl-plugin acl index 1'
]

vpp_telnet = [
    '10.199.28.53',
    '5050'
]
'''
#Функция заходит на VPP по ssh и проверяет статус демона, если активен - возвращает True, нет - возвращает False
def vpp_configuring(creds, commands):
    ip, port = creds
    telnet_param = f"telnet {ip} {port}"
    telnet = pexpect.spawn(telnet_param)
    for com in commands:
        telnet.expect('vpp#')
        telnet.sendline(com)
        telnet.sendline('')
        telnet.expect('vpp#')
    telnet.close()
    
#print(working_func.vpp_check_status(vpp))

vpp_configuring(vpp_telnet, vpp_config_commands)
'''



def start_client(creds, traffic, proto='tcp'):
    d_ip = traffic
    user, passwd, ip, p = creds
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username=user, password=passwd, port=p, allow_agent=False)
    command = f'sleep 1; ping -c5 {d_ip}'
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    print(error)
    print(output)
    client.close()

start_client(vpp, '172.16.100.1')
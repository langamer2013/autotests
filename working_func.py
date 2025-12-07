import paramiko
import pytest
import re
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor
import sys
import time
import socket

#Функция заходит на VPP по ssh и проверяет статус демона, если активен - возвращает True, нет - возвращает False
def vpp_check_status(creds):
    for user, passwd, ip in creds:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ip, username=user, password=passwd)
        stdin, stdout, stderr = client.exec_command('systemctl status sshd')
        output = stdout.read().decode()
        errors = stderr.read().decode()
        if errors:
            print('Не удалось определить статус VPP, ошибка:')
            print(errors)
            sys.exit()
        if re.search(r'Loaded: loaded', output) and re.search(r'Active: active \(running\)', output):
            return True
        else:
            return False

#Функция заходит на VPP по ssh и делает стоп/старт демона vpp с интерфалом 10 секунд
def vpp_stop_start(creds):
    list_commands = [
    'systemctl stop systemd-journald.service',
    'sleep 10',
    'systemctl start systemd-journald.service',
    'sleep 10',
    'systemctl status systemd-journald.service'
]
    for user, passwd, ip in creds:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ip, username=user, password=passwd)
        for comm in list_commands:
            stdin, stdout, stderr = client.exec_command(comm)
            output = stdout.read().decode()
            errors = stderr.read().decode()
            #if errors:
            #    print('Не удалось перезапустить VPP, ошибка:')
            #    print(errors)
            #    sys.exit()
            if comm == 'systemctl status systemd-journald.service':
                if re.search(r'Loaded: loaded', output) and re.search(r'Active: active \(running\)', output):
                    return True
                else:
                    return False

#Функция заходит на VPP по ssh и выполняет команды по настройке
def vpp_configuring(creds, commands):
    for user, passwd, ip in creds:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ip, username=user, password=passwd)
        for comm in commands:
            stdin, stdout, stderr = client.exec_command(comm)
            time.sleep(2)
            output = stdout.read().decode()
            errors = stderr.read().decode()
            if errors:
                print('Не удалось настроить VPP, ошибка:')
                print(errors)
                sys.exit()

#Функция подключается на сервер и запускает там питоновский скрипт который слушает сокет на определенном порту, 
# порт передает как аргумет для запуска
def start_server(creds, listen_port):
    for user, passwd, ip in creds:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ip, username=user, password=passwd)
        command = f'python3 /root/scripts/socket_server.py {listen_port}'
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        print(output)
        print(error)

#Функция подключается на кдиента и запускает там питоновский скрипт который пытаелся открыть соединение
# ип порт и сурс порт задается как параметрами запуска
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




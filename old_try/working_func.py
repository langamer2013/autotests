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
        stdin, stdout, stderr = client.exec_command('sudo systemctl status sshd')
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
    'sudo systemctl stop systemd-journald.service',
    'sudo sleep 10',
    'sudo systemctl start systemd-journald.service',
    'sudo sleep 10',
    'sudo systemctl status systemd-journald.service'
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
            if comm == 'sudo systemctl status systemd-journald.service':
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
        command = f'sudo timeout 7s python3 /root/scripts/socket_server.py {listen_port}'
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

#Функция подключается на кдиента и запускает там питоновский скрипт который пытается открыть соединение
# ип порт и сурс порт задается как параметрами запуска
def start_client(creds, d_ip, dport, sport):
    for user, passwd, ip in creds:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ip, username=user, password=passwd)
        command = f'sudo timeout 5s python3 /root/scripts/socket_client.py {d_ip} {dport} {sport} '
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        print(error)

# Функция для захвата трафика, возвращает список строк с дампом
def get_tcpdump(creds):
    output = []
    for user, passwd, ip in creds:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ip, username=user, password=passwd)
        stdin, stdout, stderr = client.exec_command('sudo timeout 10s tcpdump -ni any')
        dumped_traff = stdout.read().decode().split('\n')
        for line in dumped_traff:
            output.append(line)
    return output

#Функция парсинга полученного дампа на приедмет наличия в нем необходимого трафика
#sip - ип источника для поиска 
#dip ип назначения для поиска
#dport порт назначения для поиска
#sport порт источника для поиска если задан
#Список содержащий строки из дампа
#Возвращает true если найдено совпадение в дампе иначе false
def parce_dump(sip, dip, dport, lines, sport=None):
    finded = False
    to_find = f"{sip}.{sport} > {dip}.{dport}"
    for line in lines:
        if to_find in line:
            finded = True
            return finded


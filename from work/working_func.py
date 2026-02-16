import re
import sys
import time

import paramiko
import pexpect


# Функция заходит на VPP по ssh и проверяет статус демона, если активен - возвращает True, нет - возвращает False
def vpp_check_status(creds):
    user, passwd, ip, port = creds
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username=user, password=passwd, port=port, allow_agent=False)
    stdin, stdout, stderr = client.exec_command('sudo systemctl status dozor_ngfw_vpp')
    output = stdout.read().decode()
    errors = stderr.read().decode()
    if errors:
        print('Не удалось определить статус VPP, ошибка:')
        print(errors)
        sys.exit()
    client.close()
    if re.search(r'Loaded: loaded', output) and re.search(r'Active: active \(running\)', output):
        return True
    else:
        return False


# Функция заходит на VPP по ssh и делает стоп/старт демона vpp с интервалом 10 секунд
def vpp_stop_start(creds):
    list_commands = [
        'sudo systemctl stop dozor_ngfw_vpp',
        'sudo sleep 1',
        'sudo systemctl start dozor_ngfw_vpp',
        'sudo sleep 15',
        'sudo systemctl status dozor_ngfw_vpp'
    ]
    user, passwd, ip, port = creds
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username=user, password=passwd, port=port, allow_agent=False)
    for comm in list_commands:
        stdin, stdout, stderr = client.exec_command(comm)
        output = stdout.read().decode()
        errors = stderr.read().decode()
        #if errors:
        #    print('Не удалось перезапустить VPP, ошибка:')
        #    print(errors)
        #    sys.exit()
        if comm == 'sudo systemctl status dozor_ngfw_vpp':
            if re.search(r'Loaded: loaded', output) and re.search(r'Active: active \(running\)', output):
                return True
            else:
                return False
    client.close()


# Функция заходит на VPP по ssh и выполняет команды по настройке
def vpp_configuring_old(creds, commands):
    user, passwd, ip, p = creds
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username=user, password=passwd, port=p, allow_agent=False)
    for comm in commands:
        stdin, stdout, stderr = client.exec_command(comm)
        time.sleep(2)
        output = stdout.read().decode()
        errors = stderr.read().decode()
        if errors:
            print('Не удалось настроить VPP, ошибка:')
            print(errors)
            sys.exit()
    client.close()


# Функция для конфигурации впп
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


# Функция подключается на сервер и запускает там питоновский скрипт который слушает сокет на определенном порту,
# порт передает как аргумет для запуска
def start_server_socket(creds, traffic):
    user, passwd, ip, p = creds
    *_, listen_port = traffic
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username=user, password=passwd, port=p, allow_agent=False)
    command = f'sudo timeout 7s python3 /root/scripts/socket_server.py {listen_port}'
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()


# Функция подключается на кдиента и запускает там питоновский скрипт который пытается открыть соединение
# ип порт и сурс порт задается как параметрами запуска
def start_client_socket(creds, traffic):
    _, sport, d_ip, dport = traffic
    user, passwd, ip, p = creds
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username=user, password=passwd, port=p, allow_agent=False)
    command = f'sudo timeout 5s python3 /root/scripts/socket_client.py {d_ip} {dport} {sport} '
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    print(error)


# Функция для захвата трафика, возвращает список строк с дампом
def get_tcpdump(creds):
    output = []
    user, passwd, ip, p = creds
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username=user, password=passwd, port=p, allow_agent=False)
    stdin, stdout, stderr = client.exec_command('sudo timeout 7s tcpdump -ni any')
    dumped_traff = stdout.read().decode().split('\n')
    for line in dumped_traff:
        output.append(line)
    client.close()
    return output


# Функция парсинга полученного дампа на предмет наличия в нем необходимого трафика
# sip - ип источника для поиска
# dip ип назначения для поиска
# dport порт назначения для поиска
# sport порт источника для поиска если задан
# Список содержащий строки из дампа
# Возвращает true если найдено совпадение в дампе иначе false
def parce_dump(traffic, lines, proto):
    sip, sport, dip, dport = traffic
    found = False
    to_find = f"{sip}.{sport} > {dip}.{dport}"
    if proto == 'icmp':
        for line in lines:
            if sip in line and 'ICMP' in line and dip in line:
                found = True
                return found
    for line in lines:
        if to_find in line:
            found = True
            return found


# Функция подключается на клиента и запускает там curl до с заданными параметрами
# ип порт и сурс порт задается как параметрами запуска
def start_client(creds, traffic, proto='tcp'):
    _, sport, d_ip, dport, = traffic
    user, passwd, ip, p = creds
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username=user, password=passwd, port=p, allow_agent=False)
    if proto == 'tcp':
        command = f'sleep 1;curl --connect-timeout 1 --retry 3 --retry-delay 1 --local-port {sport} -s -o /dev/null {d_ip}:{dport}'
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        print(error)
        client.close()
    elif proto == 'udp':
        command = f'sleep 1; echo "Best UDP test" | nc -u {d_ip} {dport} -p {sport}'
        stdin, stdout, stderr = client.exec_command(command)
        stdin, stdout, stderr = client.exec_command(command)
        stdin, stdout, stderr = client.exec_command(command)
        stdin, stdout, stderr = client.exec_command(command)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        print(error)
        client.close()
    elif proto == 'icmp':
        command = f'sleep 3; timeout 2s ping -c5 -f -i0.2 {d_ip}'
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        print(error)
        client.close()


# Функция подключается на сервер и запускает там питоновский  http сервер на определенном порту
def start_server(creds, traffic):
    *_, listen_port = traffic
    user, passwd, ip, p = creds
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=ip, username=user, password=passwd, port=p, allow_agent=False)
    command = f'sudo timeout 7s python3 -m http.server {listen_port}'
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    client.close()

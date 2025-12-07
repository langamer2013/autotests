import paramiko
import time
import pytest
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

prepare_vpp(vpp_ip, vpp_user, vpp_passwd, vpp_config)

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
def test_check():
     assert check_prepare_vpp(vpp_ip, vpp_user, vpp_passwd, check_vpp_config) == True
     
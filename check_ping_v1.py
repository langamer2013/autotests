import paramiko
import re
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor

client_ip = "192.168.50.252"
server_ip = "192.168.50.251"

# Функция для выполнения списка команд на удаленной машине
def execute_commands(host, username, password, commands):
    results = []
    try:
        # Создаем SSH клиент
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Подключаемся к удаленной машине
        client.connect(hostname=host, username=username, password=password)
        
        for command in commands:
            # Выполняем команду
            stdin, stdout, stderr = client.exec_command(command)
            
            # Получаем вывод команды
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            # Сохраняем результат
            results.append((command, output, error))
        
        # Закрываем соединение
        client.close()
        return (host, results)
    
    except Exception as e:
        return (host, str(e))

# Список виртуальных машин с соответствующими командами
hosts_commands = [
    {
        'host': '192.168.50.252',
        'username': 'root',
        'password': 'tester',
        'commands': ['ping -c5 192.168.50.251', 'uname -a', 'ls -l']
    },
    {
        'host': '192.168.50.251',
        'username': 'root',
        'password': 'tester',
        'commands': ['sudo timeout 5s tcpdump -ni enp0s3 icmp']
    }
    # Добавьте другие машины и команды по мере необходимости
]

# Используем ThreadPoolExecutor для параллельного выполнения
with ThreadPoolExecutor(max_workers=len(hosts_commands)) as executor:
    futures = []
    for host_info in hosts_commands:
        futures.append(executor.submit(execute_commands, host_info['host'], host_info['username'], host_info['password'], host_info['commands']))      
    for future in futures:
        host, results = future.result()
        if host == server_ip:
            tcpdump_output = []
            for i in results[0][1].rstrip().split('\n'):
                if re.findall(r'192.168.5', i):
                    tcpdump_output.append(re.findall(r'192.168.5', i))
            #print(f'Host: {host}')
            #for command, output, error in results:
                #print(f'Command: {command}\nOutput: \n{output}\nError: {error}\n')

print(tcpdump_output)

if tcpdump_output:
    print('Пинг прошел!')
else:
    print("Тест провален!")


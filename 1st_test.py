
from pprint import pprint
import paramiko
import time
from concurrent.futures import ThreadPoolExecutor

client_ip = "192.168.50.252"
server_ip = ""
username = "tester"
password = "tester"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(client_ip, username="tester", password="tester", look_for_keys=False, allow_agent=False)

ssh = client.invoke_shell()
ssh.send("ping -c5 192.168.50.251\n")
time.sleep(6)

a = ssh.recv(3000).decode("utf-8")
print(type(a))
pprint(a.split("\n"))
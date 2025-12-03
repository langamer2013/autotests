
from pprint import pprint
import paramiko
import time
from concurrent.futures import ThreadPoolExecutor

client_ip = "192.168.50.252"
server_ip = "192.168.50.251"
user = "root"
passwd = "tester"

client_client = paramiko.SSHClient()
client_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client_client.connect(client_ip, username=user, password=passwd, look_for_keys=False, allow_agent=False)

ssh_client = client_client.invoke_shell()
ssh_client.send("ping -c5 192.168.50.251\n")
time.sleep(6)

client_server = paramiko.SSHClient()
client_server.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client_server.connect(server_ip, username="tester", password="tester", look_for_keys=False, allow_agent=False)

ssh_server = client_server.invoke_shell()
ssh_server = client_client.invoke_shell()
ssh_server.send("sudo -s\n")
ssh_server.send("tester\n")
time.sleep(1)
ssh_server.send("timeout 5s tcpdump -ni enp0s3 icmp\n")
time.sleep(6)





client_screen = ssh_client.recv(3000).decode("utf-8")
server_screen = ssh_server.recv(3000).decode("utf-8")

pprint(client_screen.split("\n"))
pprint("-" * 50)
pprint(server_screen.split("\n"))
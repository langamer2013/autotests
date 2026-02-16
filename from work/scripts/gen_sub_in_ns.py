#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pprint import pprint
import subprocess
import ipaddress
import time
#Скрипт генерирует необходимое колво сабинтерфейсов с учетом заданных параметров

list_interfacies = []
list_ns = []
list_vlan = []
list_iterations = []
list_ip_interfacies = []

#Забиваем параметры генерации
for i in range(1,5):
    list_interfacies.append(f"tap{i}")

for i in range(1,17):
    list_ns.append(f"ns{i}")

for i in range(3,4095):
    list_vlan.append(i)

for i in range(1,10000):
    list_iterations.append(i)

big_net = ipaddress.ip_network('100.0.0.0/8')
for i in big_net.subnets(new_prefix=22):
    list_ip_interfacies.append(i[1])


#Создаем неймспейсы
for create_ns in list_ns:
    subprocess.run(f"ip netns add {create_ns}", shell=True, capture_output=True, text=True)
time.sleep(30)
current_int = 0
current_ns = 0
current_vlan = 0
current_ip_int = 0

print('start ', time.strftime("%H:%M:%S"))

for i in list_iterations:
    if current_vlan == 750 or current_vlan == 1500 or current_vlan == 2250 or current_vlan == 3000 or current_vlan == 3750:
        current_ns += 1
    if current_vlan == 3750:
        current_vlan = 3
        current_int += 1
    interface = list_interfacies[current_int]
    ns = list_ns[current_ns]
    vlan = list_vlan[current_vlan]
    ip_int = list_ip_interfacies[current_ip_int]
    #print(f"ip link add link {interface} name {interface}.{vlan} type vlan id {vlan}")
    #print(f"ip addr add {ip_int} dev {interface}.{vlan}")
    #print(f"ip link set dev {interface}.{vlan} up")
    #print(f"ip link set {interface}.{vlan} netns {ns}")
    #print(f"ip netns exec {ns} ip link set up {interface}.{vlan}")
    #print(f"ip netns exec {ns} ip add add {ip_int}/30 dev {interface}.{vlan}")
    subprocess.run(f"ip link add link {interface} name {interface}.{vlan} type vlan id {vlan}", shell=True)
    subprocess.run(f"ip addr add {ip_int}/30 dev {interface}.{vlan}", shell=True)
    subprocess.run(f"ip link set dev {interface}.{vlan} up", shell=True)
    subprocess.run(f"ip link set {interface}.{vlan} netns {ns}", shell=True)
    subprocess.run(f"ip netns exec {ns} ip link set up {interface}.{vlan}", shell=True)
    subprocess.run(f"ip netns exec {ns} ip add add {ip_int}/30 dev {interface}.{vlan}", shell=True)
    time.sleep(0.15)
    current_vlan += 1
    current_ip_int += 1

print('end ', time.strftime("%H:%M:%S"))

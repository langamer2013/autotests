# Тест выполняет проверку балансировки трафика ECMP при 2 группах.
# Для запуска необходим Mininet https://mininet.org/download/#option-2-native-installation-from-source
# Рекомендуется использовать Ubuntu 22.04.5
# Скрипт запускает mininet со следующей топологией, генерирует NUMBER_OF_PACKETS_TO_SEND с хоста h1
# Параметры генерируемого трафика tcp SYN, rand SRC 10.0.0.128/25:4444, DST 1.1.1.1:80
# Собирает статистику с выходных портов r1, определяет разницу в % между этими значениями и возвращает FALSE, если разница больше или равна ACCEPTABLE_FLOW_DIFFERENCE
#        [  h1  ] (Host 1)
#
#           | .1
#           |
#     (eth0)| 10.0.0.0/24
#
#           |
#           | .2
#        [  r1  ] (Router 1)
#        /      \
#   .1  /        \ .1
# (eth1)          (eth2)
#     / 10.0.1.0/24 \ 10.0.2.0/24
#    /                \
#   / .2            .2 \
# [  r2  ]          [  r3  ] (Routers 2 & 3)
#   \ .1            .1 /
# (eth1)          (eth1)
#     \ 10.0.3.0/24 / 10.0.4.0/24
#      \           /
#    .2 \         / .2
#     (eth0)    (eth1)
#        [  h2  ] (Host 2)
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info

NUMBER_OF_PACKETS_TO_SEND = 1000  # Сколько будет генерировать пакетов
ACCEPTABLE_FLOW_DIFFERENCE = 5  # Сколько % допустима разница между ECMP группами


# Функция принимает имя устройства и имя интерфейса, возвращает кол-во tx пакетов с это интерфейса
def get_packet_count(device, interface):
    tx_packets = device.cmd(f'cat /sys/class/net/{interface}/statistics/tx_packets')
    return int(tx_packets)


def mynetwork():
    net = Mininet(topo=None, build=False)
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.3.2/24')  # Основной IP на первом интерфейсе

    # Роутеры в Mininet — это хосты с включенным форвардингом
    r1 = net.addHost('r1', ip='10.0.0.2/24')
    r2 = net.addHost('r2', ip='10.0.1.2/24')
    r3 = net.addHost('r3', ip='10.0.2.2/24')

    # info('*** Creating links\n')
    # Описываем физические подключения в топологии
    net.addLink(h1, r1)  # h1-eth0 <-> r1-eth0
    net.addLink(r1, r2)  # r1-eth1 <-> r2-eth0
    net.addLink(r1, r3)  # r1-eth2 <-> r3-eth0
    net.addLink(r2, h2)  # r2-eth1 <-> h2-eth0
    net.addLink(r3, h2)  # r3-eth1 <-> h2-eth1 (второй линк к h2)

    net.start()

    # info('*** Configuring IP forwarding and manual IP/Routes\n')
    # Включаем форвардинг на роутерах
    for r in [r1, r2, r3]:
        r.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Настройка IP на дополнительных интерфейсах
    r1.setIP('10.0.1.1/24', intf='r1-eth1')
    r1.setIP('10.0.2.1/24', intf='r1-eth2')
    r2.setIP('10.0.3.1/24', intf='r2-eth1')
    r3.setIP('10.0.4.1/24', intf='r3-eth1')
    h2.setIP('10.0.4.2/24', intf='h2-eth1')

    # Настройка маршрутов
    h1.cmd('ip route add default via 10.0.0.2')
    r1.cmd('ip route add 1.1.1.1 nexthop via 10.0.1.2 dev r1-eth1 weight 1 nexthop via 10.0.2.2 dev r1-eth2 weight 1')
    r2.cmd('ip route add default via 10.0.3.2')
    r3.cmd('ip ro add default via 10.0.4.2')
    h1.cmd(
        f'python3 -c "from scapy.all import *; sendp(Ether()/IP(dst=\'1.1.1.1\', src=RandIP(\'10.0.0.128/25\'))/TCP(dport=80, sport=444, flags=\'S\'), iface=\'h1-eth0\', count={NUMBER_OF_PACKETS_TO_SEND})"')
    tx_percent_interface1 = round((get_packet_count(r1, 'r1-eth1') / NUMBER_OF_PACKETS_TO_SEND) * 100, 2)
    tx_percent_interface2 = round((get_packet_count(r1, 'r1-eth2') / NUMBER_OF_PACKETS_TO_SEND) * 100, 2)
    # CLI(net)
    net.stop()
    if round(abs(tx_percent_interface1 - tx_percent_interface2)) >= ACCEPTABLE_FLOW_DIFFERENCE:
        return False
    else:
        return True


if __name__ == '__main__':
    mynetwork()

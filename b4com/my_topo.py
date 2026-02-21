from mininet.net import Mininet
from mininet.node import Host
from mininet.cli import CLI
from mininet.log import setLogLevel, info


def mynetwork():
    net = Mininet(topo=None, build=False)

    info('*** Adding nodes\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.3.2/24')  # Основной IP на первом интерфейсе

    # Роутеры в Mininet — это хосты с включенным форвардингом
    r1 = net.addHost('r1', ip='10.0.0.2/24')
    r2 = net.addHost('r2', ip='10.0.1.2/24')
    r3 = net.addHost('r3', ip='10.0.2.2/24')

    info('*** Creating links\n')
    net.addLink(h1, r1)  # h1-eth0 <-> r1-eth0
    net.addLink(r1, r2)  # r1-eth1 <-> r2-eth0
    net.addLink(r1, r3)  # r1-eth2 <-> r3-eth0
    net.addLink(r2, h2)  # r2-eth1 <-> h2-eth0
    net.addLink(r3, h2)  # r3-eth1 <-> h2-eth1 (второй линк к h2)

    net.start()

    info('*** Configuring IP forwarding and manual IP/Routes\n')
    # Включаем форвардинг на роутерах
    for r in [r1, r2, r3]:
        r.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Настройка IP на дополнительных интерфейсах
    # r1: eth1 (к r2) уже имеет IP из конструктора, настроим eth2 (к r3)
    r1.setIP('10.0.1.1/24', intf='r1-eth1')
    r1.setIP('10.0.2.1/24', intf='r1-eth2')
    r2.setIP('10.0.3.1/24', intf='r2-eth1')
    r3.setIP('10.0.4.1/24', intf='r3-eth1')

    # h2: настраиваем второй интерфейс (от r3)
    h2.setIP('10.0.4.2/24', intf='h2-eth1')

    # Настройка маршрутов, чтобы h1 видел h2 через r1
    h1.cmd('ip route add default via 10.0.0.2')
    r1.cmd('ip route add 1.1.1.1 nexthop via 10.0.1.2 dev r1-eth1 weight 1 nexthop via 10.0.2.2 dev r1-eth2 weight 1')
    r2.cmd('ip route add default via 10.0.3.2')
    r3.cmd('ip ro add default via 10.0.4.2')
    # h2.cmd('ip route add default via 10.0.0.4') # По умолчанию через r2

    CLI(net)
    h1.cmd(
        'python3 -c "from scapy.all import *; send(IP(dst=\'1.1.1.1\', src=RandIP(\'10.0.0.128/25\', sport=444 ))/TCP(dport=80, flags=\'S\'), count=5000)"')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    mynetwork()


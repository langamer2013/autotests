import socket
import sys
import time

destination_ip = sys.argv[1]
destination_port = int(sys.argv[2])
source_port = int(sys.argv[3])
time.sleep(2)

def client_socket(d_ip, dport, sport):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.bind(('', sport))
    clientsocket.connect((d_ip, dport))
    clientsocket.send('hello'.encode("utf-8"))

client_socket(destination_ip, destination_port, source_port)

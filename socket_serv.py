import socket
import sys
listening_port = int(sys.argv[1])
def server_socket(port):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('0.0.0.0', port))
    serversocket.listen(5)
    while True:
        connection, address = serversocket.accept()
        buf = connection.recv(64)
        if len(buf) > 0:
            print (buf)
            break
server_socket(listening_port)

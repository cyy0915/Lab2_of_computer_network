import socket

c = socket.socket()
host = socket.gethostname()
port = 2680
c.connect((host, port))
print(c.recv(1024).decode())
print(c.recv(1024).decode())
c.close()
import socket
import threading
import os

s = socket.socket()
host = socket.gethostname()
port = 2680
s.bind((host, port))

s.listen(5)

c,addr = s.accept()
print(addr)
c.send("hellow world".encode('utf-8'))
c.send('a'.encode('utf-8'))
c.recv(1024)
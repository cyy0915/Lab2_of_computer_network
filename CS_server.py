import socket
import threading
import os
from FileTransfer import *

def sendFiletoClient(c, file, filename):
    sendFile(c, file, filename)
    print("success")
    c.close()

s = socket.socket()
host = socket.gethostname()
port = 2680
s.bind((host, port))
s.listen(10)

filename = input("filename:")
file = open(filename, 'rb')
filecontent = file.read()
while True:
    c,addr = s.accept()
    c.sendall()
    t = threading.Thread(target=sendFiletoClient, args=(c, filecontent, filename))
    t.start()

import socket
from FileTransfer import *

c = socket.socket()
host = '10.0.0.1'
port = 2680
c.connect((host, port))
recvFile(c)
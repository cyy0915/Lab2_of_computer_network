import socket
from FileTransfer import *

c = socket.socket()
host = socket.gethostname()
port = 2680
c.connect((host, port))
recvFile(c)
import socket
import threading
import os
from FileTransfer import *
import time

filename = '1Mtest'
cnum = 5

def sendFiletoClient(c, file, filename):
    sendFile(c, file, filename)
    print("success")
    c.close()
    mutex.acquire()
    endTime[0] = time.time()
    endTimeCount[0] += 1
    log = open('../timelog', 'a')
    log.write(str(endTime[0]-startTime[0])+'\t')
    log.close()
    mutex.release()

s = socket.socket()
host = '10.0.0.1'
port = 2680
s.bind((host, port))
s.listen(10)

file = open(filename, 'rb')
filecontent = file.read()
mutex = threading.Lock()
log = open('../timelog', 'a')
log.write('\nC/S: ')
log.close()
while True:
    c,addr = s.accept()
    startTime = [time.time()]
    endTime = [0]
    endTimeCount = [0]
    t = threading.Thread(target=sendFiletoClient, args=(c, filecontent, filename))
    t.start()

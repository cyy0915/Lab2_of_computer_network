import socket
import threading
import os
from FileTransfer import *
import sys
import json
import time

filename = '1Mtest'
num = 6

def findAvaliable(clientState, partID):
    result = []
    for i in range(len(clientState)):
        if clientState[i][partID]==1:
            result.append(clientAddr[i])
    return result

def safeSendFile(c, fileContent, require, filename):
    busyStateMutex.acquire()
    isBusy[0] = True
    busyStateMutex.release()
    sendFile(c, fileContent[require], str(require)+filename)
    busyStateMutex.acquire()
    isBusy[0] = False
    busyStateMutex.release()

def sendFiletoClient(c, fileContent, filename, num, cID):
    #init
    clientStateMutex.acquire()
    clientState.append([0] * num)
    clientStateMutex.release()
    initInfo = {'filename': filename, 'partNum': num, 'cID': cID}
    c.send(json.dumps(initInfo).encode('utf-8'))
    #loop
    while True:
        currentState = json.loads(c.recv(1024).decode('utf-8'))
        clientStateMutex.acquire()
        clientState[cID] = currentState['state']
        clientStateMutex.release()
        require = currentState['require']
        if (require==-1):
            break
        clientStateMutex.acquire()
        avaliableHost = findAvaliable(clientState, currentState['require'])
        clientStateMutex.release()
        if len(avaliableHost)==0:
            c.send(json.dumps('me').encode('utf-8'))
            c.recv(1024)
            safeSendFile(c, fileContent, require, filename)
        else:
            tmp = {'avaliableHost': avaliableHost, 'isBusy': isBusy[0]}
            c.send(json.dumps(tmp).encode('utf-8'))
            if c.recv(1024).decode('utf-8')=='yes':
                safeSendFile(c, fileContent, require, filename)
    c.close()
    #record time
    timeMutex.acquire()
    endTime[0] = time.time()
    endTimeCount[0]+=1
    log = open('../timelog', 'a')
    log.write(str(endTime[0]-startTime[0])+'\t')
    log.close()
    timeMutex.release()
    

s = socket.socket()
host = '10.0.0.1'
port = 2680
s.bind((host, port))
s.listen(10)

#read and divide file
file = open(filename, 'rb')
fileSize = os.path.getsize(filename)
partSize = int(fileSize / num)
lastPartSize = fileSize - (num-1)*partSize
fileContent = [0]*num
for i in range(num):
    if i!=num-1:
        fileContent[i] = file.read(partSize)
    else:
        fileContent[i] = file.read(lastPartSize)

#init var
clientState = []
clientAddr = []
isBusy = [False]
cID = 0
busyStateMutex = threading.Lock()
clientStateMutex = threading.Lock()
timeMutex = threading.Lock()
log = open('../timelog', 'a')
log.write('\nP2P: ')
log.close()

#start listen
while True:
    print('start listen')
    c,addr = s.accept()
    startTime = [time.time()]
    endTime = [0]
    endTimeCount = [0]
    tmp = json.loads(c.recv(1024).decode('utf-8'))
    addr = (addr[0], tmp)
    clientAddr.append(addr)
    t = threading.Thread(target=sendFiletoClient, args=(c, fileContent, filename, num, cID))
    cID += 1
    t.start()

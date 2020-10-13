import socket
import threading
import os
from FileTransfer import *
import sys
import json

def findAvaliable(clientState, partID):
    result = []
    for i in range(len(clientState)):
        if clientState[i][partID]==1:
            result.append(clientAddr[i])
    return result

def sendFiletoClient(c, fileContent, filename, num, cID):
    #init
    clientState.append([0] * num)
    initInfo = {'filename': filename, 'partNum': num, 'cID': cID}
    c.send(json.dumps(initInfo).encode('utf-8'))
    #loop
    while True:
        currentState = json.loads(c.recv(1024).decode('utf-8'))
        clientState[cID] = currentState['state']
        require = currentState['require']
        if (require==-1):
            break
        avaliableHost = findAvaliable(clientState, currentState['require'])
        if len(avaliableHost)==0:
            c.send(json.dumps('me').encode('utf-8'))
            c.recv(1024)
            isBusy[0] = True
            sendFile(c, fileContent[require], str(require)+filename)
            #isBusy[0] = False
        else:
            tmp = {'avaliableHost': avaliableHost, 'isBusy': isBusy[0]}
            c.send(json.dumps(tmp).encode('utf-8'))
            if c.recv(1024).decode('utf-8')=='yes':
                isBusy[0] = True
                sendFile(c, fileContent[require], str(require) + filename)
                #isBusy[0] = False
    c.close()


s = socket.socket()
host = socket.gethostname()
port = 2680
s.bind((host, port))
s.listen(10)

filename = 'test.exe'
file = open(filename, 'rb')
fileSize = os.path.getsize(filename)
num = 4
partSize = int(fileSize / num)
lastPartSize = fileSize - (num-1)*partSize
fileContent = [0]*num
for i in range(num):
    if i!=num-1:
        fileContent[i] = file.read(partSize)
    else:
        fileContent[i] = file.read(lastPartSize)
clientState = []
clientAddr = []
isBusy = [False]
cID = 0
while True:
    c,addr = s.accept()
    tmp = json.loads(c.recv(1024).decode('utf-8'))
    addr = (addr[0], tmp)
    clientAddr.append(addr)
    t = threading.Thread(target=sendFiletoClient, args=(c, fileContent, filename, num, cID))
    cID += 1
    t.start()
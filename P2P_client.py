from FileTransfer import *
import socket
import threading
import os
import sys
import json
import random

clientSendPort = 2690

def nextPart(cID, num):
    n = cID % num
    count = 0
    while clientState[n]!=0:
        n = (n+1)%num
        count += 1
        if count > num:
            return -1
    return n

def combineFile(filename, num):
    f = open('full'+filename, 'wb')
    for i in range(num):
        partf = open(str(i)+filename, 'rb')
        f.write(partf.read())
        partf.close()
    f.close()

def sendThread(filename):
    s = socket.socket()
    host = socket.gethostname()
    port = clientSendPort
    s.bind((host, port))
    s.listen(10)
    while True:
        sendClient, addr = s.accept()
        t = threading.Thread(target=sendSubThread, args=(sendClient, filename))
        t.start()

def sendSubThread(sendClient, filename):
    require = int(sendClient.recv(1024).decode('utf-8'))
    sendClient.send(json.dumps(isBusy[0]).encode('utf-8'))
    if sendClient.recv(1024).decode('utf-8')=='yes':
        sendFileContent = open(str(require)+filename, 'rb').read()
        isBusy[0] = True
        sendFile(sendClient, sendFileContent, str(require)+filename)
        isBusy[0] = False
        sendClient.close()
    else:
        sendClient.close()

def recvThread(c, cID, num, filename):
    while True:
        #require part
        require = nextPart(cID, num)
        sendmsg = {'require': require, 'state': clientState}
        c.send(json.dumps(sendmsg).encode('utf-8'))
        if require==-1:
            break
        tmp = c.recv(1024).decode('utf-8')
        recvmsg = json.loads(tmp)
        #receive avaliable host
        if recvmsg == 'me':
            c.send('prepared'.encode('utf-8'))
            recvFile(c)
        else:
            availableHostAddr = recvmsg['avaliableHost']
            freeHost = []
            if recvmsg['isBusy']==False:
                freeHost.append(c)
            conList = [c]
            for addr in availableHostAddr:
                con = socket.socket()
                con.connect((addr[0], addr[1]))
                conList.append(con)
                con.send(str(require).encode('utf-8'))
                if json.loads(con.recv(1024).decode('utf-8'))==False:
                    freeHost.append(con)
            #choose host and receive file
            tmpList = []
            if len(freeHost)==0:
                choiceHost = random.choice(conList)
            else:
                choiceHost = random.choice(freeHost)
            #close extra
            conList.remove(choiceHost)
            for con in conList:
                con.send('no'.encode('utf-8'))
            ##
            choiceHost.send('yes'.encode('utf-8'))
            recvFile(choiceHost)

        clientState[require]=1
    c.close()
    combineFile(filename, num)

c = socket.socket()
host = socket.gethostname()
port = 2680
c.connect((host, port))
#init
c.send(json.dumps(clientSendPort).encode('utf-8'))
initInfo = json.loads(c.recv(1024).decode('utf-8'))
num = initInfo['partNum']
cID = initInfo['cID']
filename = initInfo['filename']
clientState = [0]*num
isBusy = [False]

st = threading.Thread(target=sendThread, args=(filename,))
rt = threading.Thread(target=recvThread, args=(c, cID, num, filename))
st.start()
rt.start()
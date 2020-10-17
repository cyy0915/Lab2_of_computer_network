from FileTransfer import *
import socket
import threading
import os
import sys
import json
import random
import psutil

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

def sendThread(filename, cID):
    s = socket.socket()
    host = ''
    for name, netCardInfo in psutil.net_if_addrs().items():
        if name != 'lo':
            for ip in netCardInfo:
                if ip.family == socket.AF_INET:
                    host = ip.address
    port = clientSendPort
    s.bind((host, port))
    s.listen(10)
    while True:
        sendClient, addr = s.accept()
        t = threading.Thread(target=sendSubThread, args=(sendClient, filename, cID, addr))
        t.start()

def sendSubThread(sendClient, filename, cID, addr):
    require = int(sendClient.recv(1024).decode('utf-8'))
    sendClient.send(json.dumps(isBusy[0]).encode('utf-8'))
    msg = sendClient.recv(1024).decode('utf-8')
    if msg=='yes':
        sendFileContent = open(str(require)+filename, 'rb').read()
        mutex.acquire()
        isBusy[0] = True
        mutex.release()
        sendFile(sendClient, sendFileContent, str(require)+filename)
        mutex.acquire()
        isBusy[0] = False
        mutex.release()
        sendClient.close()
    else:
        sendClient.close()

def recvThread(c, cID, num, filename):
    log = open('log', 'w')
    while True:
        #require part
        require = nextPart(cID, num)
        log.write('require' + str(require)+'\n')
        sendmsg = {'require': require, 'state': clientState}
        c.send(json.dumps(sendmsg).encode('utf-8'))
        if require==-1:
            break
        tmp = c.recv(1024).decode('utf-8')
        log.write(tmp+'\n')
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
                log.write('start connect '+addr[0]+'\t')
                con.connect((addr[0], addr[1]))
                log.write('connect '+addr[0]+'\n')
                conList.append(con)
                con.send(str(require).encode('utf-8'))
                msg = con.recv(1024).decode('utf-8')
                log.write('receive isbusy'+msg+'\n')
                if json.loads(msg)==False:
                    freeHost.append(con)
            #choose host and receive file
            if len(freeHost)==0:
                choiceHost = random.choice(conList)
            else:
                choiceHost = random.choice(freeHost)
            #close extra
            log.write('choose finish\n\n')
            conList.remove(choiceHost)
            for con in conList:
                con.send('no'.encode('utf-8'))
            ##
            choiceHost.send('yes'.encode('utf-8'))
            recvFile(choiceHost)

        clientState[require]=1
    c.close()
    log.write('finish')
    log.close()
    combineFile(filename, num)

c = socket.socket()
host = '10.0.0.1'
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
mutex = threading.Lock()

st = threading.Thread(target=sendThread, args=(filename,cID))
rt = threading.Thread(target=recvThread, args=(c, cID, num, filename))
st.start()
rt.start()
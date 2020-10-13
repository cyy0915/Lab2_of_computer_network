import socket
import sys
import json
import struct

def sendFile(c, file, filename):
    filesize_bytes = sys.getsizeof(file)
    dirc = {
        'filename': filename,
        'filesize_bytes': filesize_bytes,
    }
    head_info = json.dumps(dirc)
    head_info_len = struct.pack('i', len(head_info))
    c.send(head_info_len)
    c.send(head_info.encode('utf-8'))
    c.sendall(file)

def recvFile(c):
    head_struct = c.recv(4)
    head_len = struct.unpack('i', head_struct)[0]
    data = c.recv(head_len)
    head_dir = json.loads(data.decode('utf-8'))
    filesize_b = head_dir['filesize_bytes']
    filename = head_dir['filename']

    recv_len = 0
    recv_mesg = b''
    f = open(filename, 'wb')
    while recv_len < filesize_b:
        if filesize_b - recv_len > 1024:

            recv_mesg = c.recv(1024)
            f.write(recv_mesg)
            recv_len += len(recv_mesg)
        else:
            recv_mesg = c.recv(filesize_b - recv_len)
            recv_len += len(recv_mesg)
            f.write(recv_mesg)
            break
    f.close()
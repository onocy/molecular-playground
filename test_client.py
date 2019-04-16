import socket
import json
import base64

HOST = '127.0.0.1' 
PORT = 65432     

with socket.socket() as s:
    s.connect((HOST, PORT))
    while(True):
        data = s.recv(1024).decode('utf-8')
        print('Received', repr(data.replace('\n', '')))

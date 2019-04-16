import socket
import json
import base64

HOST = '127.0.0.1' 
PORT = 65432     

with socket.socket() as s:
    s.connect((HOST, PORT))
    while(True):
        data = s.recv(1024).decode('utf-8')
        if len(list(data)) > 2: 
            representation = repr(data.replace('\n', ''))[1:-1]
            print('Received', representation)

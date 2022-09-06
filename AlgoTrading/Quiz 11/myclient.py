import socket
import sys


import json

HOST, PORT = "localhost", 9999
data = "logon message from Seb"

class Strategy1:
    def __init__(self):
        self.count = 0
    def handle_md(self,md):
        self.count +=1
    def update_action(self):
        if self.count % 5 == 0:
            return "BUY"


seb_strategy=Strategy1()

# Create a socket (SOCK_STREAM means a TCP socket)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    sock.connect((HOST, PORT))

    while True:
        # Receive data from the server and shut down
        received = str(sock.recv(1024), "utf-8")
        # print("Received: {}".format(received))
        deserialized_string=json.loads(received)
        print(deserialized_string['Price'],deserialized_string['Quantity'])
        seb_strategy.handle_md(deserialized_string)
        if(seb_strategy.update_action()=='BUY'):
            print("BUY")
#!/usr/bin/env python3

import socket
import threading
import csv
import json
import argparse
import sys
import time
import datetime



class ThreadedServer(object):
    def __init__(self, host,opt):
        self.environment = {}
        self.environment['NoMode'] = {'points' : 0}
        self.environment['Occupancy'] = {'occupancy' : 0, 'points' : 0}
        self.host = host
        self.port = opt.port
        self.opt = opt
        self.state = self.environment[opt.mode if opt.mode else 'NoMode']
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.lock = threading.Lock()

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(500)
            threading.Thread(target = self.listenToClient,args = (client,address)).start()
            threading.Thread(target = self.sendStreamToClient,args =
                             (client,self.sendCSVfile())).start()

    def handle_client_answer(self,obj):
        if self.opt.mode is not None and self.opt.mode=='Occupancy':
            
            if 'Occupancy' not in obj:
                return
            self.lock.acquire()
            if self.state['occupancy'] == int(obj['Occupancy']):
                self.state['points']+=1 
            self.lock.release()
        return 

    def listenToClient(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size).decode()
                if data:
                    # Set the response to echo back the recieved data
                    a=json.loads(data.rstrip('\n\r '))
                    self.handle_client_answer(a)
    
                    #client.send(response)
                else:
                    print('Client disconnected')
                    return False
            except:
                print('Client closed the connection')
                print ("Unexpected error:", sys.exc_info()[0])
                client.close()
                return False

    def handleCustomData(self,buffer):
        if self.opt.mode is not None and self.opt.mode=='Occupancy':
            self.lock.acquire()
            buffer['date']=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.state['occupancy']= int(buffer['Occupancy'])
            buffer['Occupancy']=-1
            self.lock.release()

    def sendStreamToClient(self,client,buffer):
        for i in buffer:
            print(i)
            self.handleCustomData(i)
            try:
                client.send((self.convertStringToJSON(i)+'\n').encode('utf-8'))
                time.sleep(self.opt.interval)
            except:
                print('End of stream')
                return False
        client.send((self.convertStringToJSON(self.state)+'\n').encode('utf-8'))   
        return False

    def convertStringToJSON(self,st):
        return json.dumps(st)
            
    def sendCSVfile(self):
        out=[]
        for f in self.opt.files:
            print ('reading file %s...' % f)
            csvfile = open(f, 'r')
            reader = csv.DictReader( csvfile)
            for row in reader:
                out+=[row]
        return out

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage='usage: tcp_server -p port [-f -m]')
    parser.add_argument('-f', '--files', nargs='+')
    parser.add_argument("-m", "--mode",action="store", dest="mode")
    parser.add_argument("-p", "--port",action="store", dest="port",type=int)
    parser.add_argument("-t", "--time-interval",action="store",
                        dest="interval",type=int,default=1)
    
    opt=parser.parse_args()
    if not opt.port:
        parser.error('Port not given')
    ThreadedServer('127.0.0.1',opt).listen()


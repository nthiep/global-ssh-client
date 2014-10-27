#!/usr/bin/env python
#
# Name: 	Global SSH Server
# Description:	connect to client and return public ip.
#		use TCP server.
#
# Author: 	Nguyen Thanh Hiep
# Time: 	2014/09 IUH
# Required for client: 	paramiko, pymongo, ecdsa
#
import socket
import struct
import sys
from threading import Thread
from sv_handle import Handle
class Main_handle(Thread):
    """docstring for Main_handle"""
    def __init__(self, port):
        super(Main_handle, self).__init__()
        self.daemon = True
        self.cancelled = False
        self.port = port
        
    def run(self):
        s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        try:            
            s.bind(("", 5000))
        except:
            print "error: Main_handle rebind port 8080"
            s.bind(("", self.port))
        print "----Global SSH Server----"
        print "TCP Listening on port %d" % self.port
        print ".........................."                   
        while True:
            s.listen(5)
            connection, client_address = s.accept()
            newhandle = Handle(client_address, connection)
            newhandle.start()
        s.close()
        sys.exit(1)

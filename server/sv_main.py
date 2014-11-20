#!/usr/bin/env python
#
# Name:     Global SSH socket server
# Description:  help connect ssh between client via return public ip and ramdom port.
#               use socket.
# project 2
# Server:   cloud koding
#
# Author:   Nguyen Thanh Hiep - Nguyen Huu Dinh
# Time:     2014/11
# Requirements:  view requirements.txt
#
import socket, json
import struct
import sys
from threading import Thread
from sv_handle import Handle
from sv_peer import Peer
from sv_lspeer import lsPeer, lspeer, session
from ConfigParser import SafeConfigParser
peer = Peer()
def main():
    parser = SafeConfigParser()
    parser.read('sv_config.conf')
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    port = int(parser.get('server', 'port'))
    s.bind(("", port))
    print "----Global SSH Server----"
    print "TCP Listening on port %d" % port
    print ".........................."
    s.listen(5)      
    while True:
        connection, client_address = s.accept()
        data = connection.recv(1024)
        q = process(connection, client_address, data)
        if q:
            newhandle = Handle(json.loads(data)["token"], json.loads(data)["mac"], client_address, connection)
            newhandle.start()
    s.close()
    sys.exit(1)

def listpeer(token):
    ls = peer.lspeer(token)
    res = []
    for l in ls:
        res.append({'host': l["host"], 'mac' : l["mac"]})
    for p in lspeer:
        if p.token == token:
            p.connection.send(json.dumps(res))
def checkhandle(token, mac):
    for p in lspeer:
        if p.token == token and p.mac == mac:
            return True
    return False
def addhandle(token, mac, connection):
    if not checkhandle(token, mac):
        ls = lsPeer(token, mac, connection)
        lspeer.append(ls)
        return True
    return False
def addprocess(connection, data, nat):
    if addhandle(data["token"], data["mac"], connection):
        peer.online(data["token"], data["mac"], data["host"], nat)
        listpeer(data["token"])
        return True            
    connection.send(json.dumps({"status": "error"}))
    return False
def nattype(token, mac):
    p = peer.info(token, mac)
    if p:
        return p["nat"]
    return False
def process(connection, client_address, data):
    data = json.loads(data)
    req = data["request"]
    print client_address
    addr, port = client_address
    if req == "login":
        if data["lport"] == port:
            return addprocess(connection, data, "None")
        elif checkhandle(data["token"], data["mac"]):
            connection.send(json.dumps({"status": "error"}))
            return False
        peer.login(data["token"], data["mac"], data["lport"], port)
        connection.send(json.dumps({"status": "check"}))
        return False
    if req == "checknat":
        lg = peer.checklogin(data["token"], data["mac"])
        if lg:
            if port > lg["port"]:
                return addprocess(connection, data, "ASC")
            else:
                return addprocess(connection, data, "DESC")
        connection.send(json.dumps({"status": "error"}))
        return False
    if req == "connect":
        print data
        se = peer.checksession(data["session"])
        nat = nattype(data["token"], data["mymac"])
        if not nat:
            print "not nat"
            return False
        if data["session"] in session and se:
                print "linked request session: %s" % data["session"]
                session[data["session"]].send(json.dumps({"user": data["user"], "lport" : data["lport"],
                 "laddr": data["laddr"], "port": port, "addr": addr, "me": se["addr"],"nat": nat}))
                connection.send(json.dumps({"lport" : se["lport"], "laddr": se["laddr"], "port": se["port"],
                "addr": se["addr"], "me" :addr, "nat": se["nat"]}))
                session[data["session"]].close()
                connection.close()
                del session[data["session"]]
                return False
        else:                
            if peer.checkonline(data["token"], data["mac"]):
                session[data["session"]] = connection
                peer.session(data["session"], data["lport"], data["laddr"], port, addr, nat)
                for pe in lspeer:
                    if pe.token == data["token"] and pe.mac == data["mac"]:
                        pe.connection.send(json.dumps({"status": "bind", "session": data["session"]}))                
                log = "connect to " + data["mac"]
                peer.addlog(data["token"], data["mymac"], log)
            return False
    if req == "upkey":
        if peer.checkonline(data["token"], data["mac"]):
            for pe in lspeer:
                if pe.token == data["token"] and pe.mac == data["mac"]:
                    log = "add key to " + data["mac"]
                    peer.addlog(data["token"], data["mymac"], log)
                    pe.connection.send(json.dumps({"status": "addkey", "key": data["key"]}))
        connection.close()
        return False
    if req == "logs":
        lg = peer.logs(data["token"])
        res = []
        for l in lg:
            res.append({'time': l['time'], 'mac': l['mac'], 'log' : l['log']})
        connection.send(json.dumps(res))
        connection.close()
        return False
if __name__ == "__main__":
    main()
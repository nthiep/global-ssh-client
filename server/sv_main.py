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
import sys, socket, json, random, hashlib, struct
from threading import Thread
from sv_handle import Handle
from sv_peer import Peer
from sv_lspeer import lsPeer, lspeer, session
from ConfigParser import SafeConfigParser
peer = Peer()
class Udp_main(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        parser = SafeConfigParser()
        parser.read('sv_config.conf')
        port = int(parser.get('server', 'port'))
        usk = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        usk.bind( ("", port) )
        print "UDP listening on port %d" % port
        print ".........................." 
        while True:
            data, addr = usk.recvfrom(1024)
            print "connection from udp  %s:%d" % addr 
            try:
                data = json.loads(data)
                session = data["session"]
                host, port = addr
                check = peer.check_udp_session(session)
                if not check:
                    peer.udp_session(session, host, port)
                else:
                    usk.sendto(json.dumps({"host": host, "port": port}), (check["addr"], int(check["port"])))
                    usk.sendto(json.dumps({"host": check["addr"], "port": check["port"]}), addr)
                    print "linked session %s" % session
            except:
                pass
def main():    
    print "----Global SSH Server----"
    parser = SafeConfigParser()
    parser.read('sv_config.conf')
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    port = int(parser.get('server', 'port'))
    s.bind(("", port))
    udp_thread = Udp_main()
    #udp_thread.deamon = True
    udp_thread.start()
    print "TCP Listening on port %d" % port
    print ".........................."
    s.listen(5)      
    while True:
        connection, client_address = s.accept()
        data = connection.recv(1024)
        q = process(connection, client_address, data)
        if q:
            newhandle = Handle(json.loads(data)["mac"], connection)
            newhandle.start()
    s.close()
    sys.exit(1)
def listpeer(user):
    ls = peer.lspeer(user)
    res = []
    for l in ls:
        res.append({'host': l["host"], 'mac' : l["mac"]})
    for p in lspeer:
        if p.user == user:
            p.connection.send(json.dumps(res))
def checkhandle(mac):
    for p in lspeer:
        if p.mac == mac:
            return True
    return False
def addhandle(data, connection):
    if checkhandle(data["mac"]):
        connection.send(json.dumps({"error": "login"}))
        return False
    elif peer.check_token(data["mac"], data["token"]):
        user = username(data["token"], data["mac"])
        ls = lsPeer(user, data["mac"], connection)
        lspeer.append(ls)
        peer.online(user, data["mac"], data["host"])
        listpeer(user)
        return True
    connection.send(json.dumps({"error": "token"}))
    return False
def username(token, mac):
    p = peer.check_token(mac, token)
    if p:
        return p["user"]
    return False
def nattype(mac):
    p = peer.info(mac)
    if p:
        return p["nat"]
    return False
def process(connection, client_address, data):
    try:
        data = json.loads(data)
    except:
        return False
    req = data["request"]
    print client_address
    addr, port = client_address
    if req == "login":
        if addhandle(data, connection):
            if data["lport"] == port:
                peer.addnat(data["mac"], "None")
            peer.login(data["mac"], data["lport"], port)
            return True
        return False
    if req == "checknat":
        lg = peer.checklogin(data["mac"])
        if lg:
            if port != int(data["lport"]):
                peer.addnat(data["mac"], "RAD")
            else:
                return False
            if port > int(lg["port"]) and (port - int(lg["port"])) < 10:
                peer.addnat(data["mac"], "ASC")
            elif port < int(lg["port"]) and (int(lg["port"]) - port) < 10 :
                peer.addnat(data["mac"], "DESC")
            peer.login(data["mac"], data["lport"], port)
        return False
    if req == "connect":
        print data
        nat = nattype(data["mymac"])
        if "session" in data:
            se = peer.checksession(data["session"])
            if data["session"] in session and se:
                print "linked request session: %s" % data["session"]
                session[data["session"]].send(json.dumps({"session": data["session"], "user": data["user"], "lport" : data["lport"],
                 "laddr": data["laddr"], "port": port, "addr": addr, "me": se["addr"],"nat": nat, "mynat": se["nat"]}))
                connection.send(json.dumps({"lport" : se["lport"], "laddr": se["laddr"], "port": se["port"],
                "addr": se["addr"], "me" :addr, "nat": se["nat"], "mynat": nat}))
                session[data["session"]].close()
                connection.close()
                del session[data["session"]]
            return False
        else:
            if peer.checkconnect(data["mymac"], data["mac"]):
                r = random.getrandbits(128)
                ss = hashlib.sha1(str(r)).hexdigest()
                session[ss] = connection
                peer.session(ss, data["lport"], data["laddr"], port, addr, nat)
                for pe in lspeer:
                    if pe.mac == data["mac"]:
                        pe.connection.send(json.dumps({"status": "bind", "session": ss}))                
                log = "connect to " + data["mac"]
                peer.addlog(data["mymac"], log)
            return False
    if req == "upkey":
        if peer.checkconnect(data["mymac"], data["mac"]):
            for pe in lspeer:
                if pe.mac == data["mac"]:
                    log = "add key to " + data["mac"]
                    peer.addlog(data["mymac"], log)
                    pe.connection.send(json.dumps({"status": "addkey", "key": data["key"] , "username": data["username"], "password" : data["password"]}))
        connection.close()
        return False
if __name__ == "__main__":
    try:
        act = sys.argv[1]
        if act == "del":
            peer.rm_all()
    except (IndexError, ValueError):
        pass
    main()
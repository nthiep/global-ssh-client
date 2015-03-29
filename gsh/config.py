#!/usr/bin/env python
#
# Name:			Configuration file
# Description:	Configuration file
#

import os, uuid, platform
from ConfigParser import ConfigParser
# change config file if you move to another place 
CONFIG_FILE = "/etc/gsh/gsh.conf"

# Configuration variable
parser = ConfigParser()
parser.read(CONFIG_FILE)
# get mac address
_node = "%12X" %uuid.getnode()
_node = _node.replace(" ", "0")
_mac = ':'.join([''.join(i) for i in map(None, *(_node[::2], _node[1::2]))])

info		= platform.linux_distribution()
PLATFORM 	= " ".join(info)
MAC_ADDR 	= _mac
GSH_DIR 	= parser.get('config', 'gsh_dir')
KEY_FILE 	= os.path.join(GSH_DIR, "gsh.key")
NET_DIR		= os.path.join(GSH_DIR, "net/")

# connect server
SERVER 		= "172.16.8.1"
PORT	 	= 8080

# ssh server config
SSH_SERVER	= parser.get('config', 'ssh_server')
SSH_PORT	= int(parser.get('config', 'ssh_port'))
#!/usr/bin/env python
#
# Name:			Configuration module
# Description:	Configuration module file
#

import os, uuid, platform, logging
from ConfigParser import ConfigParser

# change config file if you move to another place 
CONFIG_FILE = "/etc/gsh/gsh.conf"
LOG_FILENAME= "/var/log/gshs.log"
parser = ConfigParser()
parser.read(CONFIG_FILE)
# enable or disable debug model
DEBUG 	= False
dg 		= parser.get('config', 'debug')
if dg.lower() == 'true':
	DEBUG = True

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
# check if not debug mode
if not DEBUG:
	logging.disable(level=logging.DEBUG)

# Configuration variable
# get mac address
_node 		= "%12X" %uuid.getnode()
_node 		= _node.replace(" ", "0")
_mac 		= ':'.join([''.join(i) for i in map(None, *(_node[::2], _node[1::2]))])

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
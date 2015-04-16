#!/usr/bin/env python
#
# Name:			Configuration module
# Description:	Configuration module file
#

import os, uuid, platform, logging
from ConfigParser import ConfigParser

windows = True if platform.system() == "Windows" else False
# change config file if you move to another place
root 		= os.path.abspath(os.sep)
if windows:
	GSH_DIR 	= os.path.join(root, "gsh")
	CONFIG_FILE = os.path.join(root, "gsh", "gsh.conf")
	LOG_FILENAME= os.path.join(root, "gsh", "gsh.log")
	PLATFORM 	= platform.system() + platform.release()
else:
	GSH_DIR 	= os.path.join(root, "etc", "gsh")
	CONFIG_FILE = os.path.join(root, "etc", "gsh", "gsh.conf")
	LOG_FILENAME= os.path.join(root, "var", "log", "gsh.log")
	info		= platform.linux_distribution()
	PLATFORM 	= " ".join(info)
parser = ConfigParser()
if not os.path.exists(CONFIG_FILE):
	parser.add_section('config')
	parser.set('config','ssh_server', '127.0.0.1')
	parser.set('config','ssh_port', 22)
	parser.set('config','debug', True)
	f = open(CONFIG_FILE, "w")
	parser.write(f)
	f.close()
parser.read(CONFIG_FILE)
# enable or disable debug model
DEBUG 	= False
dg 		= parser.get('config', 'debug')
if dg.lower() == 'true':
	DEBUG = True

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
# check if not debug mode
logger = logging.getLogger()
if not DEBUG:
	logger.disabled = True
# Configuration variable
# get mac address
_node 		= "%12X" %uuid.getnode()
_node 		= _node.replace(" ", "0")
_mac 		= ':'.join([''.join(i) for i in map(None, *(_node[::2], _node[1::2]))])

MAC_ADDR 	= _mac
NET_DIR		= os.path.join(GSH_DIR, "net")
KEY_FILE 	= os.path.join(GSH_DIR, "gsh.key")

# connect server
SERVER 		= "gssh.koding.io"
PORT	 	= 8080

# ssh server config
SSH_SERVER	= parser.get('config', 'ssh_server')
SSH_PORT	= int(parser.get('config', 'ssh_port'))
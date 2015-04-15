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
	CONFIG_FILE = os.path.join(root, "gsh", "gsh.conf")
	LOG_FILENAME= os.path.join(root, "log", "gshs.log")
	PLATFORM 	= platform.system() + platform.release()
else:
	CONFIG_FILE = os.path.join(root, "etc", "gsh", "gsh.conf")
	LOG_FILENAME= os.path.join(root, "var", "log", "gshs.log")
	info		= platform.linux_distribution()
	PLATFORM 	= " ".join(info)
parser = ConfigParser()
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
GSH_DIR 	= parser.get('config', 'gsh_dir')
NET_DIR		= os.path.join(GSH_DIR, "net")
KEY_FILE 	= os.path.join(GSH_DIR, "gsh.key")

# connect server
SERVER 		= "gssh.koding.io"
PORT	 	= 8080

# ssh server config
SSH_SERVER	= parser.get('config', 'ssh_server')
SSH_PORT	= int(parser.get('config', 'ssh_port'))
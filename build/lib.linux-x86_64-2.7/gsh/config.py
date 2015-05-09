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

PRIVATE = False
pv 		= parser.get('config', 'private')
if pv.lower() == 'true':
	PRIVATE = True
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
WORK_DIR		= os.path.join(GSH_DIR, "workgroup/")
KEY_FILE 	= os.path.join(GSH_DIR, "gsh.key")

# author server
DOMAIN 			= parser.get('access', 'domain')
CLIENT_ID 		= parser.get('access', 'client_id')
CLIENT_SECRET 	= parser.get('access', 'client_secret')

ACCESS_TOKEN 	= parser.get('access', 'access_token')
TOKEN_TYPE 		= parser.get('access', 'token_type')
try:
	EXPIRES_IN 	= float(parser.get('access', 'expires_in'))
except:
	EXPIRES_IN  = False
REFESH_TOKEN	= parser.get('access', 'refresh_token')

WORKGROUP_ID 	= parser.get('access', 'workgroup_id')
WORKGROUP_SECRET= parser.get('access', 'workgroup_secret')

def save_client(domain, client_id, client_secret):
	cfgfile = open(CONFIG_FILE, 'w')
	parser.set('access','domain', domain)
	parser.set('access','client_id', client_id)
	parser.set('access','client_secret', client_secret)
	parser.set('access','workgroup_id', '')
	parser.set('access','workgroup_secret', '')
	parser.write(cfgfile)
	cfgfile.close()
	global CLIENT_ID
	CLIENT_ID = client_id
	global CLIENT_SECRET
	CLIENT_SECRET = client_secret
def save_token(access_token, token_type, expires_in, refresh_token):
	cfgfile = open(CONFIG_FILE, 'w')
	parser.set('access','access_token', access_token)
	parser.set('access','token_type', token_type)
	parser.set('access','expires_in', expires_in)
	parser.set('access','refresh_token', refresh_token)
	parser.set('access','workgroup_id', '')
	parser.set('access','workgroup_secret', '')
	parser.write(cfgfile)
	cfgfile.close()
	global ACCESS_TOKEN
	ACCESS_TOKEN = access_token
	global TOKEN_TYPE
	TOKEN_TYPE = token_type
	global EXPIRES_IN
	EXPIRES_IN = expires_in
	global REFESH_TOKEN
	REFESH_TOKEN = refresh_token

def save_workgroup(workgroup_id, workgroup_secret):
	cfgfile = open(CONFIG_FILE, 'w')
	parser.set('access','workgroup_id', workgroup_id)
	parser.set('access','workgroup_secret', workgroup_secret)
	parser.set('access','client_id', '')
	parser.set('access','client_secret', '')
	parser.set('access','access_token', '')
	parser.set('access','token_type', '')
	parser.set('access','expires_in', '')
	parser.set('access','refresh_token', '')
	parser.write(cfgfile)
	cfgfile.close()
	global WORKGROUP_ID
	WORKGROUP_ID = workgroup_id
	global WORKGROUP_SECRET
	WORKGROUP_SECRET = workgroup_secret


# socket server config
SERVER 		= "gssh.koding.io"
PORT	 	= 8080
# web service config
WS_SERVER 	= "gssh.koding.io"
WS_PORT 	= 8000
# ssh server config
SSH_SERVER	= parser.get('config', 'ssh_server')
SSH_PORT	= int(parser.get('config', 'ssh_port'))
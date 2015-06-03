#!/usr/bin/env python
#
# Name:			Configuration module
# Description:	Configuration module file
#

import os, uuid, platform, logging
from ConfigParser import ConfigParser

windows = True if platform.system().lower() == "windows" else False
# change config file if you move to another place
root 		= os.path.abspath(os.sep)
if windows:
	GOSH_DIR 	= os.path.join(root, "gosh")
	CONFIG_FILE = os.path.join(root, "gosh", "gosh.conf")
	LOG_FILENAME= os.path.join(root, "gosh", "gosh.log")
	PLATFORM 	= platform.system() + platform.release()
else:
	GOSH_DIR 	= os.path.join(root, "etc", "gosh")
	CONFIG_FILE = os.path.join(root, "etc", "gosh", "gosh.conf")
	LOG_FILENAME= os.path.join(root, "var", "log", "gosh.log")
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
WORK_DIR	= os.path.join(GOSH_DIR, "workgroup/")
KEY_FILE 	= os.path.join(GOSH_DIR, "gosh.key")
# machine id
ID_MACHINE		= parser.get('access', 'id_machine')
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

def save_machine(id_machine):
	cfgfile = open(CONFIG_FILE, 'w')
	parser.set('access','id_machine', id_machine)
	parser.write(cfgfile)
	cfgfile.close()
def save_client(domain, client_id, client_secret):
	cfgfile = open(CONFIG_FILE, 'w')
	parser.set('access','domain', domain)
	parser.set('access','client_id', client_id)
	parser.set('access','client_secret', client_secret)
	parser.set('access','workgroup_id', '')
	parser.set('access','workgroup_secret', '')
	parser.write(cfgfile)
	cfgfile.close()
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

# socket server config
SERVER 		= "128.199.211.29"
PORT	 	= 8080
# web service config
WS_SERVER 	= "128.199.211.29"

# stun server config
STUN_SERVER = "128.199.211.29"
STUN_PORT 	= 3478
# ssh server config
SSH_SERVER	= parser.get('config', 'ssh_server')
SSH_PORT	= int(parser.get('config', 'ssh_port'))

# localhost address
LOCALHOST	= parser.get('config', 'localhost')
# accept machine
mac_access	= parser.get('access', 'mac_access')
if mac_access.lower() == 'true':
	MAC_ACCESS = 'true'
elif mac_access.lower() == 'false':
	MAC_ACCESS = 'false'
else:
	MAC_ACCESS = 'none'

try:
	MAC_LIST = parser.get("access","mac_list").lower().split(';')
except:
	MAC_LIST = []
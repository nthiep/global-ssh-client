#!/usr/bin/env python
import os, sys, platform
try:
      from setuptools import setup
except:
      from distutils.core import setup
# Version info -- read without importing
_locals = {}
with open(os.path.join("gosh", "_version.py")) as fp:
    exec(fp.read(), None, _locals)
version = _locals['__version__']

windows = True if platform.system().lower() == "windows" else False
# setup init file
init     = []
datafile = []
requires = []
if os.system('ssh -V') or windows:
      requires = ["paramiko"]
if not windows:
      scripts = ['bin/gosh', 'bin/goshd']
      init = ['etc/init.d/other/gosh']
      if platform.linux_distribution()[0].lower() in ['ubuntu', 'debian']:
            init = ['etc/init.d/gosh']
      config = ("","")
      if not os.path.isfile("/etc/gosh/gosh.conf"):
            config = ('/etc/gosh', ['etc/gosh/gosh.conf'])
      datafile = [('/etc/init.d', init), config]
setup(name        ='gosh',
      version     =version,
      description ='Global SSH',
      long_description=open('README.md').read(),
      author      ='nthiep',
      author_email='hieptux@gmail.com',
      url         ='https://github.com/nthiep/global-ssh',  
      packages    =['gosh'],
      install_requires    = requires,
      license     ='GNU',
      platforms   = 'Posix; Windows',
      scripts     = scripts,
      data_files  = datafile 
     )
if sys.argv[1] == 'install':
      if windows:
            pass
      else:
            print "chmod for gosh deamon..."
            os.system("chmod +x /etc/init.d/gosh")
            print "chmod success.----ok"
            print "chmod for gosh.conf ..."
            os.system("chmod 766 /etc/gosh/gosh.conf")
            print "chmod success.----ok"
            print "create run level rc.d ..."
            for x in range(2,5):
                  if not os.path.isfile("/etc/rc%d.d/S99gosh" %x):
                        os.system("ln -s /etc/init.d/gosh /etc/rc%d.d/S99gosh" %x)
            for x in [0,1,6]:
                  if not os.path.isfile("/etc/rc%d.d/K20gosh" %x):
                       os.system("ln -s /etc/init.d/gosh /etc/rc%d.d/K20gosh" %x)
            print "create success.----ok"
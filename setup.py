#!/usr/bin/env python
import os, sys, platform
from setuptools import setup
# Version info -- read without importing
_locals = {}
with open('gsh/_version.py') as fp:
    exec(fp.read(), None, _locals)
version = _locals['__version__']
# setup init file
init = ['etc/init.d/gshd']
if platform.linux_distribution()[0].lower() == 'centos':
      init = ['etc/init.d/gshd-centos']
with open('requirements.txt') as f:
    required = f.read().splitlines()
setup(name        ='gsh',
      version     =version,
      description ='global ssh',
      long_description=open('README.md').read(),
      author      ='hiep',
      author_email='hieptux@gmail.com',
      url         ='https://github.com/nthiep/global-ssh',  
      packages    =['gsh'],
      install_requires    = required,
      license     ='GNU',
      platforms   = 'Posix; Windows',
      scripts     =['bin/gsh', 'bin/gshd'],
      data_files  =[('/etc/init.d', init),
                  ('/etc/gsh', ['etc/gsh/gsh.conf'])]
     )
if sys.argv[1] == 'install':
      if platform.linux_distribution()[0].lower() == 'centos':
            os.system('mv /etc/init.d/gshd-centos /etc/init.d/gshd')
      print "chmod for gsh ..."
      os.system("chmod +x /etc/init.d/gshd")
      print "chmod success.----ok"
      print "chmod for gsh.conf ..."
      os.system("chmod +r /etc/gsh/gsh.conf")
      print "chmod success.----ok"
"""
      print "create run level rc.d ..."
      for x in range(2,5):
            os.system("ln -s /etc/init.d/gshd /etc/rc%d.d/S99gshd" %x)
      for x in [0,1,6]:
            os.system("ln -s /etc/init.d/gshd /etc/rc%d.d/K20gshd" %x)
      print "create success.----ok"
"""
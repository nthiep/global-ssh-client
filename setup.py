#!/usr/bin/env python
import os, sys
from distutils.core import setup

setup(name        ='gsh',
      version     ='1.0.1',
      description ='global ssh',
      long_description=open('README.md').read(),
      author      ='hiep',
      author_email='hieptux@gmail.com',
      url         ='https://github.com/nthiep/global-ssh',      
      packages    =['gsh'],
      license     = 'GNU',
      scripts     =['bin/gsh', 'bin/gshd'],
      data_files  =[('/etc/init.d', ['etc/init.d/gshd']),
                  ('/etc/gsh', ['etc/gsh/gsh.conf'])]
     )
if sys.argv[1] == 'install':
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
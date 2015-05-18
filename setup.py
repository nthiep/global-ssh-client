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

windows = True if platform.system() == "Windows" else False
# setup init file
init     = []
datafile = []
if not windows:
      scripts = ['bin/gosh', 'bin/goshd']
      init = ['etc/init.d/goshd']
      if platform.linux_distribution()[0].lower() == 'centos':
            init = ['etc/init.d/goshd-centos']
      datafile = [('/etc/init.d', init), ('/etc/gosh', ['etc/gosh/gosh.conf'])]
setup(name        ='gosh',
      version     =version,
      description ='Global SSH',
      long_description=open('README.md').read(),
      author      ='nthiep',
      author_email='hieptux@gmail.com',
      url         ='https://github.com/nthiep/global-ssh',  
      packages    =['gosh'],
      install_requires    = [],
      license     ='GNU',
      platforms   = 'Posix; Windows',
      scripts     = scripts,
      data_files  = datafile 
     )
if sys.argv[1] == 'install':
      if windows:
            pass
      else:
            if platform.linux_distribution()[0].lower() == 'centos':
                  os.system('mv /etc/init.d/goshd-centos /etc/init.d/goshd')
            print "chmod for gosh ..."
            os.system("chmod +x /etc/init.d/goshd")
            print "chmod success.----ok"
            print "chmod for gosh.conf ..."
            os.system("chmod 766 /etc/gosh/gosh.conf")
            print "chmod success.----ok"
            print "create run level rc.d ..."
            for x in range(2,5):
                  os.system("ln -s /etc/init.d/goshd /etc/rc%d.d/S99goshd" %x)
            for x in [0,1,6]:
                  os.system("ln -s /etc/init.d/goshd /etc/rc%d.d/K20goshd" %x)
            print "create success.----ok"
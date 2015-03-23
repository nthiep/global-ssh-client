#!/usr/bin/env python
import os
from distutils.core import setup

setup(name='gsh',
      version='1.0.0',
      description='global ssh',
      long_description=open('README.md').read(),
      author='hiep',
      author_email='hieptux@gmail.com',
      url='https://www.python.org/',      
      packages=['gsh'],
      scripts=['bin/gsh', 'bin/gssh'],
      data_files=[('/etc/init.d', ['bin/gshd']),
                  ('/etc/gsh', ['gsh/gsh.conf'])]
     )
print "chmod for gsh..."
os.system("chmod +x /etc/init.d/gshd")
print "chmod ok."

Global-SSH
==========

Description: Global-SSH webservice, application help connect SSH to computer via p2p network, use hole punching create TCP connect and use for SSH

How use Global-SSH:
-------
connect to machine:
<!-- highlight:-d language:console -->
	$gosh [user@]hostname
	hostname can use MAC address
option:
<!-- highlight:-d language:console -->
	Usage: gosh [options] [user@][hostname]

	Global SSH help connect SSH behind NAT

	Options:
		--version             show program's version number and exit
		-h, --help            show this help message and exit

	Network:
		-j, --join          Join a Domain
		-r, --register      Create new Domain
		-g *, --group=*     Join a Workgroup
		-c *, --create=*    [workgroup] create a Workgroup
		-d *, --delete=*    [workgroup] delete Workgroup
		-l, --logout        logout Domain or Workgroup

	Connect:
		-D *, --bind=*      -D [bindport:]destport
		-L *, --tunnel=*    -L port:host:port
		-p *, --port=*      [user@]hostname -p port
		-i *, --identity=*  [user@]hostname -i identity_file
		-v, --verbose       [user@]hostname -v debugging mode

	Infomation:
		-I, --info          show infomation of machine
		-m *, --mac=*       -I -m hostname
		-n, --nat           check nat type

How install:
-------
install gosh from pypi:
<!-- highlight:-d language:console -->
	$ sudo pip install gosh

Clone the repo global-sh:
<!-- highlight:-d language:console -->
	$ git clone https://github.com/nthiep/global-ssh.git
download zip/tar.gz file then extract file.

run setup tool:
<!-- highlight:-d language:console -->
	$ sudo python setup.py install

check service is running:
<!-- highlight:-d language:console -->
	$ sudo service goshd status

About project
-------
This project will build a application tool to connect linux computer behind NAT use hole punching and multi hole punching for symmetric NAT.
Our team: Nguyen Thanh Hiep and Nguyen Huu Dinh

####View details at: https://gssh.github.io
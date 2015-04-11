Global-SSH
==========

Description: Global-SSH webservice, application help connect SSH to computer via p2p network, use hole punching create TCP connect and use for SSH

How use Global-SSH:
-------
<!-- language:console -->
-- connect to machine
-- $gsh [user@]hostname

-- show machines:
$ gsh [-l]

-- connect to other service
$ gsh hostname --port {port}
-- this will return local port
-- to connect use:
$ {service} [option] -p {port}


How to install:
-------
<!-- language:console -->
-- use git to clone gsh
$ git clone https://github.com/nthiep/global-ssh.git
-- or download zip/tar.gz file
-- extract file

-- run setup tool
$ sudo python setup.py install

-- check service is running
$ sudo service gshd status

About project
-------
This project will build a application tool to connect linux computer behind NAT use hole punching and multi hole punching for symmetric NAT.
Our team: Nguyen Thanh Hiep and Nguyen Huu Dinh

View details at: https://gssh.github.io
-------
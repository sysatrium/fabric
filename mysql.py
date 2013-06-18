#!/usr/bin/python
import os
import glob
import sys
import time

from fabric.api import *
from fabric.contrib import *
from fabric.colors import *
import jinja2
import MySQLdb

sys.path.append(os.getcwd() + "/lib")

from daemonMysql import Mysql

@task
def help():
	print (green("""
	# Description
	This cook will be cook the MySQL.
	He can do install, update, remove, start, stop, restart, configure of 
	a single server and set replication master-slave, master-master.
	
	

		# Default settings is character=utf8, skip_networking=0, version=5.1
	"""+blue("""
		# Install a single server with the default settings
		fab -f mysql.py single -H lab1rhce -u root -pteligent
		
		# Install a single server with specified settings: 
		#	character=latin1,version=5.1,skip_networking=1
		fab -f mysql.py single:character=latin1,version=5.1,skip_networking=1 -H lab1rhce -u root -pteligent
		
		# Install master-slave with the default settings
		fab -f mysql.py single -P -H lab1rhce,lab2rhce -u root -pteligent
		fab -f mysql.py master_slave:slave=lab2rhce,master=lab1rhce

		# Install master-slave with specified settings: 
		#	character=latin1
		fab -f mysql.py single:character=latin1 -P -H lab1rhce,lab2rhce -u root -pteligent
		fab -f mysql.py master_slave:slave=lab2rhce,master=lab1rhce
		
		# Install master-master with the default settings
		fab -f mysql.py single -P -H lab1rhce,lab2rhce -u root -pteligent
		fab -f mysql.py master_master:lab1rhce,lab2rhce

		# Install master-master with specified settings:
		#	character=latin1
		fab -f mysql.py single:character=latin1 -P -H lab1rhce,lab2rhce -u root -pteligent
		fab -f mysql.py master_master:lab1rhce,lab2rhce

		# Manual start MySQL
		fab -f mysql.py init:start -P -H lab1,lab2 -u root -p password
			
		# Manual stop MySQL
		fab -f mysql.py init:stop  -P -H lab1,lab2 -u root -p password
			
		# Manual restart MySQL
		fab -f mysql.py init:restart -P -H lab1,lab2 -u root -p password
			
		# Manual remove MySQL
		fab -f mysql.py init:remove -P -H lab1,lab2 -u root -p password

		# Manual update MySQL
		fab -f mysql.py init:update -P -H lab1,lab2 -u root -p password
			
		# Manual install MySQL
		fab -f mysql.py init:install -P -H lab1,lab2 -u root -p password
	""")))

@task
def single(character="utf8",skip_networking="0",version="5.1"):
	mysql=Mysql(name="mysqld", config="/etc")
	mysql.yum("mysql mysql-server", "install")
	mysql.single(character=character,skip_networking=skip_networking,version=version)
	mysql.chkconfig("on")
	mysql.init("start")
	mysql.postinstall()

@task
def master_slave(master,slave):
	mysql=Mysql(name="mysqld", config="/etc", type=None)
	mysql.get_master_info(master)
	mysql.set_replication(slave)

@task
def master_master(master,slave):
	mysql=Mysql(name="mysqld", config="/etc", type=None)
	mysql.get_master_info(master)
	if mysql.set_replication(slave) == 0:
		mysql.get_master_info(slave)
		mysql.set_replication(master)

@task
def init(action):
	mysql=Mysql(name="mysqld", config="/etc")
	
	if action == "start" or action == "restart" or action == "stop":
		mysql.init(action)
	
	if action == "remove" or action == "install" or action == "update":
		mysql.yum("mysql mysql-server",action)

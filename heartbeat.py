#!/usr/bin/python

import sys
import os

import jinja2
from fabric.api import *
from fabric.contrib import *
from fabric.colors import *

sys.path.append(os.getcwd() + "/lib")

from daemonHeartbeat import Heartbeat

@task
def help():
	print(green("""
		This cook will be cook Heartbeat. He can setup VIP, double VIP, or external VIP.

		"""+blue("""Usage:
			# Get list of methods
			fab -f heartbeat.py -l

			# set 'VIP'
			fab -f heartbeat.py set_1VIP -H lab1,lab2 -u root -p password

			# set 'double VIP'
			fab -f heartbeat.py set_2VIP -H lab1,lab2 -u root -p password

			# set 'internal VIP and external VIP'
			fab -f heartbeat.py set_extVIP -H lab1,lab2 -u root -p password
			
			# Manual start Heartbeat
			fab -f heartbeat.py init:start -P -H lab1,lab2 -u root -p password
			
			# Manual stop Heartbeat
			fab -f heartbeat.py init:stop  -P -H lab1,lab2 -u root -p password
			
			# Manual restart Heartbeat
			fab -f heartbeat.py init:restart -P -H lab1,lab2 -u root -p password
			
			# Manual remove Heartbeat
			fab -f heartbeat.py init:remove -P -H lab1,lab2 -u root -p password

			# Manual update Heartbeat
			fab -f heartbeat.py init:update -P -H lab1,lab2 -u root -p password
			
			# Manual install Heartbeat
			fab -f heartbeat.py init:install -P -H lab1,lab2 -u root -p password	
		""")))

@task
def set_1VIP():
	heartbeat=Heartbeat(name="heartbeat", config="/etc/ha.d")
	heartbeat.yum("heartbeat","install")

	heartbeat.singleVIP()
	heartbeat.chkconfig("on")
	if console.confirm("Do you want to start the "+heartbeat.name+"?", default=False):
		heartbeat.init("start")

@task
def set_2VIP():
	heartbeat=Heartbeat(name="heartbeat", config="/etc/ha.d")
	heartbeat.yum("heartbeat","install")

	heartbeat.doubleVIP()
	heartbeat.chkconfig("on")
	if console.confirm("Do you want to start the "+heartbeat.name+"?", default=False):
		heartbeat.init("start")

@task
def set_extVIP():
	heartbeat=Heartbeat(name="heartbeat", config="/etc/ha.d")
	heartbeat.yum("heartbeat","install")

	heartbeat.externalVIP()
	heartbeat.chkconfig("on")
	if console.confirm("Do you want to start the "+heartbeat.name+"?", default=False):
		heartbeat.init("start")

@task
def init(action):
	heartbeat=Heartbeat(name="heartbeat", config="/etc/ha.d")
	
	if action == "start" or action == "restart" or action == "stop":
		heartbeat.init(action)
	
	if action == "remove" or action == "install" or action == "update":
		heartbeat.yum("heartbeat",action)

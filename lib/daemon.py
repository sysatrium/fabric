import os
import sys

import jinja2
from fabric.api import *
from fabric.contrib import *
from fabric.colors import *

class Daemon:
	
	
	init_path="/etc/init.d"
	root_templates="templates"
 
	def __init__(self,name=None,config=None,type="remote"):
		self.name=name
		self.type=type
		status=0
		
		# Skip set of path_install and path_templates
		# If you need not run some commands on the hosts over fabric
		if type is None:
			return None

		if name is None:
			print(red("The name of daemon is None"))
			sys.exit()

		if self.type == "remote":
			if run('test -x '+self.init_path+'/'+name+'', timeout=240, quiet=True).return_code == 1:
				status=1
		else:
			if not os.path.exists(self.init_path+'/'+name):
				status=1

		if status == 1:
			print(red("The daemon '"+self.name+"' on the host '"+env.host_string+"' didn't installed"))

		# Init the path of the templates
		self.path_templates(name)

		# Init the install path of configs
		if config is None:
			self.path_install("/etc/"+name)
		else:
			self.install_path=config

	def init(self,action=None):
		status=0
		if action == "start" or action == "stop" or action == "status" or action == "restart":
			if self.type == "remote":
				if run("service "+self.name+" "+action+"", timeout=240, quiet=True).return_code == 1:
					status=1
			else:
				if local("service "+self.name+" "+action+"i").return_code == 1:
					status=1

			if status == 0:
				print(green("The daemon '"+self.name+"' on the host '"+env.host_string+"' is "+action))
			else:
				print(red("The daemon '"+self.name+"' on the host "+env.host_string+" isn't "+action+"ed"))
				sys.exit()
		else:
			print(red("Usage action: start, stop, status, restart"))
			sys.exit()
		return 0

	def path_templates(self,name):
		if os.path.exists(self.root_templates+"/"+name):
			self.templates_path=self.root_templates+"/"+name
		else:
			print(red("The  path '"+self.root_templates+"/"+name+"' on the host '"+env.host_string+"' doesn't exist"))
			sys.exit()

	def path_install(self,path):
		status=0

		if self.type == "remote":
			if run("test -d "+path+"", timeout=240, quiet=True).return_code == 0:
				self.install_path=path
			else:
				status=1
		else:
			if os.path.exists(path):
				self.install_path=path
			else:
				status=1

		if status == 1:
			print(red("The path '"+path+"' on the host '"+env.host_string+"' doesn't exist"))
			sys.exit()

	def chkconfig(self,turn="off"):
		status=0
		with quiet():
			if self.type == "remote":
				if run("chkconfig "+self.name+" "+turn+"", timeout=240).return_code == 1:
					status=1
			else:
				if local("chkconfig "+self.name+" "+turn+"", timeout=240).return_code == 1:
					status=1

			if status == 0:
				print(green("The "+self.name+" on the host '"+env.host_string+"' was added to the autostart"))
			else:
				print(red("The "+self.name+" on the host '"+env.host_string+"' wasn't added to the autostart"))

	def yum(self,packages=None,action=None):
		if action == "install" or action == "remove" or action == "update":
			with quiet():
				if run('yum -y '+action+' '+packages+'', timeout=240).return_code == 0:
					print(green("The "+packages+" on the host '"+env.host_string+"' "+action+"ed successfully"))
				else:
					print(red("The "+packages+" on the host '"+env.host_string+"' didn't "+action))
					sys.exit()
		else:
			print(red("The "+action+" not supported"))
			sys.exit()


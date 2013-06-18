#!/usr/bin/python
#
# Author: Maxim Ivchenko
#
# description:
#	This cook will be to cook SSHD. 
#	He can copy your key to all hosts and do start, stop, restart SSHD



from fabric.api import *
from fabric.contrib import *
from fabric.colors import *
import jinja2
import os
import glob



# Get syntax
def syntax():
	print (green('\n\
	# Description \n\
	This cook will be to cook SSHD. \n\
	He can copy your key to all hosts and do start, stop, restart SSHD'))
	
	print (blue('\n\
	# Install your ssh key \n\
	cp ~/.ssh/id_rsa.pub templates/ssh/keys/your_name.pub \n\
	fab -f ssh.py install_keys -H webdb1,webdb2 \n\
	\n\
	# Stop, start, restart sshd \n\
	fab -f ssh.py stop:1 -H webdb1,webdb2 \n\
 	fab -f ssh.py start:1 -H webdb1,webdb2 \n\
 	fab -f ssh.py restart:1 -H webdb1,webdb2'))

# PATH to templates
def get_templates(path='templates/ssh'):
	global templates_path
	templates_path=path


# PATH to  install
def get_install(path='/etc/ssh'):
	global install_path
	install_path=path


# Set PATH
def path():
	if 'templates_path' not in globals():
		execute(get_templates)
	if 'install_path' not in globals():
		execute(get_install)


# Unset path
def unset_path():
	del globals()['templates_path']
	del globals()['install_path']



# Start
def start(silent):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to start the sshd?', default=True);

	if action:
		run('service sshd start');


# Stop
def stop(silent):

	if silent:
		action=1
	else:	
		action=console.confirm('Do you want to stop the sshd?', default=True);

	if action:
		run('service sshd stop');


# Restart
def restart(silent):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to restart the sshd?', default=True);

	if action:
		run('service sshd restart');


# List keys
def get_keys():
	return glob.glob(''+templates_path+'/keys/*.pub')
	


# Install keys
def install_keys():

	# set path of templates
	execute(path)

	# install keys
	for key in get_keys():
		local('ssh-copy-id -i '+key+' %(host_string)s' % env);

	# unset path
	unset_path()

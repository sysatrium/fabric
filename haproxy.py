#!/usr/bin/python
#
# Author: Maxim Ivchenko
#
# description:
#	This cook will be to cook the Haproxy.
#	He can install, configure and start, stop, restart of Haproxy.




from fabric.api import *
from fabric.contrib import *
from fabric.colors import *
import jinja2
import os
import glob


# Get syntax
def syntax():
	print (green('\n\
	This cook will be to cook the Haproxy. \n\
	He can install, configure and start, stop, restart of Haproxy.'))

	print (blue('\n\
	# Install and configure Haproxy \n\
	fab -f haproxy.py deploy_haproxy:backends="webdb1 webdb2",apps="conference cc" -H localhost \n\
	or\n\
	fab -f haproxy.py deploy_haproxy:"webdb1 webdb2","conference cc" -H localhost \n\
	\n\
	# Start, stop, restart Haproxy \n\
	fab -f haproxy.py start:1 -H localhost \n\
	fab -f haproxy.py stop:1 -H localhost \n\
	fab -f haproxy.py restart:1 -H localhost \n\
	\n\
	available apps: cc, televoting, vcc, conference, url, community, freephone, chat, mas, mvpn, tms'))
	

# PATH to templates
def get_templates(path='templates/haproxy'):
	global templates_path
	templates_path=path


# PATH to  install
def get_install(path='/etc/haproxy'):
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



# Start haproxy
def start(silent):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to start the haproxy?', default=True)

	if action:
		run('service haproxy start')


# Stop haproxy
def stop(silent):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to stop the haproxy?', default=True)

	if action:
		run('service haproxy stop')


# Restart haproxy
def restart(silent):
	
	if silent:
		action=1
	else:
		action=console.confirm('Do you want to restart the haproxy?', default=True)

	if action:
		run('service haproxy restart')


# Install haproxy
def install_soft(silent):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to install any rpm packages of the haproxy?', default=True)
	
	if action:
		run('yum -y install haproxy hatop')



# Configuration Haproxy
def haproxy_configure(backends,apps):

	execute(path)

	backends=backends.split(' ')
	apps=apps.split(' ')

	context={
		'backends': backends,
		'apps': apps,
	}
	
	files.upload_template('haproxy.cfg', ''+install_path+'/haproxy.cfg', context=context, use_jinja=True, template_dir=templates_path)
	run('chkconfig haproxy on')



def deploy_haproxy(backends='webdb1 webdb2',apps='conference vcc'):
	install_soft(silent=0)
	haproxy_configure(backends=backends,apps=apps)
	start(silent=0)

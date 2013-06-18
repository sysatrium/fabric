#!/usr/bin/python
#
# Author: Maxim Ivchenko
#
# description:
#	This cook will be to cook the Tomcat.
#	He can install, configure and start, stop, restart of the Tomcat.




from fabric.api import *
from fabric.contrib import *
from fabric.colors import *
import jinja2
import os
import glob
import sys
import time
import string


# Get syntax
def syntax():
	print (green("""
	This cook will be to cook the Tomcat.
	He can install, configure and start, stop, restart of the Tomcat.
	"""))

	print (blue("""
	# Install and configure Tomcat


	# Start, stop, restart Tomcat
	fab -f tomcat.py start:1 -H localhost
	fab -f tomcat.py stop:1 -H localhost
	fab -f tomcat.py restart:1 -H localhost

	available apps: cc, vcc, conference, url, community, mas"""))
	

# PATH to templates
def get_templates(path='templates/tomcat'):
	global templates_path
	templates_path=path


# PATH to  install
def get_install(path='/etc/tomcat'):
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


# Start tomcat applications
def start(apps='',silent=0):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to start the tomcat applications '+apps+'?', default=True)

	apps=apps.split(' ')

	for app in apps:
		if action:
			run('service tomcat7-'+app+' start')


# Stopt tomcat applications
def stop(apps='',silent=0):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to stop the tomcat applications '+apps+'?', default=True)

	apps=apps.split(' ')

	for app in apps:
		if action:
			run('service tomcat7-'+app+' stop')


# Restart tomcat applications
def restart(apps='',silent=0):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to restart the tomcat applications '+apps+'?', default=True)

	apps=apps.split(' ')

	for app in apps:
		if action:
			run('service tomcat7-'+app+' restart')



# Reload tomcat applications
def reload(apps='',silen=0):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to reload the tomcat applications '+apps+'?', default=True)

	apps=apps.split(' ')

	for app in apps:
		if action:
			run('service tomcat7-'+app+' reload')



# Install tomcat
def install_soft(silent):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to install any rpm packages of the tomcat?', default=True)
	
	if action:
		run('yum -y install tomcat7')


# Create symlinc
def symlink_tomcats(apps=''):
	if apps == '':
		print (red('You must give me a list of the tomcat apps through the gap for the deploy.'))
		exit()

	apps=apps.split(' ')

	for app in apps:
		run('ln -sf /etc/init.d/tomcat7 /etc/init.d/tomcat7-'+app)


# Define standart ports
def set_ports():
	apps={
		'vcc': '8080',
		'url': '8081',
		'conference': '8082',
		'community': '8083',
		'crc': '8084',
		'freephone': '8085',
		'televoting': '8086',
		'chat': '8087',
		'cc': '8088',
		'mas': '8089',
		'mvpn': '8090',
		'tms': '8091',
		'kamailio-manager': '8092',
	}
	return apps


# Chkconfig
def chkconfig_on(apps=''):
	if apps == '':
		print (red('You must give me a list of the tomcat apps through the gap for the deploy.'))
		exit()

	apps=apps.split(' ')

	run('chkconfig tomcat7 off')

	for app in apps:
		run('chkconfig --add tomcat7-'+app)
		run('chkconfig tomcat7-'+app+' on')


# Configuration Tomcat
def tomcat_configure(apps='',cluster=''):
	if apps == '':
		print (red('You must give me a list of the tomcat apps through the gap for the deploy.'))
		exit()

	# set path
	get_templates(path="templates/tomcat/sysconfig")
	get_install(path="/etc/sysconfig")

	apps=apps.split(' ')

	standart_apps=set_ports()

	for app in apps:

		context={
		'app': app,
		'port': standart_apps[app],
		'cluster': cluster,
		}

		files.upload_template('tomcat7', ''+install_path+'/tomcat7-'+app, context=context, use_jinja=True, template_dir=templates_path)


# Deploy tomcat
def deploy_tomcat(apps='',cluster=1):
	install_soft(silent=0)
	symlink_tomcats(apps=apps)
	tomcat_configure(apps=apps,cluster=cluster)
	chkconfig_on(apps=apps)
	start(apps=apps,silent=0)
	stop(apps=apps,silent=1)

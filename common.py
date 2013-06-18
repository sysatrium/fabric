#!/usr/bin/python

from fabric.api import *
from fabric.contrib import *
from fabric.colors import *

# PATH to templates
def get_templates(path=''):
	if path=='':
		print(red('Enter a path to the templates'))
		exit()
	return path


# PATH to  install
def get_install(path=''):
	if path=='':
		print(red('Enter a path to the install'))
		exit()
	return path


# Start some services
# fab -f *.py start:services="tomcat7 nginx",silent=1
def start(services='',silent=0):
	if services == '':
		print(red('You must give me a list of services over gap for complete start'))
		exit()

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to start the \''+services+'\'?', default=True)

	services=services.split(' ')

	for service in services:
		print service
		if action:
			run('service '+service+' start')


# Stop some services
# run: fab -f *.py stop:services="tomcat7 nginx",silent=1
def stop(services='',silent=0):
	if services == '':
		print(red('You must give me a list of services over gap for complete stop'))
		exit()

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to stop the \''+services+'\'?', default=True)

	services=services.split(' ')

	for service in services:
		if action:
			run('service '+service+' stop')


# Retart some services
# run: fab -f *.py restart:services="tomcat7 nginx",silent=1
def restart(services='',silent=0):
	if services == '':
		print(red('You must give me a list of services over gap for complete restart'))
		exit()

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to restart the \''+services+'\'?', default=True)

	services=services.split(' ')

	for service in services:
		if action:
			run('service '+service+' restart')


# Reload some services
# run: fab -f *.py reload:services="tomcat7 nginx",silent=1
def reload(services='',silent=0):
	if services == '':
		print(red('You must give me a list of services over gap for complete reload'))
		exit()

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to reload the \''+services+'\'?', default=True)

	services=services.split(' ')

	for service in services:
		if action:
			run('service '+service+' reload')


# Chkconfig some services
# run: fab -f *.py chkconfig_on:services="tomcat7 nginx",silent=1
def chkconfig_on(services='',silent=0):
	if services == '':
		print(red('You must give me a list of services over gap that will be add to the startup'))
		exit()

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to add the \''+services+'\' to the startup?', default=True)

	services=services.split(' ')

	for service in services:
		if action:
			run('chkconfig '+service+' on')


# Chkconfig some services
# run: fab -f *.py chkconfig_off:services="tomcat7 nginx",silent=1
def chkconfig_off(services='',silent=0):
	if services == '':
		print(red('You must give me a list of services over gap that will be remove from the startup'))
		exit()

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to remove the \''+services+'\' from the startup?', default=True)

	services=services.split(' ')

	for service in services:
		if action:
			run('chkconfig '+service+' off')
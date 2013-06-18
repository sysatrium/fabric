#!/usr/bin/python
#
# Author: Maxim Ivchenko
#
# description:
#	This cook will be to cook some client web interfaces and some tomcat applications.
#	He can deploy some client web interfaces to the web hosts.
#	The default path of deploy of clients web interfaces is /var/www




from fabric.api import *
from fabric.contrib import *
from fabric.colors import *
import jinja2
import os
import glob
import sys
import MySQLdb
import time
import string
import common


# Get syntax
def syntax():
	print (green("""
	# Description
	This cook will be to cook some client web interfaces.
	He can deploy some client web interfaces to the web hosts.
	The default path of deploy of clients web interfaces is /var/www

	If you haven't got the ssh access to the web hosts of customer,
	then you must upload clients web interfaces to 'templates/web-interfaces/interfaces_name/data'.
	"""+red('For example:')+"""templates/web-interfaces/vcc/data

	# Tomcat applications
	"""+red('Available tomcat apps:')+""" vcc, conference, url, community, mas, massonic, cc"""))

	print (blue("""
	# Deploy some clients web interfaces
	fab -f web-interfaces.py deploy_clients:interfaces="vcc community share conference" -H web1,web2"""))
	

# Get web-interfaces
# fab -f web-interfaces.py get_client_interfaces:interfaces="vcc community conference"
def get_client_interfaces(interfaces=''):
	if interfaces == '':
		print (red('You must give me a list of interfaces through the gap for the deploy.'))
		exit()

	interfaces=interfaces.split(' ')

	# check share
	if 'share' not in interfaces:
		print (red('You must give the interface - share, too'))
		exit()

	# set path
	templates_path=common.get_templates(path='templates/web-interfaces')

	for interface in interfaces:
		if os.path.exists(templates_path+'/'+interface):
			local('test -d '+templates_path+'/'+interface+' && cd '+templates_path+' && rm -rf ./'+interface)

		if interface == 'vcc':
			local('git clone -b teligent git@git.teligent.ru:/webstroy/'+interface+'-teligent.git '+templates_path+'/'+interface+'')
		else:
			local('git clone git@git.teligent.ru:/webstroy/'+interface+'-teligent.git '+templates_path+'/'+interface+'')



# Put the interfaces to the web-hosts
# fab -f web-interfaces.py put_client_interfaces:interfaces="vcc community share" -H webdb1,webdb2
def put_client_interfaces(interfaces=''):
	if interfaces == '':
		print (red('You must give me a list of interfaces through the gap for the deploy.'))
		exit()

	interfaces=interfaces.split(' ')

	# check share
	if 'share' not in interfaces:
		print (red('You must give the interface - \'share\', too'))
		exit()

	# set path
	templates_path=common.get_templates(path='templates/web-interfaces')
	install_path=common.get_install(path='/var/www')

	if not files.exists(install_path):
		run('mkdir -p '+install_path)

	for interface in interfaces:
		if not files.exists(install_path+'/'+interface):
			run('mkdir '+install_path+'/'+interface)
		put(templates_path+'/'+interface+'/data/*', install_path+'/'+interface)


# Deploy clients web-interfaces
# fab -f deploy_clients:interfaces="vcc community conference share" -H webdb1,webdb2
def deploy_clients(interfaces='',silent=0):
	if silent:
		action=1
	else:
		action=console.confirm('Do you have got the ssh access to the web-hosts of a customer?', default=True)

	if action:
		get_client_interfaces(interfaces=interfaces)
		put_client_interfaces(interfaces=interfaces)
	else:
		put_client_interfaces(interfaces=interfaces)


# Create the url for Nexus
def set_nexus_url(g='',r='public',a='',p='war',v='',c=''):
	nexus_options={
		'base_url': 'http://nexus.teligent.ru/nexus/service/local/artifact/maven/redirect',
		'g': g,
		'r': r,
		'a': a,
		'p': p,
		'v': v,
	}

	if c == '':
		url=""+nexus_options['base_url']+" -dg="+g+" -dr="+r+" -da="+a+" -dp="+p+" -dv="+v+""
	else:
		url=""+nexus_options['base_url']+" -dg="+g+" -dr="+r+" -da="+a+" -dp="+p+" -dv="+v+" -dc="+c+""

	return url


# Get tomcat7 applications
# fab -f web-interfaces.py get_tomcat_apps:apps="vcc conference url"
def get_tomcat_apps(apps='',version='release',ext='war'):
	if apps == '':
		print (red('You must give me a list of the tomcat apps through the gap for the deploy.'))
		exit()

	if (version != 'release' and version != 'snapshot'):
		print(red('The available values of the version is release or snapshot.'))
		version=prompt('What a version of the apps do you want - release|snapshot?', default='release')

	if version == 'snapshot':
		version='LATEST'

	apps=apps.split(' ')

	# set path
	templates_path=common.get_templates(path="templates/web-interfaces/tomcat")

	version=version.upper()

	# Create directory
	if not os.path.exists(templates_path):
		local('mkdir '+templates_path)

	for app in apps:
		if app == 'vcc':
			local('curl -s -o '+templates_path+'/'+app+'.'+ext+' -L -G '+set_nexus_url(g='se.teligent.mobicom.'+app,a=app+'-web',v=version,p=ext))
		if app == 'conference':
			local('curl -s -o '+templates_path+'/'+app+'.'+ext+' -L -G '+set_nexus_url(g='se.teligent.mobicom.'+app,a=app+'-web',v=version,p=ext))
		if app == 'url':
			local('curl -s -o '+templates_path+'/'+app+'.'+ext+' -L -G '+set_nexus_url(g='se.teligent.mobicom.'+app,a=app+'-web',v=version,p=ext))
		if app == 'community':
			local('curl -s -o '+templates_path+'/'+app+'.'+ext+' -L -G '+set_nexus_url(g='se.teligent.'+app+'',a=app+'-web',v=version,p=ext))
		if app == 'mas':
			local('curl -s -o '+templates_path+'/'+app+'.'+ext+' -L -G '+set_nexus_url(g='se.teligent.mobicom.'+app+'',a=app+'-web',v=version,p=ext))
		if app == 'cc':
			local('curl -s -o '+templates_path+'/'+app+'.'+ext+' -L -G '+set_nexus_url(g='se.teligent.'+app+'',a=app+'-web',v=version,p=ext))
		if app == 'massonic':
			local('curl -s -o '+templates_path+'/'+app+'.'+ext+' -L -G '+set_nexus_url(g='se.teligent.mas',a='mas-web',v=version,p=ext))



# Put the tomcat applications to the web hosts
# fab -f web-interfaces.py put_tomcat_apps:apps="vcc conference" -H webdb1,webdb2
# fab -f web-interfaces.py put_tomcat_apps:apps="vcc conference",ext="war" -H webdb1,webdb2
def put_tomcat_apps(apps="",ext='war'):
	if apps == '':
		print (red('You must give me a list of the tomcat apps through the gap for the deploy.'))
		exit()

	apps=apps.split(' ')

	# set path
	templates_path=common.get_templates(path="templates/web-interfaces/tomcat")
	install_path=common.get_install(path="/tmp/tomcat")

	if not files.exists(install_path):
		run('mkdir '+install_path)

	for app in apps:
			if os.path.exists(templates_path+'/'+app+'.'+ext):
				put(templates_path+'/'+app+'.'+ext, install_path)
			else:
				print(red('The application '+app+' doesn\'t upload to the '+env.host_string+' because it not exists in '+templates_path))


# Install tomcat applications
# fab -f web-interfaces.py install_tomcat_apps:apps="vcc conference" -H webdb1,webdb2
# fab -f web-interfaces.py install_tomcat_apps:apps="vcc conference",ext="war" -H webdb1,webdb2
def install_tomcat_apps(apps='',ext='war'):
	if apps == '':
		print (red('You must give me a list of the tomcat apps through the gap for the deploy.'))
		exit()

	apps=apps.split(' ')

	# set path
	templates_path=common.get_templates(path='/tmp/tomcat')
	install_path=common.get_install(path='/var/lib/tomcat7')

	if not files.exists(templates_path):
		print(red('The path '+templates_path+' to the tomcat applications on the '+env.host_string+' isn\'t exists'))
		exit()

	for app in apps:
		if files.exists(templates_path+'/'+app+'.'+ext):
			if not files.exists(install_path+'/'+app+'/webapps/'+app):
				run('mkdir '+install_path+'/'+app+'/webapps/'+app)
				run('cp '+templates_path+'/'+app+'.'+ext+' '+install_path+'/'+app+'/webapps/'+app)
				with cd(install_path+'/'+app+'/webapps/'+app):
					if files.exists('/usr/bin/unzip'):
						run('unzip '+app+'.'+ext)
						run('rm -f '+app+'.'+ext)
					else:
						print(red('You must install the unzip on the '+env.host_string))
						exit()
		else:
			print(red('The path to the tomcat\'s application \''+app+'\' isn\'t exists'))


# Get  a profile of the tomcat apps
# fab -f web-interfaces.py get_profiles_apps:apps='vcc conference',profile='flagman-web1'
def get_profile_app(apps='',version='release',profile='',ext='tar.gz'):
	if apps == '':
		print (red('You must give me a list of the tomcat apps through the gap for the deploy.'))
		exit()

	if (version != 'release' and version != 'snapshot'):
		print(red('The available values of the version is release or snapshot.'))
		version=prompt('What a version of the profile do you want - release|snapshot?', default='release')

	if version == 'snapshot':
		version='LATEST'

	if not profile and profile == '':
		profile=prompt('What a name of the profile of the tomcat applications do you want?', default='')

	apps=apps.split(' ')

	# set path
	templates_path=common.get_templates(path="templates/web-interfaces/profiles")

	version=version.upper()

	# create directory
	if not os.path.exists(templates_path):
		local('mkdir '+templates_path)

	for app in apps:
		if app == 'vcc':
			local('curl -s -o '+templates_path+'/'+profile+'.'+ext+' -L -G '+set_nexus_url(g='se.teligent.mobicom.'+app,a=app+'-web',v=version,c=profile,p=ext))
		if app == 'conference':
			local('curl -s -o '+templates_path+'/'+profile+'.'+ext+' -L -G '+set_nexus_url(g='se.teligent.mobicom.'+app,a=app+'-web',v=version,c=profile,p=ext))
		if app == 'url':
			local('curl -s -o '+templates_path+'/'+profile+'.'+ext+' -L -G '+set_nexus_url(g='se.teligent.mobicom.'+app,a=app+'-web',v=version,c=profile,p=ext))
		if app == 'community':
			local('curl -s -o '+templates_path+'/'+profile+'.'+ext+' -L -G '+set_nexus_url(g='se.teligent.'+app+'',a=app+'-web',v=version,c=profile,p=ext))
		if app == 'mas':
			local('curl -s -o '+templates_path+'/'+profile+'.'+ext+' -L -G '+set_nexus_url(g='se.teligent.mobicom.'+app+'',a=app+'-web',v=version,c=profile,p=ext))
		if app == 'cc':
			local('curl -s -o '+templates_path+'/'+profile+'.'+ext+' -L -G '+set_nexus_url(g='se.teligent.'+app+'',a=app+'-web',v=version,c=profile,p=ext))
		if app == 'massonic':
			local('curl -s -o '+templates_path+'/'+profile+'.'+ext+' -L -G '+set_nexus_url(g='se.teligent.mas',a='mas-web',v=version,c=profile,p=ext))


# Put profiles of the tomcat applications to the web hosts
# fab -f web-interfaces.py put_profiles_apps:apps="vcc conference" -H webdb1,webdb2
# fab -f web-interfaces.py put_profiles_apps:apps="vcc conference",ext="tar.gz" -H webdb1,webdb2
def put_profile_app(profiles='',ext='tar.gz'):
	if not profiles and profiles == '':
		profiles=prompt('What a name of the profiles of the tomcat applications do you want?', default='')

	profiles=profiles.split(' ')

	# set path
	templates_path=common.get_templates(path="templates/web-interfaces/profiles")
	install_path=common.get_install(path="/tmp/tomcat/profiles")

	if not files.exists(install_path):
		run('mkdir '+install_path)

	for profile in profiles:
			if os.path.exists(templates_path+'/'+profile+'.'+ext):
				put(templates_path+'/'+profile+'.'+ext, install_path)
			else:
				print(red('The profile '+profile+'.'+ext+' doesn\'t upload to the '+env.host_string+' because it not exists in '+templates_path))


# Install profiles of the tomcat applications
# fab -f web-interfaces.py install_profiles_apps:apps="vcc conference" -H webdb1,webdb2
# fab -f web-interfaces.py install_profiles_apps:apps="vcc conference",ext="tar.gz" -H webdb1,webdb2
def install_profile_app(apps='',ext='tar.gz',profile=''):
	if apps == '':
		print (red('You must give me a list of the tomcat apps through the gap for the deploy.'))
		exit()

	if not profile and profile == '':
		profile=prompt('What a name of the profile of the tomcat applications do you want?', default='')

	apps=apps.split(' ')

	# set path
	templates_path=common.get_templates(path='/tmp/tomcat/profiles')
	install_path=common.get_install(path='/var/lib/tomcat7')

	if not files.exists(templates_path):
		print(red('The path '+templates_path+' to the tomcat applications isn\'t exists'))
		exit()

	for app in apps:
		if files.exists(templates_path+'/'+profile+'.'+ext):
			run('cp '+templates_path+'/'+profile+'.'+ext+' '+install_path+'/'+app+'/webapps/'+app)
			with cd(install_path+'/'+app+'/webapps/'+app+''):
				with prefix('tar -xzf '+profile+'.'+ext):
					run('rm -f '+profile+'.'+ext)
		else:
			print(red('The path to the profile \''+profile+'\' of the tomcat\'s application \''+app+'\' isn\'t exists'))



# Deploy the tomcat's applications
def deploy_tomcat_apps(apps='',ext='war',version='release',silent=1,profile=''):
	get_tomcat_apps(apps=apps,version=version,ext=ext)
	put_tomcat_apps(apps=apps,ext=ext)

	# Formating a list of services
	applications=apps.split(' ')
	services=list()
	for app in applications:
		services.append('tomcat7-'+app)
	services=' '.join(services)

	common.start(services=services,silent=1)
	common.stop(services=services,silent=1)
	install_tomcat_apps(apps=apps,ext=ext)
	get_profile_app(apps=apps,ext='tar.gz',version='',profile=profile)
	put_profile_app(profiles=profile,ext='tar.gz')
	install_profile_app(apps=apps,profile=profile,ext='tar.gz')
	common.start(services=services,silent=1)
#!/usr/bin/python
#
# Author: Maxim Ivchenko
#
# description:
#	This cook will be to cook a zabbix proxy and zabbix agent.
#	He can install, configure and start, stop, restart zabbix proxy and zabbix agent



from fabric.api import *
from fabric.contrib import *
from fabric.colors import *
import jinja2
import os
import glob

# Get syntax
def syntax():
	print (green('\n\
	# Description\n\
	This cook will be to cook a zabbix proxy and zabbix agent.\n\
	He can install, configure and start, stop, restart zabbix proxy and zabbix agent.'))
	
	print (blue('\n\
	# Install and configure zabbix proxy \n\
	fab -f zabbix.py deploy_proxy -H kickstarts \n\
	\n\
	# Install and configure zabbix agent \n\
	fab -f zabbix.py deploy_agent -H webdb1,webdb2,sipfe1 \n\
	\n\
	# Zabbix agent configure and restart \n\
	fab -f zabbix.py zabbix_agent_configure:zabbix_server=192.168.1.1,plugins=1 restart_agent:1 -H webdb1,webdb2,sipfe1 \n\
	\n\
	# Start, stop, restart zabbix proxy/agent \n\
	fab -f zabbix.py start_proxy:1 -H webdb1 \n\
	fab -f zabbix.py stop_proxy:1 -H webdb1 \n\
	fab -f zabbix.py restart_proxy:1 -H webdb1 \n\
	\n\
	fab -f zabbix.py start_agent:1 -H webdb1 \n\
	fab -f zabbix.py stop_agent:1 -H webdb1 \n\
	fab -f zabbix.py restart_agent:1 -H webdb1'))


# PATH to templates
def get_templates(path='templates/zabbix'):
	global templates_path
	templates_path=path


# PATH to  install
def get_install(path='/etc/zabbix'):
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



# Start zabbix-agent
def start_agent(silent):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to start the zabbix-agent?', default=True)

	if action:
		run('service zabbix-agent start')


# Stop zabbix-agent
def stop_agent(silent):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to stop the zabbix-agent?', default=True)

	if action:
		run('service zabbix-agent stop')


# Restart zabbix-agent
def restart_agent(silent):
	
	if silent:
		action=1
	else:
		action=console.confirm('Do you want to restart the zabbix-agent?', default=True)

	if action:
		run('service zabbix-agent restart')


# Start zabbix-proxy
def start_proxy(silent):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to start the zabbix-proxy?', default=True)

	if action:
		run('service zabbix-proxy start')


# Stop zabbix-proxy
def stop_proxy(silent):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to stop the zabbix-proxy?', default=True)

	if action:
		run('service zabbix-proxy stop')


# Restart zabbix-proxy
def restart_proxy(silent):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to restart the zabbix-proxy?', default=True)

	if action:
		run('service zabbix-proxy restart')


# Install agent
def install_agent(silent):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to install rpm packages of the zabbix-agent', default=True)

	if action:
		run('yum -y install zabbix-agent')


# Install proxy
def install_proxy(silent):

	if silent:
		action=1
	else:
		action=console.confirm('Do you want to install rpm packages of the zabbix-proxy', default=True)
	
	if action:
		run('yum -y install zabbix-proxy zabbix-proxy-mysql mysql mysql-server')


# MySQL configure
def mysql_configure():

	character=prompt('What a encoding do you want?', default='utf8');
	skip_networking=console.confirm('Enabled the option \'skip-networking\'?', default=True)
	version=prompt('What a version of MySQL do you used?', default='5.1')
	server_id=1
	
	# set path
	execute(get_templates, 'templates/mysql')
	execute(get_install, '/etc')

	context={
		'character': character,
		'server_id': server_id,
		'skip_networking': skip_networking,
		'version': version,
	}

	files.upload_template('zabbix.cnf', ''+install_path+'/my.cnf', context=context, use_jinja=True, template_dir=templates_path)

	run('service mysqld start');
	run('mysqladmin -u root password \'teligent\'');
	run('mysql -u root -pteligent -e "create database zabbix;"')
	run('mysql -u root -pteligent -e "grant ALL on zabbix.* to \'zabbix\'@\'localhost\' identified by \'zabbix\';"');

	sql_path="/usr/share/doc/$(ls /usr/share/doc | grep zabbix-proxy-mysql)/database/mysql"
	run('cd '+sql_path+'; mysql -u zabbix -pzabbix zabbix < schema.sql')
	run('cd '+sql_path+'; mysql -u zabbix -pzabbix zabbix < images.sql')
	run('cd '+sql_path+'; mysql -u zabbix -pzabbix zabbix < data.sql')

	run('chkconfig mysqld on')

	# Unset path
	unset_path()


# Zabbix proxy configure
def zabbix_proxy_configure():

	zabbix_server=prompt('Enter a IP of the zabbix server', default='212.119.200.198')
	zabbix_proxy=prompt('Enter a hostname of the zabbix proxy', default='localhost')
	java_gw=prompt('Enter a IP of Java gateway', default='127.0.0.1')
	proxy_mode=prompt('Enter a mode of the zabbix proxy', default='passive')
	
	if proxy_mode == 'passive':
		mode=1
	else:
		mode=0

	context={
		'zabbix_server': zabbix_server,
		'proxy': zabbix_proxy,
		'java_gw': java_gw,
		'proxy_mode': mode,
	}

	# set path
	execute(path)
	
	files.upload_template('zabbix_proxy.conf', ''+install_path+'/zabbix_proxy.conf', context=context, use_jinja=True, template_dir=templates_path)

	run('chkconfig zabbix-proxy on')



# Zabbix proxy main install
def deploy_proxy():
	install_proxy(silent=0)
	mysql_configure()
	zabbix_proxy_configure()
	start_proxy(silent=0)


# Zabbix agent configure
def zabbix_agent_configure(zabbix_server,plugins):

	if zabbix_server == '':
		zabbix_server=prompt('Enter a IP of zabbix server/proxy', default='localhost')

	if not plugins:
		plugins=console.confirm('Do you want to install any plugins for every hosts?')

	# set path
	execute(path)

	context={
		'zabbix_server': zabbix_server,
		'client': env.host_string,
	}	
	
	run('mkdir -p '+install_path+'/plugins')

	if plugins:
		if (env.host_string == 'webdb1' or env.host_string == 'webdb2'):
			put(templates_path + '/webdbX/plugins/*', ''+install_path+'/plugins')

		if (env.host_string == 'mrf1' or env.host_string == 'mrf2'):
			put(templates_path+'/mrfX/plugins/*', ''+install_path+'/plugins')

		if (env.host_string == 'sipfe1' or env.host_string == 'sipfe2'):
			put(templates_path + '/sipfeX/plugins/*', ''+install_path+'/plugins')

	run('chmod -R +x '+install_path+'/plugins/')

	files.upload_template('zabbix_agentd.conf', ''+install_path+'/zabbix_agentd.conf', context=context, use_jinja=True, template_dir=templates_path)

	run('chkconfig zabbix-agent on')


# Zabbix agent main install
def deploy_agent():
	install_agent(silent=0)
	zabbix_agent_configure(zabbix_server='',plugins=0)
	restart_agent(silent=0)

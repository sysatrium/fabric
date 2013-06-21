import os
import glob

from fabric.api import *
from fabric.contrib import *
from fabric.colors import *
import jinja2

sys.path.append(os.getcwd() + "/lib")

from daemonHaproxy import Haproxy


@task
def help():
	print (green("""
	This cook will be to cook the Haproxy.
	He can install, configure and start, stop, restart of Haproxy.

    The list of apps: cc, televoting, vcc, conference, url, community, freephone, chat, mas, mvpn, tms, red5
	"""+blue("""
        # Install and configure Haproxy
        fab -f haproxy.py haproxy:backends="webdb1 webdb2",apps="conference cc" -H localhost

        # Manual start Haproxy
        fab -f mysql.py init:start  -P -H lab1,lab2 -u root -p password
        
        # Manual stop Haproxy
        fab -f haproxy.py init:stop  -P -H lab1,lab2 -u root -p password
            
        # Manual restart Haproxy
        fab -f haproxy.py init:restart -P -H lab1,lab2 -u root -p password
            
        # Manual remove Haproxy
        fab -f haproxy.py init:remove -P -H lab1,lab2 -u root -p password

        # Manual update Haproxy
        fab -f haproxy.py init:update -P -H lab1,lab2 -u root -p password
            
        # Manual install Haproxy
        fab -f haproxy.py init:install -P -H lab1,lab2 -u root -p password
    """)))
	

@task
def haproxy(backands, apps):
    if not backands or not apps:
        print(red("Please, usage: fab -f haproxy.py help"))

    haproxy=haproxy(name="haproxy", config="/etc")
    haproxy.yum("haproxy", "install")
    haproxy.chkconfig("on")
    haproxy.set_haproxy(backands, apps)
    haproxy.init("start")

@task
def init(action):
    haproxy=Haproxy(name="haproxy", config="/etc")
    
    if action == "start" or action == "restart" or action == "stop":
        haproxy.init(action)
    
    if action == "remove" or action == "install" or action == "update":
        haproxy.yum("haproxy",action)

import sys
import os

import jinja2
from fabric.api import *
from fabric.contrib import *
from fabric.colors import *

import daemon


class Heartbeat(daemon.Daemon):


    # Gettings the standart settings of Heartbeat
    #
    def get_settings(self):
        self.vip=prompt("Enter a VIP, a netmask and a ethernet interface", default="127.0.0.1/24/eth0", validate=r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\/[0-9]{2}\/[a-z]+[0-9]{1}')
        self.gw=prompt("Enter a gateway for ping", default="127.0.0.1", validate=r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$')
        self.nodes=prompt('Enter a name of nodes over comma', default='host1,host2', validate=r'([a-z\-]|[0-9\-])+(,)+([a-z\-]|[0-9\-])+')
        self.services=prompt('Enter a list of services through gap', default=' ')

    # Creating the configuration files of Heartbeat from defined the settings
    #
    def set_configs(self,vip_type="None"):
        with quiet():
            files.upload_template('ha.cf', ''+self.install_path+'/ha.cf', context=self.settings, use_jinja=True, template_dir=self.templates_path, backup=True)
            if vip_type:
                templates_path=self.templates_path+"/"+vip_type
                files.upload_template('haresources', ''+self.install_path+'/haresources', context=self.settings, use_jinja=True, template_dir=templates_path, backup=True)
            put(''+self.templates_path+'/authkeys', self.install_path)
            run('chmod 600 '+self.install_path+'/authkeys', timeout=60)

    # Set of the standart settings for the single VIP and double VIP
    #
    def set_settings(self,double="off"):
        self.nodes=self.nodes.split(",")
        self.vip=self.vip.split("/")

        self.settings={
            'node1': self.nodes[0],
            'node2': self.nodes[1],
            'gw': self.gw,
            'netmask': self.vip[1],
            'interface': self.vip[2],
            'vip': self.vip[0],
            'services': self.services,
        }
             
        if double == "on":
            self.get_vip2_settings()

    # Getting and set of the standart settings of the Heartbeat with double VIP
    #         
    def get_vip2_settings(self):
        vip2=prompt("Enter a second VIP, a netmask and a ethernet interface", default="127.0.0.2/24/eth1", validate=r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\/[0-9]{2}\/[a-z]+[0-9]{1}')
        services2=prompt('Enter a list of services through gap', default=' ')
        
        vip2=vip2.split("/")
        self.settings['vip2']=vip2[0]
        self.settings['netmask2']=vip2[1]
        self.settings['interface2']=vip2[2]
        self.settings['services2']=services2

    # Set a 1 VIP
    #
    def singleVIP(self):
        self.get_settings()
        self.set_settings()
        self.set_configs("single")

    # Set a 2 VIP
    def doubleVIP(self):
        self.get_settings()
        self.set_settings(double="on")
        self.set_configs("double")

    # Set a internal ip VIP and external ip VIP
    def externalVIP(self):
        self.get_settings()
        self.set_settings(double="on")
        gw2=prompt('Enter a IP of external gateway', default='127.0.0.1', validate=r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$')
        self.settings['gw2']=gw2
        self.settings['services2']=self.settings['services2']+" defaultGw"
        self.set_configs("external")
        with quiet():
            files.upload_template('defaultGW', ''+self.install_path+'/resource.d/defaultGW', context=self.settings, use_jinja=True, template_dir=self.templates_path, backup=True)

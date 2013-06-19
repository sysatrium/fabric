import os
import glob
import sys
import time

import jinja2
import MySQLdb
from fabric.api import *
from fabric.contrib import *
from fabric.colors import *

import daemon


class Mysql(daemon.Daemon):
    

    root_password="teligent"
    teligent_password="teligent"

    # Single server
    def single(self,character="utf8",skip_networking="0",version="5.1"):
        
        # generate server-id
        x=0
        while(x < len(env.hosts)):
            if env.host_string == env.hosts[x]:
                server_id=x+1
            x = x + 1
        
        self.settings={
            'character': character,
            'server_id': server_id,
            'skip_networking': skip_networking,
            'version': version
        }

        files.upload_template('my.cnf', ''+self.install_path+'/my.cnf', context=self.settings, use_jinja=True, template_dir=self.templates_path)

    # common
    def postinstall(self):
        status=0
        with quiet():
            if run('mysqladmin -u root password \''+self.root_password+'\'', timeout=240).return_code == 0:
                print(green("The root's password was set to '"+self.root_password+"' on the host "+env.host_string+""))
            else:
                print(red("I can't set root's password on the host "+env.host_string+""))
                status=1

            query1=run('mysql -u root -p'+self.root_password+' -e "grant ALL on *.* to \'teligent\'@\'localhost\' identified by \''+self.teligent_password+'\';"', timeout=240).return_code
            query2=run('mysql -u root -p'+self.root_password+' -e "grant ALL on *.* to \'teligent\'@\'%\' identified by \''+self.teligent_password+'\';"', timeout=240).return_code
        
            if  query1 == 0 and query2 == 0:
                print(green("The teligent's password was set to '"+self.teligent_password+"' on the host "+env.host_string+""))
            else:
                print(red("I can't set teligent's password on the host "+env.host_string+""))
                status=1

        return status

    # Get information about master server - User, Password, Hostname, Binlog, Logposition
    def get_master_info(self,master):
        self.master=master
        con = MySQLdb.connect(host=""+self.master+"", user="teligent", passwd=""+self.teligent_password+"")
        cur = con.cursor()
        cur.execute('show master status;')
        data = cur.fetchall()
        for rec in data:
            self.master_info=dict(binlog=rec[0],logposition=rec[1])
            self.master_info['master']=self.master
            self.master_info['user']='teligent'
            self.master_info['password']=''+self.teligent_password+''
        con.close()
        return self.master_info

    # Setup of replication
    def set_replication(self,slave):
        status=0
        con = MySQLdb.connect(host=""+slave+"", user="teligent", passwd=""+self.teligent_password+"")
        cur = con.cursor()
        self.master_info["logposition"]=str(self.master_info["logposition"]).replace('L', '')
        cur.execute("change master to MASTER_HOST=\'"+ \
                    str(self.master_info['master'])+"\', MASTER_USER=\'"+ \
                    str(self.master_info['user'])+"\', MASTER_PASSWORD=\'"+ \
                    str(self.master_info['password'])+"\', MASTER_LOG_FILE=\'"+ \
                    str(self.master_info['binlog'])+"\', MASTER_LOG_POS="+str(self.master_info['logposition'])+";")
        cur.execute('start slave;')
        time.sleep(10)
        cur.execute('show slave status;')
        data=cur.fetchall()
        for rec in data:
            slave_status=dict(Slave_IO_Running=rec[10],Slave_SQL_Running=rec[11])

        if slave_status['Slave_IO_Running'] == 'Yes' and slave_status['Slave_SQL_Running'] == 'Yes':
            print (green("The replication on slave '"+slave+"' with master server '"+self.master+"' is OK"))
        else:
            print (red("The replication on slave '"+slave+"' with master server '"+self.master+"' isn't OK"))
            status=1

        con.close()
        return status

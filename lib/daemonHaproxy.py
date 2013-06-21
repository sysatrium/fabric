import os
import glob

from fabric.api import *
from fabric.contrib import *
from fabric.colors import *
import jinja2

import daemon


class Haproxy(daemon.Daemon):


    """
    The method "set_haproxy" will be setup and configure the Haproxy.
    It has two argument. This is "backend", which must be 
    appear in a format - "host1 host2 host3" and name applications, 
    which must be appear in a format - 'vcc url red5'.

    You can use the next list of applications:
        conference
        vcc
        url
        community
        crc
        freephone
        televoting
        chat
        cc
        mas
        mvpn
        tms
        red5
    """
    def set_haproxy(backends,apps):
        backends=backends.split(' ')
        apps=apps.split(' ')

        self.settings={
            'backends': backends,
            'apps': apps,
        }
        with quiet():
            files.upload_template('haproxy.cfg', ''+self.install_path+'/haproxy.cfg', 
                                context=self.settings, use_jinja=True, template_dir=self.templates_path)

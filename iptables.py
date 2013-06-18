#!/usr/bin/python
#
# Author: Maxim Ivchenko
#
# description:
#	This cook will be to cook the IPTABLES.


from fabric.api import *
from fabric.colors import *

# Get syntax
def syntax():
		print (green('\n\
		# Description \n\
		This cook will be to cook the IPTABLES.'))

		print (blue('\n\
		# Configure IPTABLES for webdbX node\n\
		fab -f iptables.py iptables_webdb -H webdb1,webdb2\n\
		\n\
		# Configure IPTABLES for sipfeX node\n\
		fab -f iptables.py iptables_sipfe -H sipfe1,sipfe2\n\
		\n\
		# Configure forwarding of ports for P90 Workstation\n\
		fab -f iptables.py iptables_p90ws -H kickstarts'))


# Forwarding the ports of Workstation
def iptables_p90ws():
	p901=prompt('Please enter a IP of the first P90 host', default='127.0.0.1');
	p902=prompt('Please enter a IP of the second P90 host', default='127.0.0.1');
	local_ip=prompt('Please enter a local IP', default='127.0.0.1');

	run('iptables -A FORWARD -i eth0 -o eth1 -j ACCEPT');
	run('iptables -A FORWARD -i eth1 -o eth0 -j ACCEPT');
	run('iptables -A PREROUTING -s 212.119.200.205/32 -p tcp -m tcp --dport 28201 -j DNAT --to-destination %(p901)s:28200' % env);
	run('iptables -A PREROUTING -s 212.119.200.205/32 -p tcp -m tcp --dport 28202 -j DNAT --to-destination %(p902)s:28200' % env);
	run('iptables -A PREROUTING -s 212.119.200.205/32 -p tcp -m tcp --dport 29200 -j DNAT --to-destination %(p901)s:29199' % env);
	run('iptables -A PREROUTING -s 212.119.200.205/32 -p tcp -m tcp --dport 29201 -j DNAT --to-destination %(p902)s:29199' % env);
	run('iptables -A PREROUTING -s 212.119.200.205/32 -p tcp -m tcp --dport 27001 -j DNAT --to-destination %(p901)s:27000' % env);
	run('iptables -A PREROUTING -s 212.119.200.205/32 -p tcp -m tcp --dport 27002 -j DNAT --to-destination %(p902)s:27000' % env);
	run('iptables -A POSTROUTING -p tcp -m tcp --dport 27000 -j SNAT --to-source %(local_ip)s' % env);
	run('iptables -A POSTROUTING -p tcp -m tcp --dport 29199 -j SNAT --to-source %(local_ip)s' % env);
	run('iptables -A POSTROUTING -p tcp -m tcp --dport 28200 -j SNAT --to-source %(local_ip)s' % env);
	run('service iptables save');


def iptables_webdb():
        env.internal_network=prompt('Please enter the internal network', default='192.168.0.0/16');

        run('iptables -A INPUT -m tcp -p tcp --dport 80 -m comment --comment "Web-Client interfaces" -j ACCEPT');
        run('iptables -A INPUT -m tcp -p tcp --dport 443 -m comment --comment "Web-Client interfaces" -j ACCEPT');
        run('iptables -A INPUT -m tcp -p tcp --dport 22 -s 212.119.200.205 -m comment --comment "LLC TELIGENT" -j ACCEPT');
        run('iptables -A INPUT -m tcp -p tcp --dport 8000 -s 212.119.200.208 -m comment --comment "LLC TELIGENT" -j ACCEPT');
        run('iptables -A INPUT -m tcp -p tcp --dport 9999 -s 212.119.200.205 -m comment --comment "LLC TELIGENT" -j ACCEPT');
        run('iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT');
        run('iptables -A INPUT -i lo -j ACCEPT');
        run('iptables -A INPUT -s %(internal_network)s -m comment --comment "Internal network" -j ACCEPT' % env);
        run('iptables -A INPUT -p icmp -j ACCEPT');
        run('iptables -P INPUT DROP');
        run('service iptables save');


def iptables_sipfe():
        env.internal_network=prompt('Please enter the internal network', default='192.168.0.0/16');
	number_pstn_gw=raw_input("How many pstn hosts do you have? [1|2]:")

	if not number_pstn_gw:
		number_pstn_gw = 1

	if number_pstn_gw == '2':
		env.pstn_gw1=prompt('Please enter a IP of the pstn gw number 1', default='127.0.0.1');
		env.pstn_gw2=prompt('Please enter a IP of the pstn gw number 2', default='127.0.0.1');
        	run('iptables -I INPUT -m tcp -p tcp --dport 5060 -s %(pstn_gw1)s -m comment --comment "PSTN GW1" -j ACCEPT' % env);
        	run('iptables -I INPUT -m tcp -p tcp --dport 5060 -s %(pstn_gw2)s -m comment --comment "PSTN GW1" -j ACCEPT' % env);
		run('iptables -I INPUT -m udp -p udp --dport 5060 -s %(pstn_gw1)s -m comment --comment "PSTN GW1" -j ACCEPT' % env);
        	run('iptables -I INPUT -m udp -p udp --dport 5060 -s %(pstn_gw2)s -m comment --comment "PSTN GW1" -j ACCEPT' % env);

	if number_pstn_gw != '2':
		env.pstn_gw=prompt('Please enter a IP of the pstn gw', default='127.0.0.1');
        	run('iptables -I INPUT -m tcp -p tcp --dport 5060 -s %(pstn_gw)s -m comment --comment "PSTN GW" -j ACCEPT' % env);
        	run('iptables -I INPUT -m udp -p udp --dport 5060 -s %(pstn_gw)s -m comment --comment "PSTN GW" -j ACCEPT' % env);
       
	run('iptables -A INPUT -p udp -m udp --dport 20000:21000 -m comment --comment "RTP" -j ACCEPT');

	# Access for LLC Teligent
        run('iptables -A INPUT -m tcp -p tcp --dport 22 -s 212.119.200.205 -m comment --comment "LLC TELIGENT" -j ACCEPT');
	run('iptables -A INPUT -s 212.119.200.205 -p udp -m udp --dport 5060 -m comment --comment "LLC TELIGENT" -j ACCEPT');
	run('iptables -A INPUT -s 212.119.200.205 -p tcp -m tcp --dport 5060 -m comment --comment "LLC TELIGENT" -j ACCEPT');
	
	# Common
        run('iptables -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT');
        run('iptables -A INPUT -i lo -j ACCEPT');
        run('iptables -A INPUT -s %(internal_network)s -m comment --comment "Internal network" -j ACCEPT' % env);
        run('iptables -A INPUT -p icmp -j ACCEPT');
        run('iptables -P INPUT DROP');
        run('service iptables save');

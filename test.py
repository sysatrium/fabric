#!/usr/bin/python

host=('lab1rhce', 'lab2rhce', 'lab3rhce', 'lab4rhce')

ho='lab1rhce'

x=0
while(x < len(host)):
	if ho == host[x]:
		server_id=x+1
	x = x + 1

print server_id


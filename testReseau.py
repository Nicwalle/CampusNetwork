#! /usr/bin/env python3

import pexpect
import json

with open('config.json') as json_config:
	router_info = json.load(json_config)
	for router1 in router_info["routers"] :
		child = pexpect.spawn('sudo ./connect_to.sh project_config ' + router1["name"])
		count = 0
		for router2 in router_info["routers"] : 
			child.sendline ('ping6 -c 1 ' + router2["ip"])
			idx = child.expect(['0% packet loss', r'\d+% packet loss'])
			if idx == 0 :
				count +=1
			else :
				print('Error : ' + router2["name"] + ' unreachable from ' + router1["name"])
		child.sendline ('ping6 -c 1 2001:6a8:308f:5::1')
		if child.expect(['0% packet loss', r'\d+% packet loss']) == 0:
			print(router1["name"]  + ' can reach the outside world')
		else:
			print(router1["name"]  + ' CANNOT reach the outside world')

		child.sendline('exit')
		print(router1["name"] + ' can reach ' + str(count) + '/' + str(len(router_info["routers"])))
print('End of the test')

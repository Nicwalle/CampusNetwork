#! /usr/bin/env python3

import pexpect
import json

from Logger import Logger

with open('../config.json') as json_config:
    router_info = json.load(json_config)
    for router1 in router_info["routers"]:
        child = pexpect.spawn('sudo ./connect_to.sh project_config ' + router1["name"])
        count = 0
        for router2 in router_info["routers"]:
            child.sendline('ping6 -c 1 ' + router2["ip"])
            idx = child.expect(['0% packet loss', r'\d+% packet loss'])
            if idx == 0:
                count += 1
            else:
                Logger.get_logger(router1["name"]).error(router2["name"] + ' unreachable from ' + router1["name"])

        child.sendline('exit')
        Logger.get_logger(router1["name"]).info(router1["name"] + ' can reach ' + str(count) + '/' + str(len(router_info["routers"])))
print('End of the test')

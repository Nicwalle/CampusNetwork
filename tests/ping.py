#! /usr/bin/env python3

import pexpect
import json

from Logger import Logger

def pings():
    with open('../config.json') as json_config:
        router_info = json.load(json_config)
        total_routers = len(router_info["routers"])
        for router1 in router_info["routers"]:
            child = pexpect.spawn('sudo ../connect_to.sh project_config ' + router1["name"])
            count = 0
            for router2 in router_info["routers"]:
                child.sendline('ping6 -c 1 ' + router2["ip"])
                idx = child.expect(['0% packet loss', r'\d+% packet loss'])
                if idx == 0:
                    count += 1
                else:
                    Logger.get_logger(router1["name"]).error("cannot reach router {router2_name}".format(router2_name=router2["name"]))

            child.sendline('exit')
            Logger.get_logger(router1["name"]).info('can reach {count}/{total} routers of the core network'.format(
                count=count,
                total=total_routers
            ))

if __name__ == "__main__":
    print()
    print("## Pinging all the routers from each router ##")
    print()

    pings()

    print()
    print('## Pinging test finished ##')
    print()

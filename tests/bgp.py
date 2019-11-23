#! /usr/bin/env python3

import pexpect
import json
import os
import time
import re
import networkx as nx
import matplotlib.pyplot as plt

from Logger import Logger

def bgp():
    config = get_config()

    for router1 in config["routers"]:
        child = pexpect.spawn('sudo ../connect_to.sh project_config ' + router1["name"])
        child.expect("bash-4.3#")
        
        for router2 in config["routers"]:
            child.sendline('traceroute6 -q 1 ' + router2["ip"])
            time.sleep(1)
            child.expect("bash-4.3#")

            hops = get_hops(child.before.decode('utf-8'))
            
        child.sendline('exit')
        # Logger.get_logger(router1["name"]).info('can reach {count}/{total} routers of the core network'.format(
        #     count=count,
        #     total=total_routers
        # ))

def get_neighbors(traceroute_result):
    hops = []
    for line in traceroute_result.split('\r\n'):
        regex = r"(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)"
        neighbor = re.search(r"(\d)\s+([a-fA-F0-9\:]+)\s+\([a-fA-F0-9\:]+\)\s+([\d\.]+)\s?ms", line)
        if hop is not None:
            hops.append(hop.group(2))
    return(hops)


def get_config():
    with open('../config.json') as json_config:
        return json.load(json_config)

bgp()

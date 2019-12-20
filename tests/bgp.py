#! /usr/bin/env python3

import pexpect
import json
import os
import time
import re

from Logger import Logger

def bgp():
    config = get_config()

    peers_ips = {}
    for router in config["routers"]:
        child = pexpect.spawn('sudo ../connect_to.sh project_config ' + router["name"])
        child.expect('bash-4.3#')
        child.sendline('LD_LIBRARY_PATH=/usr/local/lib vtysh')
        child.expect('group1#')
        child.sendline('show bgp summary')
        child.expect('group1#')

        neighbors = get_neighbors(child.before.decode('utf-8'))

        if router["bgp"]["active"]:
            for expected_neighbor in router["bgp"]["neighbors"]:
                if expected_neighbor["ip"] not in neighbors:
                    Logger.get_logger(router['name']).error('is not establishing an {bgp_type}BGP session with AS{as_number} on IP {ip_addr} but should be'.format(
                        bgp_type='i' if expected_neighbor['type'] == 'internal' else 'e',
                        as_number=expected_neighbor["as_number"],
                        ip_addr=expected_neighbor["ip"]
                    ))
                else:
                    try:
                        int(neighbors[expected_neighbor["ip"]]["state"])
                        if expected_neighbor['type'] == 'external':
                            Logger.get_logger(router['name']).info('has an active eBGP session with AS{as_number} ({ip_addr}) on interface {interface}'.format(
                                as_number=expected_neighbor["as_number"],
                                ip_addr=expected_neighbor["ip"],
                                interface=router["name"] + "-eth" + str(expected_neighbor["interface-number"])
                            ))
                            for ip in expected_neighbor["ping-ips"]:
                                peers_ips[ip] = expected_neighbor["as_number"]


                    except ValueError:
                        Logger.get_logger(router['name']).error('has no active {bgp_type}BGP session with AS{as_number} on IP {ip_addr}. (State is {state})'.format(
                            bgp_type='i' if expected_neighbor['type'] == 'internal' else 'e',
                            as_number=expected_neighbor["as_number"],
                            ip_addr=expected_neighbor["ip"],
                            state=neighbors[expected_neighbor["ip"]]["state"]
                        ))



        child.sendline('exit')
        child.expect('bash-4.3#')
    for router in config["routers"]:
        for ip in peers_ips:
            child = pexpect.spawn('sudo ../connect_to.sh project_config ' + router["name"])
            child.expect('bash-4.3#')
            child.sendline('ping6 -c 1 -I '+ router['ip'] + ' ' + ip)
            idx = child.expect(['0% packet loss', r'\d+% packet loss'])
            if idx == 0:
                Logger.get_logger(router["name"]).info("can reach ip {ip} of AS{as_number}".format(ip=ip, as_number=peers_ips[ip]))
            else:
                Logger.get_logger(router["name"]).error("cannot reach ip {ip} of AS{as_number}".format(ip=ip, as_number=peers_ips[ip]))

def get_neighbors(traceroute_result):
    neighbors = {}
    for line in traceroute_result.split('\r\n'):
        regex = r"(fde4:[a-fA-F0-9:]+)\s+(\S+)\s+([0-9]+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)"
        neighbor = re.search(regex, line)
        if neighbor is not None:
            neighbors[neighbor.group(1)] = {
                "ip": neighbor.group(1),
                "as_number": neighbor.group(3),
                "time": neighbor.group(9),
                "state": neighbor.group(10)
            }
    return(neighbors)


def get_config():
    with open('../config.json') as json_config:
        return json.load(json_config)

if __name__ == "__main__":
    bgp()

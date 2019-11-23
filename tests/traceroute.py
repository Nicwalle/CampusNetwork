#! /usr/bin/env python3

import pexpect
import json
import os
import time
import re
import networkx as nx
import matplotlib.pyplot as plt

from Logger import Logger

# os.chdir("/home/vagrant/CampusNetwork/")
class Traceroute:

    config = None
    graph = None
    dns = None

    @staticmethod
    def traceroutes():
        config = Traceroute.get_config()

        for router1 in config["routers"]:
            child = pexpect.spawn('sudo ../connect_to.sh project_config ' + router1["name"])
            child.expect("bash-4.3#")
            
            for router2 in config["routers"]:
                child.sendline('traceroute6 -q 1 ' + router2["ip"])
                time.sleep(1)
                child.expect("bash-4.3#")

                hops = Traceroute.get_hops(child.before.decode('utf-8'))
                expected = Traceroute.get_path(router1['ip'], router2['ip'])
                if hops != expected[0]:
                    Logger.get_logger(router1["name"]).warning('reached {router2} via {real_path} instead of {expected_path} ({name_expected_path})'.format(
                        router2=router2["name"],
                        real_path=' -> '.join(hops),
                        expected_path=' -> '.join(expected[0]),
                        name_expected_path=' -> '.join(expected[1])
                    ))
                else:
                    Logger.get_logger(router1["name"]).info('reached {router2} via {real_path} ({name_expected_path})'.format(
                        router2=router2["name"],
                        real_path=' -> '.join(hops),
                        name_expected_path=' -> '.join(expected[1])
                    ))
                
            child.sendline('exit')

    @staticmethod
    def get_hops(traceroute_result):
        hops = []
        for line in traceroute_result.split('\r\n'):
            hop = re.search(r"(\d)\s+([a-fA-F0-9\:]+)\s+\([a-fA-F0-9\:]+\)\s+([\d\.]+)\s?ms", line)
            if hop is not None:
                hops.append(hop.group(2))
        return(hops)

    @staticmethod
    def get_config():
        if Traceroute.config is None:
            with open('../config.json') as json_config:
                Traceroute.config = json.load(json_config)
        
        return Traceroute.config

    @staticmethod 
    def get_graph():
        if Traceroute.graph is None:
            Traceroute.graph = nx.Graph()
            for router in Traceroute.get_config()["routers"]:
                Traceroute.graph.add_node(int(router["id"]), name=router["name"], ip=router["ip"])
                for interface in router["interfaces"]:
                    if "connected-router" in interface:
                        Traceroute.graph.add_edge(int(router["id"]), interface["connected-router"], weight=interface["cost"])

        return Traceroute.graph

    @staticmethod
    def get_dns():
        if Traceroute.dns is None:
            Traceroute.dns = {}
            for router in Traceroute.get_config()["routers"]:
                Traceroute.dns[router['id']] = {
                    "id": router['id'],
                    "name": router['name'],
                    "ip": router['ip']
                }
                Traceroute.dns[router['name']] = {
                    "id": router['id'],
                    "name": router['name'],
                    "ip": router['ip']
                }
                Traceroute.dns[router['ip']] = {
                    "id": router['id'],
                    "name": router['name'],
                    "ip": router['ip']
                }
        # print(Traceroute.dns)
        return Traceroute.dns

    @staticmethod
    def get_path(source, dest):
        graph = Traceroute.get_graph()

        id_shortest_path = nx.shortest_path(graph, Traceroute.get_dns()[source]['id'], Traceroute.get_dns()[dest]['id'], weight='weight')

        ip_shortest_path = []
        name_shortest_path = []
        for id in id_shortest_path:
            if Traceroute.get_dns()[source]['id'] != Traceroute.dns[id]['id'] and Traceroute.get_dns()[dest]['id'] != Traceroute.dns[id]['id']:
                ip_shortest_path.append(Traceroute.dns[id]['ip'])
                name_shortest_path.append(Traceroute.dns[id]['name'])
        
        ip_shortest_path.append(Traceroute.dns[dest]['ip'])
        name_shortest_path.append(Traceroute.dns[dest]['name'])
        return ip_shortest_path, name_shortest_path

print("\nPerforming all the traceroutes.\n\nYou can find the logs in the following folder: /tests/logs/ROUTER_NAME.log")
Traceroute.traceroutes()

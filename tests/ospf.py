#! /usr/bin/env python3

import pexpect
import json
import os
import time
import re
import networkx as nx
import matplotlib.pyplot as plt

from random import randint
from Logger import Logger

# os.chdir("/home/vagrant/CampusNetwork/")
class OSPF:

    config = None
    graph = None
    dns = None

    @staticmethod
    def traceroutes():
        config = OSPF.get_config()
        dns = OSPF.get_dns()

        for router1 in config["routers"]:
            child = pexpect.spawn('sudo ../connect_to.sh project_config ' + router1["name"])
            child.expect("bash-4.3#")
            
            for router2 in config["routers"]:
                child.sendline('traceroute6 -q 1 ' + router2["ip"])
                time.sleep(1)
                child.expect("bash-4.3#")

                hops = OSPF.get_hops(child.before.decode('utf-8'))
                expected = OSPF.get_path(router1['ip'], router2['ip'])
                if hops != expected[0]:
                    Logger.get_logger(router1["name"]).warning('reached {router2} via {real_path} instead of {name_expected_path}'.format(
                        router2=router2["name"],
                        real_path=' -> '.join(map(lambda x: dns[x]['name'], hops)),
                        name_expected_path=' -> '.join(expected[1])
                    ))
                else:
                    Logger.get_logger(router1["name"]).info('reached {router2} via {real_path}'.format(
                        router2=router2["name"],
                        real_path=' -> '.join(map(lambda x: dns[x]['name'], hops))
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
        if OSPF.config is None:
            with open('../config.json') as json_config:
                OSPF.config = json.load(json_config)
        
        return OSPF.config

    @staticmethod 
    def get_graph() -> nx.Graph:
        if OSPF.graph is None:
            OSPF.graph = nx.Graph()
            for router in OSPF.get_config()["routers"]:
                OSPF.graph.add_node(int(router["id"]), name=router["name"], ip=router["ip"])
                for interface in router["interfaces"]:
                    if "connected-router" in interface:
                        OSPF.graph.add_edge(int(router["id"]), interface["connected-router"], weight=interface["cost"])

        return OSPF.graph

    @staticmethod
    def get_dns():
        if OSPF.dns is None:
            OSPF.dns = {}
            for router in OSPF.get_config()["routers"]:
                OSPF.dns[router['id']] = {
                    "id": router['id'],
                    "name": router['name'],
                    "ip": router['ip']
                }
                OSPF.dns[router['name']] = {
                    "id": router['id'],
                    "name": router['name'],
                    "ip": router['ip']
                }
                OSPF.dns[router['ip']] = {
                    "id": router['id'],
                    "name": router['name'],
                    "ip": router['ip']
                }
        return OSPF.dns

    @staticmethod
    def get_path(source, dest):
        graph = OSPF.get_graph()

        id_shortest_path = nx.shortest_path(graph, OSPF.get_dns()[source]['id'], OSPF.get_dns()[dest]['id'], weight='weight')

        ip_shortest_path = []
        name_shortest_path = []
        for id in id_shortest_path:
            if OSPF.get_dns()[source]['id'] != OSPF.dns[id]['id'] and OSPF.get_dns()[dest]['id'] != OSPF.dns[id]['id']:
                ip_shortest_path.append(OSPF.dns[id]['ip'])
                name_shortest_path.append(OSPF.dns[id]['name'])
        
        ip_shortest_path.append(OSPF.dns[dest]['ip'])
        name_shortest_path.append(OSPF.dns[dest]['name'])
        return ip_shortest_path, name_shortest_path

    @staticmethod
    def traceroutes_with_random_failures(amount=5):
        config = OSPF.get_config()
        graph = OSPF.get_graph()
        dns = OSPF.get_dns()

        for i in range(amount):
            interface, router1, router2 = OSPF.get_random_interface_link_pair()

            weight = graph[router1][router2]['weight']
            graph.remove_edge(router1, router2)

            child = pexpect.spawn('sudo ../connect_to.sh project_config ' + dns[router1]["name"])
            child.expect("bash-4.3#")
            child.sendline("ip link set dev " + interface + " down")
            child.expect("bash-4.3#")
            print("== Destroying interface "+ str(i+1)+"/"+str(amount) +": "+ interface, end='')
            for j in range(10):
                time.sleep(1)
                print(".", end='')
            print()

            OSPF.traceroutes()

            child = pexpect.spawn('sudo ../connect_to.sh project_config ' + dns[router1]["name"])
            child.expect("bash-4.3#")
            child.sendline("ip link set dev " + interface + " up")
            child.expect("bash-4.3#")
            print("== Reactivating interface "+ str(i+1)+"/"+str(amount) +": "+ interface, end='')
            for j in range(10):
                time.sleep(1)
                print(".", end='')
            print()

            graph.add_edge(router1, router2, weight=weight)



    @staticmethod
    def get_random_interface_link_pair():
        config = OSPF.get_config()
        routers = config["routers"]

        router1 = routers[randint(0, len(routers)-1)]
        
        rand_interface = randint(0, len(router1["interfaces"])-1)
        while not router1["interfaces"][rand_interface].get("ospf_active", False):
            rand_interface = randint(0, len(router1["interfaces"])-1)

        router1_interface = "{router}-eth{number}".format(router=router1["name"],number=router1["interfaces"][rand_interface]["number"])
        router2 = router1["interfaces"][rand_interface]["connected-router"]


        return router1_interface, router1["id"], router2

        
if __name__ == "__main__":
    print()
    print("## Running OSPF tests (without link failures) ##")
    print()

    OSPF.traceroutes()

    print()
    print('## OSPF tests (without link failures) finished ##')
    print()

    print()
    print("## Running OSPF tests (with random link failures) ##")
    print()

    OSPF.traceroutes_with_random_failures()

    print()
    print('## OSPF tests (with random link failures) finished ##')
    print()


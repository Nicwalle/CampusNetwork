#! /bin/sh
ldconfig

ip link set dev lo up
ip -6 addr add ${router["ip"]}/${router["subnet"]} dev lo

# Assigning IP addr for P1-eth0
% for eth_interface in router["interfaces"]:
ip link set dev ${router["name"]}-eth${eth_interface['number']} up
% if eth_interface.get("bgp_active", False):
ip -6 addr add ${eth_interface["bgp_address"]} dev ${router["name"]}-eth${eth_interface["number"]}
% endif
% endfor

# zebra is required to make the link between all FRRouting daemons
# and the linux kernel routing table
LD_LIBRARY_PATH=/usr/local/lib /usr/lib/frr/zebra -A 127.0.0.1 -f /etc/zebra.conf -z /tmp/${router["name"]}.api -i /tmp/${router["name"]}_zebra.pid --v6-rr-semantics &
# launching FRRouting OSPF daemon
LD_LIBRARY_PATH=/usr/local/lib /usr/lib/frr/ospf6d -f /etc/${router["name"]}_ospf.conf -z /tmp/${router["name"]}.api -i /tmp/${router["name"]}_ospf6d.pid -A 127.0.0.1 &
% if router.get("bgp", {}).get("active", False):
# launching FRRouting BGP daemon
LD_LIBRARY_PATH=/usr/local/lib /usr/lib/frr/bgpd -f /etc/${router["name"]}_bgpd.conf -z /tmp/${router["name"]}.api -i /tmp/${router["name"]}_bgpd.pid -A 127.0.0.1 &
% endif



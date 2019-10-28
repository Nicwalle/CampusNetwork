#! /bin/sh
ldconfig

ip link set dev lo up
ip -6 addr add ${router.ip}/${router.subnet} dev lo

# Assigning IP addr for P1-eth0
% for eth_interface in router.interfaces:
ip link set dev ${router.name}-eth${eth_interface['number']} up
% endfor

# zebra is required to make the link between all FRRouting daemons
# and the linux kernel routing table
LD_LIBRARY_PATH=/usr/local/lib /usr/lib/frr/zebra -A 127.0.0.1 -f /etc/zebra.conf -z /tmp/${router.name}.api -i /tmp/${router.name}_zebra.pid &
# launching FRRouting OSPF daemon
LD_LIBRARY_PATH=/usr/local/lib /usr/lib/frr/ospf6d -f /etc/${router.name}_ospf.conf -z /tmp/${router.name}.api -i /tmp/${router.name}_ospf6d.pid -A 127.0.0.1



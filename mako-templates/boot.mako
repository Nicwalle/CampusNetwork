#!/bin/bash

## Router behavior
sysctl -w net.ipv6.conf.all.forwarding=1
sysctl -w net.ipv6.conf.default.forwarding=1

## Create a new chain to log dropped files (normally due to DDoS attacks)
ip6tables -N LOGGINGLIMIT
## Log only twice per minute (so that we won't log a huge amount of packets in case of DDoS attacks)
## Those could be packets from a DDoS attacks or packets filtered due to a limit value (of packets, see rules below)
## which is too low for our network
ip6tables -A LOGGINGLIMIT -m limit --limit 2/min -j LOG --log-prefix "ip6tables - drop (limit): " --log-level 4
## Finally, drop them
ip6tables -A LOGGINGLIMIT -j DROP


## Filtering OSPF packets and BGP packets (before the connection is made) and filtering private IPv6 addresses
## Source for private IPv6 addresses : https://www.ripe.net/manage-ips-and-asns/ipv6/ipv6-address-types/ipv6addresstypes.pdf
% for interface in router["interfaces"]:
    % if interface.get("ospf_active", false):
        ## accept OSPFs (protocol number 89) packets coming from an interface linking the routers of our AS
        ip6tables -A INPUT -i ${router["name"]}-eth${interface["number"]} -p 89 -j ACCEPT
    % else:
        ## this interface is linked to an external peer, to another AS

        ## drop the OSPF packets that another AS wants to forward through one of our routers
        ip6tables -A FORWARD -i ${router["name"]}-eth${interface["number"]} -p 89 -j DROP
        ## drop BGP packets (BGP : TCP on port 179) that we are asked to forward
        ip6tables -A FORWARD -i ${router["name"]}-eth${interface["number"]} -p tcp --destination-port 179 -j DROP

        ## Authorize a limited amount of connections per second
        ip6tables -A INPUT -i ${router["name"]}-eth${interface["number"]} -j ACCEPT -m limit --limit 30/s --limit-burst 30
        ip6tables -A FORWARD -i ${router["name"]}-eth${interface["number"]} -j ACCEPT -m limit --limit 30/s --limit-burst 30
        ## Deny external packets when the limit is reached
        ip6tables -A INPUT -i ${router["name"]}-eth${interface["number"]} -j LOGGINGLIMIT
        ip6tables -A FORWARD -i ${router["name"]}-eth${interface["number"]} -j LOGGINGLIMIT
    % endif
% endfor

ip6tables -A INPUT -p 89 -j DROP ## drop OSPF packets by default


## -------- Private addresses filtering for the addresses we are not using for the moment :

## Create a new chain to log packets which we are dropping because of the rules described in the report
ip6tables -N LOGGINGPRIVATE
## Log only twice per minute (so that we won't log a huge amount of packets in case of DDoS attacks)
## Those could be packets from a DDoS attacks or packets filtered due to a limit value (of packets, see rules below)
## which is too low for our network
ip6tables -A LOGGINGPRIVATE -m limit --limit 2/min -j LOG --log-prefix "ip6tables - drop (private addr): " --log-level 4
## Finally, drop them
ip6tables -A LOGGINGPRIVATE -j DROP

## Unspecified, may only be used as a source addr by an initialising host before it has learned its own address 
ip6tables -A FORWARD -d ::/128 -j LOGGINGPRIVATE

## Benchmarking addresses
ip6tables -A INPUT -s 2001:0002::/48 -j LOGGINGPRIVATE 
ip6tables -A FORWARD -s 2001:0002::/48 -j LOGGINGPRIVATE 
ip6tables -A INPUT -d 2001:0002::/48 -j LOGGINGPRIVATE 
ip6tables -A FORWARD -d 2001:0002::/48 -j LOGGINGPRIVATE 

## Orchid addresses
ip6tables -A INPUT -s 2001:0010::/28 -j LOGGINGPRIVATE 
ip6tables -A FORWARD -s 2001:0010::/28 -j LOGGINGPRIVATE 
ip6tables -A INPUT -d 2001:0010::/28 -j LOGGINGPRIVATE 
ip6tables -A FORWARD -d 2001:0010::/28 -j LOGGINGPRIVATE 

## Documentation addresses
ip6tables -A INPUT -s 2001:db8::/32 -j LOGGINGPRIVATE 
ip6tables -A FORWARD -s 2001:db8::/32 -j LOGGINGPRIVATE 
ip6tables -A INPUT -d 2001:db8::/32 -j LOGGINGPRIVATE 
ip6tables -A FORWARD -d 2001:db8::/32 -j LOGGINGPRIVATE 

## Multicast addresses, should never be used as source addresses
ip6tables -A INPUT -s ff00::/8 -j LOGGINGPRIVATE 
ip6tables -A FORWARD -s ff00::/8 -j LOGGINGPRIVATE

## -------- End of private addresses filtering for the addresses we are not using for the moment :

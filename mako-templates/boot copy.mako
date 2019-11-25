#!/bin/bash

## Router behavior
sysctl -w net.ipv6.conf.all.forwarding=1
sysctl -w net.ipv6.conf.default.forwarding=1

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
        ip6tables -A FORWARD -i ${router["name"]}-eth${interface["number"]} -p tcp --destination-port 179

        ## Link-Local Addresses should not be received from other ASes
        ip6tables -A INPUT -i ${router["name"]}-eth${interface["number"]} -s fe80::/10 -j DROP
        

    % endif
% endfor

ip6tables -A INPUT -p 89 -j DROP ## drop OSPF packets by default


## -------- Private addresses filtering for the addresses we are not using for the moment :

## Unspecified, may only be used as a source addr by an initialising host before it has learned its own address 
ip6tables -A FORWARD -d ::/128 -j DROP

## ULAs, not public address space, should be forwarded and shouldn't be the source or destination address
ip6tables -A INPUT -s fc00::/7 -j DROP 
ip6tables -A FORWARD -s fc00::/7 -j DROP 
ip6tables -A INPUT -d fc00::/7 -j DROP 
ip6tables -A FORWARD -d fc00::/7 -j DROP 

## Benchmarking addresses
ip6tables -A INPUT -s 2001:0002::/48 -j DROP 
ip6tables -A FORWARD -s 2001:0002::/48 -j DROP 
ip6tables -A INPUT -d 2001:0002::/48 -j DROP 
ip6tables -A FORWARD -d 2001:0002::/48 -j DROP 

## Orchid addresses
ip6tables -A INPUT -s 2001:0010::/28 -j DROP 
ip6tables -A FORWARD -s 2001:0010::/28 -j DROP 
ip6tables -A INPUT -d 2001:0010::/28 -j DROP 
ip6tables -A FORWARD -d 2001:0010::/28 -j DROP 

## Documentation addresses
ip6tables -A INPUT -s 2001:db8::/32 -j DROP 
ip6tables -A FORWARD -s 2001:db8::/32 -j DROP 
ip6tables -A INPUT -d 2001:db8::/32 -j DROP 
ip6tables -A FORWARD -d 2001:db8::/32 -j DROP 

## Multicast addresses, should never be used as source addresses
ip6tables -A INPUT -s ff00::/8 -j DROP 
ip6tables -A FORWARD -s ff00::/8 -j DROP

## -------- End of private addresses filtering for the addresses we are not using for the moment :

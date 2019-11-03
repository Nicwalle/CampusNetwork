! -*- bgp -*-
!
! BGP configuration file
!
hostname bgpd
password zebra
!
router bgp ${as_number}
bgp router-id 1.${router["id"]}.${router["id"]}.${router["id"]}

% for bgp_neighbor in router["bgp"]["neighbors"]:
neighbor ${bgp_neighbor["ip"]} remote-as ${bgp_neighbor["as_number"]}
% endfor

address-family ipv6 unicast
% for bgp_neighbor in router["bgp"]["neighbors"]:
neighbor ${bgp_neighbor["ip"]} activate
% for bgp_neighbor_prefix in bgp_neighbor["prefixes"]:
network ${bgp_neighbor_prefix}
% endfor
% endfor
exit-address-family
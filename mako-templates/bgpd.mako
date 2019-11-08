! -*- bgp -*-
!
! BGP configuration file
!
hostname bgpd
password zebra
!
router bgp ${as_number}
bgp router-id 1.${router["id"]}.${router["id"]}.${router["id"]}
no bgp default ipv4-unicast

% for bgp_neighbor in router["bgp"]["neighbors"]:
! 
    neighbor ${bgp_neighbor["ip"]} remote-as ${bgp_neighbor["as_number"]}
    % if bgp_neighbor["type"] == "external":
    neighbor ${bgp_neighbor["ip"]} interface ${router["name"]}-eth${bgp_neighbor["interface-number"]}
    % endif

    address-family ipv6 unicast
        neighbor ${bgp_neighbor["ip"]} activate
        % if bgp_neighbor["type"] == "internal":
        neighbor ${bgp_neighbor["ip"]} next-hop-self
        % if bgp_neighbor.get("relationship", "dontcare") == "client":
        neighbor ${bgp_neighbor["ip"]} route-reflector-client
        % endif
        neighbor ${bgp_neighbor["ip"]} update-source ${router["ip"]}
        % else:
        % for bgp_neighbor_prefix in bgp_neighbor["prefixes"]:
        network ${bgp_neighbor_prefix}
        % endfor 
        % endif
    exit-address-family
% endfor

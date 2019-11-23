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


!% if router["community"] == "main":
!bgp community-list standard ${router["community"]} permit 65001:110
!% elif router["community"] == "backup":
!bgp community-list standard ${router["community"]} permit 65001:10
!% endif

% for bgp_neighbor in router["bgp"]["neighbors"]:
! 
    
    
    neighbor ${bgp_neighbor["ip"]} remote-as ${bgp_neighbor["as_number"]}
    % if bgp_neighbor.get("MD5_password", "dontcare") != "dontcare":
        neighbor ${bgp_neighbor["ip"]} password 7 ${bgp_neighbor["MD5_password"]}
    % endif
    % if bgp_neighbor["type"] == "external":
        neighbor ${bgp_neighbor["ip"]} interface ${router["name"]}-eth${bgp_neighbor["interface-number"]}
    %endif
    
    

    address-family ipv6 unicast
        neighbor ${bgp_neighbor["ip"]} activate
        % if bgp_neighbor["type"] == "internal":
            neighbor ${bgp_neighbor["ip"]} next-hop-self
            % if bgp_neighbor.get("relationship", "dontcare") == "client":
            neighbor ${bgp_neighbor["ip"]} route-reflector-client
            % endif
            neighbor ${bgp_neighbor["ip"]} update-source ${router["ip"]}
        % elif bgp_neighbor["type"] == "external":
            % for bgp_neighbor_prefix in bgp_neighbor["prefixes"]:
                network ${bgp_neighbor_prefix}
            % endfor 
            !% if bgp_neighbor["input-whitelist"] != []:
            !    neighbor ${bgp_neighbor["ip"]} prefix-list ${bgp_neighbor["relationship"]}-${bgp_neighbor["as_number"]}-in in
            !% endif
            
            !% if bgp_neighbor["output-whitelist"] != []:
            !    neighbor ${bgp_neighbor["ip"]} prefix-list ${bgp_neighbor["relationship"]}-${bgp_neighbor["as_number"]}-out out
            !%endif
        % endif

    exit-address-family

    % if bgp_neighbor["type"] == "external":
       % for output_ip in bgp_neighbor["output-whitelist"]:
            ip prefix-list ${bgp_neighbor["relationship"]}-${bgp_neighbor["as_number"]}-out permit ${output_ip}
        % endfor

        % for input_ip in bgp_neighbor["input-whitelist"]:
            ip prefix-list ${bgp_neighbor["relationship"]}-${bgp_neighbor["as_number"]}-in permit ${input_ip}
        % endfor
    % endif
% endfor


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
    % if bgp_neighbor.get("MD5_password", "dontcare") != "dontcare":
        neighbor ${bgp_neighbor["ip"]} password ${bgp_neighbor["MD5_password"]}
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
            % if bgp_neighbor["input-whitelist"] != []:
                neighbor ${bgp_neighbor["ip"]} prefix-list ${bgp_neighbor["relationship"]}-${bgp_neighbor["as_number"]}-in in
            % endif
            % if bgp_neighbor["output-whitelist"] != []:
                neighbor ${bgp_neighbor["ip"]} prefix-list ${bgp_neighbor["relationship"]}-${bgp_neighbor["as_number"]}-out out
            %endif

            % if  bgp_neighbor.get("community", "dontcare") != "dontcare":
                neighbor ${bgp_neighbor["ip"]} route-map ${bgp_neighbor["community"]} in
            % endif
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

    bgp community-list standard garbage permit 64512:100
    bgp community-list standard customer permit 101:1
    bgp community-list standard provider permit 101:2
    bgp community-list standard sharedCost permit 101:3
    !
    route-map garbage permit 10
        set ip next-hop ::1
        set local-preference 5
        set community additive no-export
    route-map  garbage permit 20
    !
    route-map customer permit 10
        call rm-community-in
        on-match next
    route-map customer permit 20
        set local-preference 100
    route-map customer permit 30
    !
    route-map rm-community-in permit 10
        match community garbage
        call garbage
    route-map rm-community-in permit 20
    !
    route-map provider permit 10
        set local-preference 10
    route-map provider permit 20
    !
    route-map sharedCost permit 10
        set local-preference 50
    route-map sharedCost permit 20
    !


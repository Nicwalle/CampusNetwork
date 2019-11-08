!
! OSPF configuration for ${router["name"]}
!
hostname ${router["name"]}
password zebra
log stdout
service advanced-vty
!
debug ospf6 neighbor state
!
interface lo
    ipv6 ospf6 cost 1
    ipv6 ospf6 hello-interval 10
    ipv6 ospf6 dead-interval 40
    ipv6 ospf6 instance-id 0
!
% for eth_interface in router["interfaces"]:
interface ${router["name"]}-eth${eth_interface['number']}
    ipv6 ospf6 cost ${eth_interface['cost']}
    % if eth_interface.get('ospf_active', False):
    ipv6 ospf6 hello-interval ${eth_interface['hello-time']}
    ipv6 ospf6 dead-interval ${eth_interface['dead-time']}
    % else:
    ipv6 ospf6 passive
    % endif
    ipv6 ospf6 instance-id ${eth_interface['instance-id']}
!
% endfor
router ospf6
    ospf6 router-id 1.${router["id"]}.${router["id"]}.${router["id"]}
    interface lo area 0.0.0.0
    % for eth_interface in router["interfaces"]:
    % if eth_interface.get('ospf_active', False):
    interface ${router["name"]}-eth${eth_interface['number']} area ${eth_interface['area']}
    % endif
    % endfor
!
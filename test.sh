cd tests

echo "#################################################"
echo "#                                               #"
echo "#            STARTING NETWORK TESTS             #"
echo "# you can find the logs in the following folder #"
echo "#          /tests/logs/ROUTER_NAME.log          #"
echo "#                                               #"
echo "#################################################"

python3 ping.py

python3.6 ospf.py

python3.6 bgp.py
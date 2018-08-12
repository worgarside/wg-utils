#!/bin/bash

INITIAL_IP="$(wget http://ipinfo.io/ip -qO -)"

{
  sudo -b openvpn --config /etc/openvpn/config.ovpn --auth-user-pass /etc/openvpn/login.txt
} &> /dev/null

wait

VPN_IP="$(wget http://ipinfo.io/ip -qO -)"

if [ "$INITIAL_IP" = "$VPN_IP" ] 
then
	echo "IP address is unchanged @ $INITIAL_IP. Possible failure. "
else
	echo "VPN connected @ $VPN_IP. Starting Deluge daemon and webUI"
	deluged
	wait
	deluge-web
	echo "Complete"
fi



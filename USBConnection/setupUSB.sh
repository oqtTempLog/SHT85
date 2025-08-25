#!/bin/bash

nmcli | grep -q enx
if [ $? -eq 1 ]; then
	echo "mist"
else
	DEV_USB=$(nmcli | grep enx | awk '{print substr($1, 1, length($1)-1); exit}')
	DEV_WAN=$(ip -4 route get 8.8.8.8 | awk '{print $5; exit}')
	
	ip addr flush dev "$DEV_USB"
	ip addr add 192.168.4.1/24 dev "$DEV_USB"
	echo 1 >> /proc/sys/net/ipv4/ip_forward
	nft flush ruleset
	nft add table ip nat
	nft add chain ip nat postrouting '{ type nat hook postrouting priority 100; }'
	nft add rule ip nat postrouting oifname "$DEV_WAN" masquerade
	nft add table inet filter
	nft add chain inet filter forward '{ type filter hook forward priority 0; }'
	nft add rule inet filter forward ct state established,related accept
	nft add rule inet filter forward iifname "$DEV_USB" oifname "$DEV_WAN" accept
fi

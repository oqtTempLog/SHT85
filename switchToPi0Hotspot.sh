#!/bin/bash

nmcli connection show --active | grep -q "Wi-Fi to pi0 hotspot"
if [ $? -eq 0 ]; then
	echo "Already connected to pi."
else
	nmcli device wifi list --rescan yes | grep -q "pi0hotspot"
	if [ $? -eq 0 ]; then
		echo "pi0 hotspot available. Connect to pi0..."
		nmcli connection up "Wi-Fi to pi0 hotspot"
	else
		echo "pi0 hotspot not available."
	fi
	
fi
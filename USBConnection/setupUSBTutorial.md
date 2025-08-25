# Setting up a USB connection between Raspi and Computer

Pi
/boot/firmware/config.txt: 
+ remove otg_mode=1 (in [cm4])
+ remove dtoverlay=dwc2,dr_mode=host (in [cm5])
+ add dtoverlay=dwc2 in [all]

/boot/firmware/cmdline.txt:
add modules-load=dwc2,g_ether after rootwait

create new NetworkProfile for the usb connection:
go to /etc/NetworkManager/system-connections, create a file called usb0.nmconnection and add the following content:

```
[connection]
id=usb0
uuid=c6dc7c01-038c-4188-8a0e-3aeafe069865
type=ethernet
interface-name=usb0

[ethernet]

[ipv4]
address1=192.168.4.11/24,192.168.4.1
dns=8.8.8.8;
method=manual

[ipv6]
addr-gen-mode=default
method=auto

[proxy]
```

Bring up this network via nmcli connection up usb0. To bring it up automatically at boot-time, go to /etc/systemd/system/, create a new file called nm-usb0.service and copy/paste the following:

```
[Unit]
Description=Bring up usb0 with nmcli
After=network.target NetworkManager.service
Requires=NetworkManager.service

[Service]
Type=oneshot
ExecStart=/usr/bin/nmcli connection up usb0
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Next, enable this newly created service via sudo systemctl enable nm-usb0.service
Finally, reboot the pi.

Laptop
plug in the pi via usb and run the setupUSB.sh script (with root privileges).

# Using SSH via USB connection between Raspi and Computer

On the Pi, go to `/boot/firmware/config.txt` and
+ remove `otg_mode=1` (in `[cm4]`)
+ remove `dtoverlay=dwc2,dr_mode=host` (in `[cm5]`)
+ add `dtoverlay=dwc2` in `[all]`

Next, open `/boot/firmware/cmdline.txt` and insert `modules-load=dwc2,g_ether` after `rootwait`.

Create a new network profile for the usb connection using the NetworkManager:
Go to `/etc/NetworkManager/system-connections`, create a file called `usb0.nmconnection` and add the following content (instead of `192.168.4.11` you can use any IP address of the form `192.168.4.x`, do not change the gateway address `192.168.4.1`):

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

Bring up the newly created interface via `nmcli connection up usb0`. To bring it up automatically at boot-time, go to `/etc/systemd/system/`, create a new file called `nm-usb0.service` and copy/paste the following:

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

Next, enable this newly created service via `sudo systemctl enable nm-usb0.service`.
Finally, reboot the pi.

Plug a USB cable into the Pis USB and into your laptop (attention: there are USB cables that are made only for charging, we need a cable that also supports data transfer). Run the `setupUSB.sh` script (with root privileges). You should then be able to ssh into the Pi (via `ssh username@192.168.4.x`).

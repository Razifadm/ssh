### Too many bugs.##

## SSH over WebSocket Setup (OpenWrt)

### Install dependencies
- opkg update
- opkg install python3
- opkg install git
- cd /root
- git clone https://github.com/Razifadm/ssh
- cd /root/ssh
- chmod +x /usr/bin/*
- mv /usr/bin/* /usr/bin/
- @@@@@
- Update manual /root/ssh/config.py
- and ssh_connector.py

### Run
-radu


 
Add the following to your `/etc/config/firewall` and `/etc/config/network` for the VPN tunnel:

### `/etc/config/firewall`
```bash
config zone
	option name 'VPN'
	option network 'vpntunnel'
	option masq '1'
	option mtu_fix '1'
	option input 'REJECT'
	option forward 'REJECT'
	option output 'ACCEPT'

config forwarding
	option src 'lan'
	option dest 'VPN'
````

### `/etc/config/network`

```bash
config interface 'vpntunnel'
	option proto 'none'
	option device 'tun1'
```
 

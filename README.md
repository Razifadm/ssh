## SSH over WebSocket Setup (OpenWrt)

### Go to /root and clone the repo
- cd /root
- git clone https://github.com/dotywrt/SSH-WebSocket.git ssh

### Install dependencies
- opkg update
- opkg install python3
- chmod +x /root/ssh/usr/bin/*
- mv /root/ssh/usr/bin/* /usr/bin/
- Update /root/ssh/config.py

### Run
- cd /root/ssh
- python3 main.py

 
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
 

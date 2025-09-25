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

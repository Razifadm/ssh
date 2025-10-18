#!/bin/sh
#Install command, dependency wajib
opkg update
opkg install python3
opkg install git
cd /root

#copy download source code
git clone https://github.com/Razifadm/ssh
cd /root/ssh

#chmod bin wajib dan pindah bin ke direktori
chmod +x /usr/bin/*
mv /usr/bin/* /usr/bin/

#padam skripp terclone
rm -f /root/ssh/Install.sh

#padam skrip Install.sh
rm -f "$0"

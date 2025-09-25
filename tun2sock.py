#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import signal
 
TUN_DEV = "tun1"
TUN_ADDRESS = "10.0.0.2"
TUN_GATEWAY = "10.0.0.1"
TUN_NETMASK = "255.255.255.0"
TUN_MTU = 1420
SOCKS_SERVER = "127.0.0.1:1080"
UDPGW_SERVER = "127.0.0.1:7300"

ROUTE_LOG = "/root/ssh/log/tun2socks-route.log"

tun2socks_process = None


def init_tun_dev():
    os.system(f"ip link del dev {TUN_DEV} 2>/dev/null")
    os.system(f"ip tuntap add dev {TUN_DEV} mode tun")
    os.system(f"ip link set dev {TUN_DEV} mtu {TUN_MTU} up")
    print("Tun device initialized")


def destroy_tun_dev():
    os.system(f"ip link set dev {TUN_DEV} down")
    os.system(f"ip tuntap del dev {TUN_DEV} mode tun")
    print("Tun device removed")


def start_tun2socks():
    global tun2socks_process
    os.system(f"ifconfig {TUN_DEV} {TUN_GATEWAY} netmask {TUN_NETMASK} up")

    cmd = [
        "badvpn-tun2socks",
        "--loglevel", "0",
        "--tundev", TUN_DEV,
        "--netif-ipaddr", TUN_ADDRESS,
        "--netif-netmask", TUN_NETMASK,
        "--socks-server-addr", SOCKS_SERVER,
        "--udpgw-remote-server-addr", UDPGW_SERVER
    ]

    tun2socks_process = subprocess.Popen(cmd)

    default_route = os.popen("ip route show | grep default").read().strip()
    with open(ROUTE_LOG, "w") as f:
        f.write(default_route)

    os.system("ip route del " + default_route)
    os.system(f"ip route add default via {TUN_ADDRESS} metric 6")

    print("Tun2socks started")


def stop_tun2socks():
    global tun2socks_process
    if tun2socks_process:
        tun2socks_process.terminate()
        tun2socks_process.wait()

    if os.path.exists(ROUTE_LOG):
        with open(ROUTE_LOG) as f:
            default_route = f.read().strip()
        os.system(f"ip route add {default_route}")
        os.remove(ROUTE_LOG)

    os.system(f"ip route del default via {TUN_ADDRESS} metric 6")
    print("Tun2socks stopped")


def cleanup(signum=None, frame=None):
    stop_tun2socks()
    destroy_tun_dev()
    sys.exit(0)


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("This script must be run as root")
        sys.exit(1)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    init_tun_dev()
    start_tun2socks()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()

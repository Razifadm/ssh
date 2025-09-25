import time
from config import CONFIG
from tunnel_strategies import get_strategy
from ssh_connector import connect_via_ws_and_start_socks


def main():
    try:
        strategy_cls = get_strategy(CONFIG['MODE'])
        ws_sock = strategy_cls(CONFIG).establish()
 
        print("[*] Testing WebSocket connection...")
        try:
            ws_sock.settimeout(5)
            test_data = ws_sock.recv(1024)
            if test_data:
                print(f"[*] Received data through tunnel: {test_data[:100]}")
            ws_sock.settimeout(None)
        except socket.timeout:
            print("[*] No immediate data, but connection seems alive")
        except Exception as e:
            print(f"[!] WebSocket test failed: {e}")

        ssh_connection = connect_via_ws_and_start_socks(
            ws_socket=ws_sock,
            ssh_user=CONFIG['SSH_USERNAME'],
            ssh_password=CONFIG['SSH_PASSWORD'],
            ssh_port=int(CONFIG['SSH_PORT']),
            local_socks_port=int(CONFIG['LOCAL_SOCKS_PORT']),
        )

        print(f"[+] SOCKS proxy up on 127.0.0.1:{CONFIG['LOCAL_SOCKS_PORT']}")
        print("[+] All traffic through that proxy is forwarded over SSH via WS tunnel.")

        while True:
            time.sleep(1) 
            if not ssh_connection.keep_running:
                print("[!] SSH tunnel died, exiting...")
                break

    except KeyboardInterrupt:
        print("[*] Shutting down (KeyboardInterrupt).")
    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()

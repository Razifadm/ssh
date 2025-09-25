import socket
import threading
import struct
import subprocess
import select
import os
import time

class SSHOverWebSocketWithSSHPass:
 
    def __init__(self, ws_socket, ssh_username, ssh_password, ssh_host="localhost", ssh_port=22):
        self.ws_socket = ws_socket
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_process = None
        self.keep_running = True

    def start_ssh_transport(self):
 
        try: 
            print("[*] Starting SSH tunnel via sshpass...")
             
            cmd = [
                'sshpass', '-p', self.ssh_password,
                'ssh', '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'LogLevel=ERROR',
                '-o', 'BatchMode=yes',
                '-p', str(self.ssh_port),
                f'{self.ssh_username}@{self.ssh_host}',
                '-N',  # No command execution
                '-D', '1080'  # Dynamic SOCKS proxy
            ]
            
            print(f"[*] Command: {' '.join(cmd)}")
             
            self.ssh_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0
            )
             
            def monitor_stderr():
                while self.keep_running:
                    try:
                        line = self.ssh_process.stderr.readline()
                        if line:
                            print(f"[SSH stderr] {line.decode().strip()}")
                        time.sleep(0.1)
                    except:
                        break
            
            stderr_thread = threading.Thread(target=monitor_stderr, daemon=True)
            stderr_thread.start()
            
            print("[*] SSH process started")
            
        except Exception as e:
            print(f"[!] Failed to start SSH: {e}")
            raise

    def bidirectional_forward(self, sock1, sock2): 
        try:
            while self.keep_running: 
                rlist, _, xlist = select.select([sock1, sock2], [], [sock1, sock2], 1.0)
                
                if xlist:
                    break
                    
                for sock in rlist:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            return
                            
                        if sock is sock1:
                            sock2.send(data)
                        else:
                            sock1.send(data)
                    except (socket.error, OSError):
                        return
        except:
            pass
        finally:
            try:
                sock1.close()
            except:
                pass
            try:
                sock2.close()
            except:
                pass

    def open_socks_proxy(self, local_port):
 
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('0.0.0.0', local_port))
        server.listen(100)
        print(f"[*] SOCKS proxy listening on 127.0.0.1:{local_port}")

        def handle_socks_client(client_sock):
            try: 
                print("[*] New SOCKS connection, forwarding through WebSocket...")
                 
                self.bidirectional_forward(client_sock, self.ws_socket)
                
            except Exception as e:
                print(f"[!] SOCKS client error: {e}")
                try:
                    client_sock.close()
                except:
                    pass

        def accept_loop():
            while self.keep_running:
                try:
                    client_sock, addr = server.accept()
                    print(f"[*] New connection from {addr}")
                    threading.Thread(target=handle_socks_client, 
                                   args=(client_sock,), daemon=True).start()
                except socket.error:
                    break

        threading.Thread(target=accept_loop, daemon=True).start()
        print("[*] SOCKS proxy started")

    def close(self): 
        self.keep_running = False
        if self.ssh_process:
            self.ssh_process.terminate()
            self.ssh_process.wait()
        if hasattr(self, 'ws_socket'):
            try:
                self.ws_socket.close()
            except:
                pass
 
class SimpleSSHWebSocketTunnel:
    def __init__(self, ws_socket, ssh_user, ssh_password, ssh_host, ssh_port=22):
        self.ws_socket = ws_socket
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.ssh_host = ssh_host  
        self.ssh_port = ssh_port
        self.keep_running = True

    def start(self): 
        print("[*] Starting simple WebSocket-SSH tunnel...")
         
        cmd = [
            'sshpass', '-p', self.ssh_password,
            'ssh', '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'LogLevel=ERROR',
            '-N',  
            '-D', '1080',   
            f'{self.ssh_user}@{self.ssh_host}',
            '-p', str(self.ssh_port)
        ]
        
        print(f"[*] SSH command: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
             
            def monitor_ssh():
                while self.keep_running:
                    line = process.stderr.readline()
                    if line:
                        print(f"[SSH] {line.decode().strip()}")
                    if process.poll() is not None:
                        print("[!] SSH process terminated")
                        self.keep_running = False
                        break
                    time.sleep(0.1)
            
            threading.Thread(target=monitor_ssh, daemon=True).start()
             
            time.sleep(2)
             
            if process.poll() is not None:
                print("[!] SSH failed to start")
                return
                
            print("[+] SSH tunnel established successfully")
            
        except Exception as e:
            print(f"[!] Error starting SSH: {e}")

    def bidirectional_forward(self, sock1, sock2): 
        def forward(src, dst):
            try:
                while self.keep_running:
                    data = src.recv(4096)
                    if not data:
                        break
                    dst.send(data)
            except:
                pass
        
        t1 = threading.Thread(target=forward, args=(sock1, sock2), daemon=True)
        t2 = threading.Thread(target=forward, args=(sock2, sock1), daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

def connect_via_ws_and_start_socks(ws_socket, ssh_user, ssh_password, ssh_port, local_socks_port):
 
    connector = SimpleSSHWebSocketTunnel(
        ws_socket, 
        ssh_user, 
        ssh_password, 
        "shin.dotycat.my",  ## realhostt boskuu hahah
        ssh_port
    )
     
    def start_tunnel():
        try:
            connector.start()
        except Exception as e:
            print(f"[!] Tunnel error: {e}")
    
    tunnel_thread = threading.Thread(target=start_tunnel, daemon=True)
    tunnel_thread.start()
     
    time.sleep(3)
    
    return connector
 
def debug_websocket_connection(ws_socket): 
    print("[*] Debugging WebSocket data...")
    ws_socket.settimeout(2.0)
    try:
        data = ws_socket.recv(1024)
        if data:
            print(f"First bytes: {data[:50]}") 
    except socket.timeout:
        print("[*] No immediate data")
    except Exception as e:
        print(f"[!] Debug error: {e}")
    ws_socket.settimeout(None)

CONFIG = {
    'MODE': 'http_payload',                   # MOD -   direct | http_payload | sni_fronted
    'FRONT_DOMAIN': '',                       # SNI IF USE TLS/sni_fronted
    'LOCAL_SOCKS_PORT': '1080',               # DEFAULT SOCKS / TUNE PORT
 
    'PROXY_HOST': 'bug.com', # BUG REVEST HOST AS PROXY & REVEST HOST
    'PROXY_PORT': '80',                                                  # PROXY PORT
 
    'TARGET_HOST': 'shin.dotycat.my',          # REAL HOST
    'TARGET_PORT': '80',                       # WS PORT
    'SSH_USERNAME': 'user',                     # USER
    'SSH_PASSWORD': 'pass',                       # PASS
    'SSH_PORT': '22',                       # SSH PORT
    'PAYLOAD_TEMPLATE': (
        "GET / HTTP/1.1[crlf]Host: shin.dotycat.my[crlf]Upgrade: websocket[crlf][crlf]"
    ),
}

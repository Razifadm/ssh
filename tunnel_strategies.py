from __future__ import annotations

import socket
import ssl
from abc import ABC, abstractmethod
from typing import Dict

from ws_tunnel import establish_ws_tunnel


class TunnelStrategy(ABC):
    def __init__(self, cfg: Dict): 
        self.cfg = cfg

    @abstractmethod
    def establish(self) -> socket.socket:   # pragma: no cover
 
        raise NotImplementedError

 

class DirectStrategy(TunnelStrategy):
    def establish(self) -> socket.socket:
        return socket.create_connection(
            (self.cfg["TARGET_HOST"], self.cfg["TARGET_PORT"])
        )


class HttpPayloadStrategy(TunnelStrategy):
    def establish(self) -> socket.socket:
        return establish_ws_tunnel(
            proxy_host=self.cfg["PROXY_HOST"],
            proxy_port=self.cfg["PROXY_PORT"],
            target_host=self.cfg["TARGET_HOST"],
            target_port=self.cfg["TARGET_PORT"],
            payload_template=self.cfg["PAYLOAD_TEMPLATE"],
            use_tls=False,
        )


class SNIFrontedStrategy(TunnelStrategy):
    def establish(self) -> socket.socket: 
        raw_sock = socket.create_connection(
            (self.cfg["PROXY_HOST"], self.cfg["PROXY_PORT"])
        )
        ctx = ssl.create_default_context()
        tls_sock = ctx.wrap_socket(
            raw_sock,
            server_hostname=(
                self.cfg.get("FRONT_DOMAIN") or self.cfg["PROXY_HOST"]
            ),
        )
 
        return establish_ws_tunnel(
            proxy_host=self.cfg["PROXY_HOST"],
            proxy_port=self.cfg["PROXY_PORT"],
            target_host=self.cfg["TARGET_HOST"],
            target_port=self.cfg["TARGET_PORT"],
            payload_template=self.cfg["PAYLOAD_TEMPLATE"],
            sock=tls_sock,         # Re-use the already-encrypted socket
            use_tls=False,         # Don’t double-wrap
        )

 

def get_strategy(mode: str) -> type[TunnelStrategy]:
    """
    Map CONFIG['MODE'] to its Strategy class.

    >>> strategy_cls = get_strategy("sni_fronted")
    >>> tunnel = strategy_cls(cfg).establish()
    """
    table = {
        "direct":       DirectStrategy,
        "http_payload": HttpPayloadStrategy,
        "sni_fronted":  SNIFrontedStrategy,
    }
    try:
        return table[mode.lower()]
    except KeyError:
        valid = ", ".join(table.keys())
        raise ValueError(f"Unknown MODE '{mode}'. Valid choices: {valid}")

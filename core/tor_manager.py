import requests
import time
import socks
import socket
from stem import Signal
from stem.control import Controller

TOR_SOCKS_PORT = 9050
TOR_CONTROL_PORT = 9051
TOR_PASSWORD = ""  # Set in torrc, or leave empty if no password

class TorManager:
    def __init__(self):
        # Configure global SOCKS proxy
        socks.setdefaultproxy(socks.SOCKS5, "127.0.0.1", TOR_SOCKS_PORT)
        socket.socket = socks.socksocket

    def get_ip(self):
        """Returns the current exit node IP (useful for debugging)."""
        try:
            r = requests.get("https://api.ipify.org?format=json", timeout=8)
            return r.json().get("ip")
        except Exception:
            return None

    def renew_identity(self):
        """Sends NEWNYM to Tor (get a new identity/exit node)."""
        try:
            with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
                controller.authenticate(password=TOR_PASSWORD)
                controller.signal(Signal.NEWNYM)
            time.sleep(3)  # Tor needs 2–3 seconds to build a new circuit
            return True
        except Exception:
            return False

    def request(self, url, timeout=15, headers=None):
        """Requests a URL through Tor."""
        try:
            return requests.get(url, timeout=timeout, headers=headers)
        except Exception as e:
            return None

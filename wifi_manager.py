import subprocess
import time
import threading
  

class WiFiManager:
    def __init__(self):
        # Verify NetworkManager is installed and running
        self._check_nm_service()

    def _check_nm_service(self):
        """Ensure NetworkManager is active"""
        result = subprocess.run(
            ["systemctl", "is-active", "NetworkManager"],
            capture_output=True,
            text=True
        )
        if result.stdout.strip() != "active":
            raise RuntimeError("NetworkManager service not running")

    def scan_networks(self) -> list:
        """Scan for available WiFi networks"""
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,SECURITY,SIGNAL", "device", "wifi", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        networks = []
        for line in result.stdout.splitlines():
            ssid, security, signal = line.split(":")
            networks.append({
                "ssid": ssid,
                "secured": security != "",
                "security": security if security else "Open",
                "signal": int(signal)
            })
        
        return networks
    
    
    def connect_to_network(self, ssid, password, callback):
            """Run in background thread"""
            def _connect():
                try:
                    cmd = ["nmcli", "device", "wifi", "connect", ssid]
                    if password:
                        cmd += ["password", password]
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        callback(True, "Connected successfully")
                    else:
                        callback(False, result.stderr)
                except Exception as e:
                    callback(False, str(e))
            
            threading.Thread(target=_connect, daemon=True).start()


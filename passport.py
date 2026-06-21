import asyncio
import json
import socket

class WorkPassportEngine:
    def __init__(self, host='127.0.0.1', port=7777):
        self.host = host
        self.port = port

    async def connect_to_mesh(self):
        print(f"[STARTUP] Connecting to telemetry mesh at {self.host}:{self.port}...")
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            print("[CONNECTED] Established active link with network.py mesh.")
            
            while True:
                data = await reader.read(1024)
                if not data:
                    print("[SIGNAL] Stream empty. Mesh connection closed by host.")
                    break
                
                try:
                    packet = json.loads(data.decode())
                    if "timestamp" in packet:
                        print(f"\n[TELEMETRY RECEIVED] {packet['timestamp']}")
                        print(f" -> Rainfall: {packet['rainfall']} mm")
                        print(f" -> Tide Level: {packet['tide']} m")
                        print(f" -> Risk Assessment: {packet['risk_pct']}% ({packet['status']})")
                except json.JSONDecodeError:
                    print("[WARNING] Received malformed non-JSON data packet. Skipping.")
                except Exception as e:
                    print(f"[INTERNAL ERROR] Logic failure during evaluation: {e}")
                    
        except ConnectionRefusedError:
            print("[ERROR] Connection refused. Is network.py running on this port?")
        except Exception as e:
            print(f"[ERROR] Passport Engine disconnected unexpectedly: {e}")
        finally:
            print("[CLEANUP] Connection streams terminated.")

if __name__ == "__main__":
    passport = WorkPassportEngine(host='127.0.0.1', port=7777)
    try:
        asyncio.run(passport.connect_to_mesh())
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Passport Engine manually stopped by developer.")

if __name__ == "__main__":
    passport = WorkPassportEngine(host='127.0.0.1', port=7777)
    try:
        asyncio.run(passport.connect_to_mesh())
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Passport Engine manually stopped by developer.")
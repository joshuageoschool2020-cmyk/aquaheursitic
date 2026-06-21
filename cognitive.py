import asyncio
import json

class CognitiveEngine:
    def __init__(self, host='127.0.0.1', port=7777):
        self.host = host
        self.port = port

    def analyze_learning_profile(self, packet):
        """Processes telemetry metrics to assess cognitive load and focus types."""
        wpm = packet.get("reading_speed_wpm", 200)
        dwell = packet.get("dwell_time_seconds", 2.0)
        intensity = packet.get("interaction_intensity", 0.5)
        fatigue = packet.get("fatigue_index", 0.1)

        print(f"\n--- [COGNITIVE ANALYSIS] ---")
        
        # Determining engagement vector profile
        if wpm > 250 and intensity > 0.6:
            profile = "HIGHLY ENGAGED (Visual/Interactive Focus Mode)"
        elif wpm < 200 and dwell > 5.0:
            profile = "DEEP PROCESSING (Textual/Analytical Absorption Mode)"
        else:
            profile = "STANDARD BALANCE (Calibrated Learning State)"

        print(f"» Tracked Profile   : {profile}")
        print(f"» Reading Velocity : {wpm} WPM | Dwell Window: {dwell}s")
        print(f"» Interaction Ratio: {int(intensity * 100)}% | Fatigue Load: {int(fatigue * 100)}%")
        
        # Overload Check Trigger
        if fatigue > 0.35:
            print("⚠ NOTICE: Focus drift detected. Suggest short cognitive break or format shift.")

    async def connect_to_mesh(self):
        print(f"[COGNITIVE] Siphoning data from mesh link at {self.host}:{self.port}...")
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)
            print("[COGNITIVE] Successfully hooked into live network data pool.")
            
            # Send an initial handshake identifier packet
            handshake = {"node": "cognitive_processor", "status": "active"}
            writer.write(json.dumps(handshake).encode())
            await writer.drain()

            while True:
                data = await reader.read(1024)
                if not data:
                    print("[COGNITIVE] Lost pipeline connection feed.")
                    break
                
                try:
                    packet = json.loads(data.decode())
                    # Skip administrative handshake loops, only process raw telemetry data frames
                    if "timestamp" in packet:
                        self.analyze_learning_profile(packet)
                except Exception as parse_error:
                    pass
                    
        except Exception as e:
            print(f"[ERROR] Cognitive Engine connection drop: {e}")

if __name__ == "__main__":
    engine = CognitiveEngine()
    asyncio.run(engine.connect_to_mesh())
    
import asyncio
import json
import time
import random

async def stream_telemetry_metrics():
    host = '127.0.0.1'
    port = 7777
    
    print(f"[TRACKER] Connecting to local data mesh at {host}:{port}...")
    try:
        reader, writer = await asyncio.open_connection(host, port)
        print("[TRACKER] Connected! Simulating interaction cadence telemetry...")
        
        while True:
            # Simulating human behavioral metrics (dwell time, typing pace, focus metrics)
            telemetry_payload = {
                "timestamp": time.time(),
                "reading_speed_wpm": random.randint(180, 320),
                "dwell_time_seconds": round(random.uniform(1.2, 8.5), 2),
                "interaction_intensity": round(random.uniform(0.1, 1.0), 2),
                "fatigue_index": round(random.uniform(0.0, 0.4), 2)  # Low baseline fatigue
            }
            
            # Pack and send over the mesh network port
            serialized_data = json.dumps(telemetry_payload).encode()
            writer.write(serialized_data)
            await writer.drain()
            
            print(f"[SENT] Streamed interaction packet: {telemetry_payload}")
            await asyncio.sleep(2) # Stream every 2 seconds
            
    except Exception as e:
        print(f"[ERROR] Telemetry tracker lost mesh connection: {e}")

if __name__ == "__main__":
    asyncio.run(stream_telemetry_metrics())
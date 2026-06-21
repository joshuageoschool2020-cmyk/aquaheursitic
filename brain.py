import pandas as pd
import socket
import json
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor

# 1. Training Data (Rainfall in mm, Tide in meters -> Risk %)
data = {
    'rainfall': [0, 50, 100, 200, 300, 500, 10, 150, 400, 20, 80, 250, 600],
    'tide':     [1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 1.1, 1.8, 2.9, 1.3, 1.4, 2.2, 3.5],
    'risk':     [0, 10, 30, 70, 90, 100, 5, 45, 95, 8, 25, 75, 100]
}
df = pd.DataFrame(data)

# 2. Initialize and Train the Model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(df[['rainfall', 'tide']], df['risk'])

def transmit_telemetry(payload):
    """Helper to send prediction data over to the network.py mesh."""
    host = '127.0.0.1'
    port = 7777
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            packet = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "rainfall": payload.get('Rainfall'),
                "tide": payload.get('Tide'),
                "risk_pct": float(payload.get('Risk_Pct')),
                "status": payload.get('Status')
            }
            s.sendall(json.dumps(packet).encode())
            print("? Telemetry successfully piped to mesh cluster network.")
    except ConnectionRefusedError:
        print("[NETWORK WARNING] Mesh network offline. Telemetry not transmitted.")
    except Exception as e:
        print(f"[NETWORK ERROR] Failed to forward telemetry: {e}")

# 3. Interactive Risk Simulator Menu
print("\n" + "="*40)
print("  AQUAHEURISTIC AI: STRATEGIC MONITOR  ")
print("="*40)

while True:
    try:
        user_rain = input("\nEnter Rainfall value (mm) [or 'exit' to quit]: ").strip()
        if user_rain.lower() == 'exit':
            print("Shutting down monitor console.")
            break
            
        user_tide = input("Enter Tide level (meters): ").strip()
        
        rain_val = float(user_rain)
        tide_val = float(user_tide)
        
        pred_features = pd.DataFrame([[rain_val, tide_val]], columns=['rainfall', 'tide'])
        prediction_val = float(model.predict(pred_features)[0])
        
        if prediction_val > 75:
            status = "CRITICAL RISK / OVERFLOW"
        elif prediction_val > 40:
            status = "ELEVATED RISK"
        else:
            status = "STABLE OPERATIONAL LEVELS"
            
        print(f"\n>> Target Status: {status}")
        print(f">> Calculated Risk: {prediction_val:.2f}%")
        
        log_entry = {
            'Rainfall': rain_val,
            'Tide': tide_val,
            'Risk_Pct': prediction_val,
            'Status': status
        }
        
        log_df = pd.DataFrame([log_entry])
        file_exists = __import__('os').path.exists('flood_logs.csv')
        log_df.to_csv('flood_logs.csv', mode='a', index=False, header=not file_exists)
        print("? Data successfully logged to flood_logs.csv")
        
        # Forward data live across the pipeline
        transmit_telemetry(log_entry)
        
    except ValueError:
        print("Error: Invalid input. Please enter valid numbers for rainfall and tide.")

from fastapi import FastAPI
# Import your brain logic here if needed
# from brain import transmit_telemetry 

app = FastAPI()

# 1. This is the "front door" that removes the "Not Found" error
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "The Heuristic Engine is fully operational.",
        "documentation": "/docs"
    }

# 2. Add your existing endpoints here
# Example of how to add an endpoint:
# @app.post("/predict")
# def get_prediction(data: dict):
#     return {"result": "success"}
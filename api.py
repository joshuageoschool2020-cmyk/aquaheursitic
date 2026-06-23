from fastapi import FastAPI, Response
from pydantic import BaseModel
import uvicorn
from brain import process_concept

app = FastAPI()

# This updated UI_HTML uses advanced grid and flexbox for the exact look you want
UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0b1016; color: #88a7c2; font-family: 'Courier New', monospace; }
        .panel { background-color: #121820; border: 1px solid #2a3547; border-radius: 4px; }
        .accent-blue { color: #5d8cb0; }
    </style>
</head>
<body class="p-6">
    <header class="mb-6">
        <h1 class="text-2xl font-bold text-white tracking-widest">HEURISTIC_ENGINE</h1>
        <p class="text-xs text-gray-500 uppercase">System Operational [v3.1]</p>
    </header>
    
    <div class="grid grid-cols-12 gap-6">
        <div class="col-span-4 panel p-5">
            <h2 class="text-xs font-bold uppercase tracking-widest mb-4">// HEURISTIC ANALYTICS WORKSPACE</h2>
            <div class="border border-blue-900/50 p-6 text-center mb-4 bg-blue-900/5">
                <p class="text-sm">Drag and Drop or Click</p>
                <p class="text-[10px] text-gray-600">File Types: (PDF, CSV, JSON, TXT)</p>
            </div>
            <textarea id="textarea" class="w-full h-32 bg-black border border-gray-700 p-3 text-blue-200 text-sm" placeholder="// Quantum datasets..."></textarea>
            <button onclick="runAnalysis()" class="w-full mt-4 bg-indigo-700 py-3 text-white font-bold hover:bg-indigo-600 transition text-sm">INITIALIZE_ANALYSIS</button>
        </div>

        <div class="col-span-8 panel p-5">
            <h2 class="text-xs font-bold uppercase tracking-widest mb-4">// SYNTHETIC_OUTPUT // Analysis Report</h2>
            <div id="output-box" class="h-64 overflow-y-auto border border-gray-800 p-4 text-sm text-gray-300">
                // System ready. Awaiting input sequence...
            </div>
        </div>
    </div>
    
    <script>
        async function runAnalysis() {
            const input = document.getElementById('textarea').value;
            const output = document.getElementById('output-box');
            output.innerText = "Ingesting core dataset... Mapping heuristics...";
            const res = await fetch('/explain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: input })
            });
            const data = await res.json();
            output.innerText = data.result;
        }
    </script>
</body>
</html>
"""

@app.get("/")
@app.get("/app")
async def serve_ui():
    return Response(content=UI_HTML, media_type="text/html")

class RequestData(BaseModel):
    text: str

@app.post("/explain")
def explain_text(data: RequestData):
    return {"result": process_concept(data.text)}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)
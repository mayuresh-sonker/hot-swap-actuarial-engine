import importlib
import threading
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Hot-Swap Actuarial Engine")

# ── Hot-swap state ──────────────────────────────────
_engine_lock = threading.RLock()
_active_engine = None
_active_engine_name = "engine_v1"

def load_engine(name: str):
    global _active_engine, _active_engine_name
    module_path = f"engines.{name}"
    with _engine_lock:
        if module_path in sys.modules:
            module = importlib.reload(sys.modules[module_path])
        else:
            module = importlib.import_module(module_path)
        _active_engine = module
        _active_engine_name = name

load_engine("engine_v1")   # Boot with v1

# ── Data models ─────────────────────────────────────
class QuoteRequest(BaseModel):
    age: int = 35
    vehicle_value: float = 35000
    zip_code: str = "90210"
    coverage: str = "collision"
    vehicle_color: str | None = None

# ── API endpoints ────────────────────────────────────
@app.post("/quote")
async def get_quote(req: QuoteRequest):
    with _engine_lock:
        engine = _active_engine
    result = engine.calculate_premium(
        req.age,
        req.vehicle_value,
        req.zip_code,
        req.coverage,
        req.vehicle_color or "",
    )
    result["request"] = req.model_dump()
    return result

@app.post("/swap/{engine_name}")
async def swap_engine(engine_name: str):
    try:
        load_engine(engine_name)
        return {"status": "swapped", "active": _active_engine_name,
                "version": _active_engine.ENGINE_VERSION}
    except Exception as e:
        raise HTTPException(400, str(e))

@app.get("/status")
async def status():
    with _engine_lock:
        return {"active_engine": _active_engine_name,
                "version": _active_engine.ENGINE_VERSION,
                "name": _active_engine.ENGINE_NAME}

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """<!DOCTYPE html>
<html><head><title>Actuarial Engine Dashboard</title>
<style>
  body{font-family:monospace;background:#0a0a0f;color:#e8f4f8;padding:40px;}
  h1{color:#e8440a;} .btn{padding:10px 20px;margin:8px;cursor:pointer;
  background:#1a7a6e;color:white;border:none;font-size:14px;}
  .btn.swap{background:#e8440a;} pre{background:#1a1a2e;padding:20px;
  border-radius:4px;} #out{min-height:200px;}
</style></head><body>
<h1>🔄 Hot-Swap Actuarial Engine</h1>
<div id="status">Loading...</div>
<hr style="border-color:#333;margin:20px 0">
<button class="btn swap" onclick="swap('engine_v1')">Load v1 — Baseline</button>
<button class="btn swap" onclick="swap('engine_v2')">🚨 Load v2 — CAT Event</button>
<button class="btn" onclick="quote()">Get Quote (Age 23, FL Coastal)</button>
<pre id="out">Click a button to demo...</pre>
<script>
async function status(){
  const r=await fetch('/status');const d=await r.json();
  document.getElementById('status').innerHTML=
    '<b style="color:#82aaff">Active: '+d.name+' ('+d.version+')</b>';}
async function swap(n){
  const r=await fetch('/swap/'+n,{method:'POST'});
  const d=await r.json();
  document.getElementById('out').textContent=JSON.stringify(d,null,2);
  status();}
async function quote(){
  const r=await fetch('/quote',{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({age:23,vehicle_value:28000,
      zip_code:'33101',coverage:'comprehensive',vehicle_color:'red'})});
  const d=await r.json();
  document.getElementById('out').textContent=JSON.stringify(d,null,2);}
status();
</script></body></html>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
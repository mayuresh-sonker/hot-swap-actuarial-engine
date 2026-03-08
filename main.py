import importlib
import threading
import sys
from typing import Optional
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
    vehicle_color: Optional[str] = None

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
  :root{
    --bg:#050712;
    --card:#111827;
    --accent:#e8440a;
    --accent-soft:#1f2937;
    --text:#e5e7eb;
    --muted:#9ca3af;
    --good:#34d399;
  }
  *{box-sizing:border-box;}
  body{
    margin:0;
    font-family:-apple-system,BlinkMacSystemFont,system-ui,sans-serif;
    background:radial-gradient(circle at top,#111827 0,#020617 55%);
    color:var(--text);
    display:flex;
    align-items:center;
    justify-content:center;
    min-height:100vh;
    padding:32px 16px;
  }
  .shell{
    width:100%;
    max-width:960px;
  }
  h1{
    margin:0 0 4px;
    font-size:28px;
    letter-spacing:0.02em;
    color:var(--text);
  }
  .subtitle{color:var(--muted);font-size:13px;margin-bottom:20px;}
  .card{
    background:var(--card);
    border-radius:16px;
    box-shadow:0 24px 60px rgba(0,0,0,0.55);
    padding:20px 22px 22px;
    border:1px solid rgba(148,163,184,0.25);
  }
  .row{display:flex;gap:24px;flex-wrap:wrap;}
  .left,.right{flex:1 1 260px;}
  .section-title{font-size:13px;text-transform:uppercase;letter-spacing:0.14em;color:var(--muted);margin-bottom:10px;}
  .status-pill{
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:6px 10px;
    border-radius:999px;
    background:var(--accent-soft);
    font-size:11px;
    color:var(--muted);
  }
  .status-dot{
    width:7px;height:7px;border-radius:999px;
    background:var(--good);
    box-shadow:0 0 8px rgba(52,211,153,0.9);
  }
  .btn{
    padding:9px 16px;
    margin:0 6px 0 0;
    cursor:pointer;
    background:var(--accent-soft);
    color:var(--text);
    border:none;
    border-radius:999px;
    font-size:13px;
    display:inline-flex;
    align-items:center;
    gap:6px;
  }
  .btn.swap{background:var(--accent);}
  .btn.secondary{background:transparent;border:1px solid rgba(148,163,184,0.4);}
  .btn:active{transform:translateY(1px);}
  .field{margin-bottom:10px;}
  label{font-size:12px;color:var(--muted);display:block;margin-bottom:3px;}
  input,select{
    width:100%;
    padding:8px 9px;
    border-radius:8px;
    border:1px solid rgba(148,163,184,0.5);
    background:#020617;
    color:var(--text);
    font-size:13px;
  }
  input:focus,select:focus{outline:none;border-color:var(--accent);}
  .inputs-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;}
  .quote-main{
    padding:14px 14px 16px;
    border-radius:12px;
    background:linear-gradient(135deg,#020617,#0b1120);
    border:1px solid rgba(148,163,184,0.4);
  }
  .price-row{
    display:flex;
    align-items:baseline;
    justify-content:space-between;
    gap:12px;
  }
  .price-large{font-size:26px;font-weight:600;color:#f9fafb;}
  .price-large span{font-size:16px;color:var(--muted);margin-left:4px;}
  .price-monthly{font-size:14px;color:var(--muted);}
  .pill{
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:4px 8px;
    border-radius:999px;
    background:#022c22;
    color:#6ee7b7;
    font-size:11px;
  }
  .meta{margin-top:10px;font-size:12px;color:var(--muted);}
  .meta strong{color:var(--text);}
  .debug{display:none;font-size:10px;margin-top:10px;white-space:pre-wrap;word-break:break-word;}
</style></head><body>
<div class="shell">
  <div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
      <div>
        <h1>Hot‑Swap Actuarial Quote</h1>
        <div class="subtitle">Compare real‑time premiums as you switch engines and tweak customer details.</div>
      </div>
      <div class="status-pill">
        <span class="status-dot"></span>
        <span id="status">Starting…</span>
      </div>
    </div>
    <div class="row">
      <div class="left">
        <div class="section-title">Customer & vehicle</div>
        <div class="inputs-grid">
          <div class="field">
            <label for="age">Age</label>
            <input id="age" type="number" value="23" min="16" max="100">
          </div>
          <div class="field">
            <label for="vehicle_value">Vehicle value (USD)</label>
            <input id="vehicle_value" type="number" value="28000" step="500">
          </div>
          <div class="field">
            <label for="zip_code">ZIP code</label>
            <input id="zip_code" type="text" value="33101">
          </div>
          <div class="field">
            <label for="coverage">Coverage</label>
            <select id="coverage">
              <option value="liability">Liability</option>
              <option value="collision">Collision</option>
              <option value="comprehensive" selected>Comprehensive</option>
            </select>
          </div>
          <div class="field">
            <label for="vehicle_color">Vehicle color</label>
            <input id="vehicle_color" type="text" value="red">
          </div>
        </div>
        <div style="margin-top:10px;">
          <button class="btn" onclick="quote()">Get quote</button>
          <button class="btn secondary" onclick="swap('engine_v1')">Baseline engine</button>
          <button class="btn secondary" onclick="swap('engine_v2')">CAT event engine</button>
        </div>
      </div>
      <div class="right">
        <div class="section-title">Premium summary</div>
        <div id="quote-main" class="quote-main">
          <div class="price-row">
            <div>
              <div class="price-large" id="annual-price">—</div>
              <div class="price-monthly" id="monthly-price">Fill in details and request a quote.</div>
            </div>
            <div>
              <div class="pill" id="engine-pill">Engine: —</div>
            </div>
          </div>
          <div class="meta" id="meta-text"></div>
        </div>
        <pre id="debug" class="debug"></pre>
      </div>
    </div>
  </div>
</div>
<script>
function formatCurrency(v){
  if(typeof v!=='number' || isNaN(v)) return '—';
  return v.toLocaleString('en-US',{style:'currency',currency:'USD'});
}
function renderQuote(d){
  const annualEl=document.getElementById('annual-price');
  const monthlyEl=document.getElementById('monthly-price');
  const engineEl=document.getElementById('engine-pill');
  const metaEl=document.getElementById('meta-text');
  const debugEl=document.getElementById('debug');

  if(d && d.detail){
    annualEl.textContent='Error';
    monthlyEl.textContent=d.detail;
    engineEl.textContent='Engine: —';
    metaEl.textContent='';
    debugEl.textContent='';
    return;
  }

  const annual=d.annual_premium;
  const monthly=d.monthly_premium;
  const engineName=d.engine_name || 'Unknown engine';
  const engineVersion=d.engine_version || '';
  const req=d.request || {};

  annualEl.innerHTML=formatCurrency(annual)+' <span>/ year</span>';
  monthlyEl.textContent=formatCurrency(monthly)+' per month';
  engineEl.textContent='Engine: '+engineName+(engineVersion ? ' v'+engineVersion : '');

  const parts=[];
  if(typeof req.age!=='undefined') parts.push('Age '+req.age);
  if(typeof req.vehicle_value!=='undefined') parts.push(formatCurrency(req.vehicle_value)+' vehicle');
  if(req.zip_code) parts.push('ZIP '+req.zip_code);
  if(req.coverage) parts.push(req.coverage.charAt(0).toUpperCase()+req.coverage.slice(1)+' coverage');
  if(req.vehicle_color) parts.push((req.vehicle_color||'').toString().toLowerCase()+' vehicle');
  metaEl.innerHTML = parts.length ? '<strong>Profile:</strong> '+parts.join(' · ') : '';

  debugEl.textContent=JSON.stringify(d,null,2);
}

async function status(){
  const r=await fetch('/status');const d=await r.json();
  document.getElementById('status').innerHTML=
    'Active: <strong>'+d.name+' ('+d.version+')</strong>';
}
async function swap(n){
  const r=await fetch('/swap/'+n,{method:'POST'});
  const d=await r.json();
  renderQuote({
    engine_name:d.active || d.engine_name,
    engine_version:d.version,
    annual_premium:NaN,
    monthly_premium:NaN,
    request:{}
  });
  status();
}
async function quote(){
  const body={
    age:Number(document.getElementById('age').value||0),
    vehicle_value:Number(document.getElementById('vehicle_value').value||0),
    zip_code:document.getElementById('zip_code').value||'00000',
    coverage:document.getElementById('coverage').value||'collision',
    vehicle_color:document.getElementById('vehicle_color').value||''
  };
  const r=await fetch('/quote',{method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(body)});
  const d=await r.json();
  renderQuote(d);
}
status();
</script></body></html>"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
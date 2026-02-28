# Hot-Swap Actuarial Engine

A small demo API that lets you **hot-swap** between two actuarial rating engines (baseline vs. catastrophe-adjusted) without restarting the server.

## Prerequisites

- **Python 3.7+**
- **pip** (use `python3 -m pip` if the `pip` command is not found)

## Quick start

### 1. Install dependencies

From the project root:

```bash
python3 -m pip install -r requirements.txt
```

### 2. Start the server

```bash
python3 main.py
```

You should see uvicorn start and the server listening on **http://0.0.0.0:8000**. Leave this terminal open.

### 3. Run the demo

**Option A — Browser**

Open in your browser:

**http://localhost:8000**

Use the dashboard to:
- See which engine is active.
- Switch between **v1 (Baseline)** and **v2 (CAT Event)**.
- Request a sample quote (e.g. age 23, FL coastal).

**Option B — Command line**

In a **new terminal**:

```bash
# Check status
curl http://localhost:8000/status

# Switch to CAT-adjusted engine (v2)
curl -X POST http://localhost:8000/swap/engine_v2

# Get a quote (JSON body)
curl -X POST http://localhost:8000/quote \
  -H "Content-Type: application/json" \
  -d '{"age":23,"vehicle_value":28000,"zip_code":"33101","coverage":"comprehensive"}'
```

## API summary

| Method | Endpoint           | Description                    |
|--------|--------------------|--------------------------------|
| GET    | `/`                | Web dashboard                  |
| GET    | `/status`          | Active engine name and version |
| POST   | `/swap/{engine_name}` | Switch engine (`engine_v1` or `engine_v2`) |
| POST   | `/quote`           | Get premium quote (JSON body: `age`, `vehicle_value`, `zip_code`, `coverage`) |

## Engines

- **engine_v1** — Baseline auto rating model.
- **engine_v2** — CAT-adjusted Florida model (e.g. post-hurricane) with higher base rate and geographic surcharges for coastal ZIPs.

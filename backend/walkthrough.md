# Walkthrough - StellarAcademy Space Education Agent

I have successfully completed the implementation, verification, and containerization of the **space-education-agent** project (StellarAcademy). This interactive Astronomy Educator utilizes ADK 2.0, FastAPI, React/Vite (TS), and a custom NASA MCP Server.

## Key Changes Made

### 1. Backend Service
- **NASA MCP Server ([nasa_mcp_server.py](file:///c:/Users/Cheese/Documents/kaggle%20capstone/space-education-agent/backend/nasa_mcp_server.py))**:
  - Exposes tools to fetch data from NASA APOD (Astronomy Picture of the Day), NeoWs (Near Earth Object Web Service), and DONKI (Space Weather Database).
  - Employs a preloaded physical telemetry fact sheet for planets and spacecraft.
  - Returns `nasa_eyes_key` for exact 3D iframe simulation targeting.
- **ADK 2.0 Agent Workflow ([agent_workflow.py](file:///c:/Users/Cheese/Documents/kaggle%20capstone/space-education-agent/backend/agent_workflow.py))**:
  - `classifier_agent`: Analyzes user query relevance using `gemini-flash-latest`.
  - `router_node`: Routes relevant queries to data retrieval, and unrelated ones to a decline handler.
  - `nasa_data_agent`: Directs tool execution to gather live stats on the target planet or space weather context from the local MCP server.
  - `pedagogical_agent`: Formats findings into an engaging, student-friendly response and constructs telemetry simulation parameters (`simulation_target`, `simulation_url`).
- **FastAPI Wrapper ([main.py](file:///c:/Users/Cheese/Documents/kaggle%20capstone/space-education-agent/backend/main.py))**:
  - Implements `/api/chat` and `/api/health` endpoints.
  - Dynamically routes in-memory ADK runner executions and formats outputs into standard chat responses.
- **Speed Test CLI ([ask_stream.py](file:///c:/Users/Cheese/Documents/kaggle%20capstone/space-education-agent/backend/ask_stream.py))**:
  - Added a CLI utility in the backend folder allowing users to type questions in the terminal and watch responses stream back chunk-by-chunk in real-time, displaying precise speed and latency statistics.

### 2. Frontend Redesign: NASA Retro Arcade Command
Based on user feedback, the frontend design was overhauled from a modern glassmorphic theme to a **youthful, highly engaging 8-bit/16-bit Retro Space Command** aesthetic:
- **NASA Color Palette**:
  - **NASA Insignia Blue (`#0B3D91`)**: Primary styling accent and user chat bubble background.
  - **NASA Insignia Red (`#FC3D21`)**: Primary logo header color and interactive action buttons.
  - **Shuttle Launch Orange (`#FF5C00`)**: Interactive focus synchronizer badges and status alerts.
  - **Solar Array Gold (`#E0AA3E`)**: Custom telemetry indicator labels.
  - **Titanium Silver (`#A0A2A6`)**: Custom 8-bit borders and scrollbar handles.
- **Premium Retro Typography**:
  - Imported `'Press Start 2P'` from Google Fonts for HUD headers and labels.
  - Imported `'Share Tech Mono'` from Google Fonts for highly readable, typewriter-style chat text.
- **Vintage Visual Enhancements**:
  - **CRT Scanline Filter**: Overlay pattern covering the screen to mimic vintage arcade monitors.
  - **NES-Style Borders**: Heavy solid borders (`4px solid #000`) and offset shadow-borders providing clean tactile feedback on hover/active states.
  - **Terminal Typing Prompt**: Replaced standard dots with a retro text status: `"TRANSMITTING DATA FROM MISSION CONTROL"` accompanied by a blinking block cursor `█`.

### 3. Containerization
- **[docker-compose.yml](file:///c:/Users/Cheese/Documents/kaggle%20capstone/space-education-agent/docker-compose.yml)**: Combines services with seamless volume/env bindings.
- **Backend [Dockerfile](file:///c:/Users/Cheese/Documents/kaggle%20capstone/space-education-agent/backend/Dockerfile)** and Frontend **[Dockerfile](file:///c:/Users/Cheese/Documents/kaggle%20capstone/space-education-agent/frontend/Dockerfile)** set up reproducible environments.

---

## Verification & Testing

### 1. Local Workflow Execution
We ran `test_run.py` to trace the ADK 2.0 flow using the live `gemini-flash-latest` model.
```json
{
  "educational_response": "Hello, future space explorer! Let's journey to Mars, the magnificent Red Planet! According to NASA data, Mars is currently a dusty, cold, desert world with a very thin atmosphere...",
  "is_space_related": true,
  "simulation_target": "mars",
  "simulation_url": "https://eyes.nasa.gov/apps/solar-system/#/mars"
}
```

### 2. Frontend Compiling
Vite compiles the new pixel-art styling system and assets cleanly with zero warnings:
```bash
vite v8.0.16 building client environment for production...
transforming...✓ 1764 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.91 kB │ gzip:  0.50 kB
dist/assets/index-DemhIBCw.css    6.06 kB │ gzip:  1.68 kB
dist/assets/index-B2IRrmmu.js   197.04 kB │ gzip: 62.87 kB

✓ built in 261ms
```

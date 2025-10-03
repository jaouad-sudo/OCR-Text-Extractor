# OCR Web App

This repository contains a full-stack OCR web application with:

- Backend: Flask (Python) in `backend/ocr_backend` — serves APIs under `/api` and can serve the frontend static build.
- Frontend: Vite + React in `frontend/ocr-frontend` — development served by the Vite dev server.

This README explains how to set up, run, build and troubleshoot both parts on Windows (PowerShell).

---

## Prerequisites

- Python 3.11+ (this project was tested with Python 3.13 in the workspace's virtualenv)
- Node.js (includes `npm`) — check with `npm --version`
- Optional: `pnpm` if you prefer using pnpm instead of npm
- Tesseract OCR (required by `pytesseract`) — install the Tesseract program on your OS and ensure it is on PATH
  - Windows: install from https://github.com/tesseract-ocr/tesseract or via package managers
- Poppler (required by `pdf2image`) — install and ensure `pdftoppm` is on PATH
  - Windows: https://blog.alivate.com.au/poppler-windows/ or via package manager

Notes:
- On Windows PowerShell, if you see an error about `npm.ps1` being blocked, use `npm.cmd` or update your execution policy (see Troubleshooting).

---

## Backend (Flask)

Location: `backend/ocr_backend`

Files of interest:
- `src/main.py` — Flask app entrypoint. Starts a server on `0.0.0.0:5000` by default (debug mode on).
- `src/routes/` — API blueprints (e.g., `ocr.py`, `user.py`).
- `src/models/user.py` — database model and SQLAlchemy initialization.
- `src/static/` — folder used to serve frontend build output (index.html + assets) when using the Flask server in production mode.

Install and run (PowerShell)

```powershell
# From project root
# Create & activate a virtualenv (if you haven't already)
python -m venv .venv
# Activate (PowerShell)
.\.venv\Scripts\Activate.ps1

# Install backend requirements
& ".\.venv\Scripts\python.exe" -m pip install -r "backend\ocr_backend\requirements.txt"

# Run the backend (development)
cd "backend\ocr_backend"
& ".\.venv\Scripts\python.exe" src\main.py
```

The Flask server starts in debug mode and listens on port 5000. It exposes routes under `/api` (e.g. `http://localhost:5000/api/...`) and serves `src/static/index.html` for the root route if present.

---

## Frontend (Vite + React)

Location: `frontend/ocr-frontend`

Install and run (PowerShell)

```powershell
# From project root
cd "frontend\ocr-frontend"

# Use npm (or pnpm/yarn if you prefer). If npm gives peer dependency issues, use the legacy option shown below
npm install --legacy-peer-deps

# Start the dev server (Vite)
npm run dev
```

Vite typically serves on http://localhost:5173. The exact port will be printed in the terminal.


### Build for production and serve with backend

To build the frontend and have Flask serve the static files:

```powershell
cd "frontend\ocr-frontend"
npm run build
# Copy the build output to the backend static folder.
# Example using robocopy (Windows):
robocopy .\dist "..\..\backend\ocr_backend\src\static" /MIR
```

After copying, start the Flask server (`backend/ocr_backend/src/main.py`) and it will serve the built frontend from `src/static`.

---

## Common commands (summary)

- Backend install: & ".\.venv\Scripts\python.exe" -m pip install -r "backend\ocr_backend\requirements.txt"
- Backend run: & ".\.venv\Scripts\python.exe" backend\ocr_backend\src\main.py
- Frontend install: cd frontend\ocr-frontend; npm install --legacy-peer-deps
- Frontend dev: cd frontend\ocr-frontend; npm run dev
- Frontend build: cd frontend\ocr-frontend; npm run build
- Copy build to backend static (Windows): robocopy .\dist "..\..\backend\ocr_backend\src\static" /MIR

---

## API smoke tests

From a terminal you can curl the backend to check it's responding:

```powershell
# Root (serves static index if present)
curl http://localhost:5000/

# Example API endpoint check (replace with real endpoints from src/routes)
curl http://localhost:5000/api/ocr
curl http://localhost:5000/api/users
```

If these endpoints return JSON or HTML, the backend is serving correctly.

---

## Troubleshooting

- npm.ps1 execution blocked in PowerShell:
  - Use `npm.cmd` instead of `npm` when calling from PowerShell scripts:
    ```powershell
    npm.cmd install
    npm.cmd run dev
    ```
  - Or change execution policy (only if you understand the implications):
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```

- Peer dependency errors on `npm install`:
  - Use `npm install --legacy-peer-deps` to accept legacy peer dependency resolution for development.
  - For production, align package versions in `package.json` to satisfy peer dependency ranges.

- Tesseract / pdf2image issues:
  - `pytesseract` needs the Tesseract binary installed and available on PATH.
  - `pdf2image` requires poppler's `pdftoppm` on PATH.

- If Flask can't find `index.html` when serving frontend:
  - Ensure you built the frontend and copied `dist/index.html` and asset files into `backend/ocr_backend/src/static`.

---

## Project structure (high level)

```
backend/
  ocr_backend/
    requirements.txt
    src/
      main.py
      static/        # where frontend build is served from
      routes/
      models/

frontend/
  ocr-frontend/
    package.json
    src/
    public/
```

---

## Notes about verification

I performed the following checks while preparing this README:
- Installed backend requirements into the project's virtualenv (all satisfied).
- Installed frontend dependencies using `npm install --legacy-peer-deps` to resolve a peer dependency conflict.
- Started the backend Flask server and the Vite dev server in background terminals — both started without immediate startup errors.

If you want, I can append a small `Makefile` or PowerShell script to automate the start-up of both servers together.

---

If you'd like, I can now:
- Add a `dev.ps1` script that launches both servers in separate terminals automatically, or
- Add a short `README` section describing the API endpoints in detail (I can scan `src/routes` and list them), or
- Create a minimal health-check test that verifies both servers respond.

Tell me which of those you'd like next.

# NeuroGenX-AI
NG‑1 (NeuroGenesis) — self‑evolving multi‑agent AutoML / anomaly detection OS (MVP)
# NeuroGenX NG-1

🚀 **NeuroGenX NG-1** is an advanced autonomous AI pipeline that evolves, evaluates, and deploys machine learning models **end-to-end**.  
It is designed to run entirely in **web environments** (GitHub + Render + Vercel), with no local CLI required — Chromebook-friendly.

---

## ✨ Features
- **Agents-based pipeline**: Ingest → Prep → Search (Optuna) → Evaluate → Deploy
- **Provenance & reproducibility**: dataset hashing, manifests, run telemetry
- **Champion model registry**: latest best model always available for `/predict`
- **React frontend**: Upload CSV, launch training runs, view metrics & status
- **Cloud-native**: Deployable on free Render (backend) + Vercel (frontend)

## 📂 Repo Structure
neurogenx-ng1/
  backend/
    app/
      main.py
      core/
        orchestrator.py
        registry.py
        telemetry.py
        schemas.py
      agents/
        base.py
        ingest_csv.py
        prep_basic.py
        search_optuna.py
        evaluate.py
        deploy_fastapi.py
      utils/
        io.py
        hashing.py
        metrics.py
    tests/  (empty for now)
    requirements.txt
    runtime.txt
  frontend/
    index.html
    package.json
    vite.config.js
    src/
      main.jsx
      App.jsx
      components/
        UploadPanel.jsx
        RunLauncher.jsx
        TrialTable.jsx
        MetricsCard.jsx
  models/            (keep small; tracked artifacts)
  data/              (.gitignore; uploads live on server)
  .github/workflows/ci.yml
  README.md
  LICENSE

neurogenx-ng1/ backend/       # FastAPI app, agents, registry, utils frontend/      # React dashboard (Vite + React) .github/       # GitHub Actions workflow models/        # Saved champion models & manifests data/          # Uploaded datasets (ignored in git)
 ## 🚀 Quick Start

### Backend (FastAPI)
1. Deploy to **Render** (free plan):
   - New → Web Service → Import from GitHub
   - Root Directory: `backend`
   - Start Command:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - Environment: Python 3.10

2. Verify backend runs → you should see docs at:

https://<your-service>.onrender.com/docs

### Frontend (React)
1. Deploy to **Vercel**:
- Import the repo → set root directory to `frontend`
- Build command: `npm run build`
- Output dir: `dist`
- Environment variable:
  ```
  VITE_API=https://<your-backend>.onrender.com
  ```

2. Open the frontend URL (Vercel gives you one):
- Upload a CSV (with a binary target column like `0/1`)
- Set target column
- Start run → Monitor logs → Refresh champion → Done ✅

---

## 🛡 License
This project is licensed under the **Apache 2.0 ** (permissive, lets others use it but credits you).  
If you want stronger protection (e.g. prevent closed-source forks), use **AGPL v3**.

---

## 📌 Roadmap
- **v0.2**: Genetic search over model families + GitHub release tagging  
- **v0.3**: Telemetry with Prometheus + Gauntlet validation  
- **v0.4**: Canary deploys + Safety gates  
- **v0.5**: Multi-agent Planner/Executor + Plugin API


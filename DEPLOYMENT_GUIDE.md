# PQC Tool Deployment Guide (Option 2: Cloud Setup)

This guide provides exactly what you need to deploy the Post-Quantum Cryptography Migration Tool to **Vercel** (Frontend) and **Render** (Backend), while seamlessly keeping your local SonarQube instance connected via **ngrok**.

---

## 🏗️ Step 1: Push Code to GitHub
Both Vercel and Render deploy automatically from your GitHub repository.
1. Create a new repository on GitHub.
2. Open a terminal in `pqc-migration-tool` and run:
   ```bash
   git init
   git add .
   git commit -m "Ready for production"
   git branch -M main
   git remote add origin https://github.com/your-username/pqc-migration-tool.git
   git push -u origin main
   ```

---

## 📡 Step 2: Expose Your Local SonarQube (ngrok)
Render needs a public internet URL to talk to your laptop's SonarQube instance.
1. Sign up for a free account at [ngrok.com](https://ngrok.com/).
2. Install ngrok and authenticate using your token.
3. Open a terminal and run:
   ```bash
   ngrok http 9000
   ```
4. **Important:** Copy the **Forwarding URL** it generates (e.g., `https://8a4b...ngrok-free.app`). Leave this terminal running!

---

## ⚙️ Step 3: Deploy the Backend (FastAPI) to Render
1. Go to [Render.com](https://render.com/) and create a free account.
2. Click **New +** > **Web Service**.
3. Connect your GitHub account and select your `pqc-migration-tool` repository.
4. **Configuration Settings**:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt` *(Ensure you have a requirements.txt with fastapi, uvicorn, sslyze, etc.)*
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click **Advanced → Add Environment Variable**:
   - Key = `SONARQUBE_URL`
   - Value = `[Paste your ngrok URL from Step 2]`
6. Click **Create Web Service**.
7. Wait 2-3 minutes for the build to finish. Copy the new Render URL (e.g., `https://pqc-backend.onrender.com`).

---

## 🚀 Step 4: Deploy the Frontend (React/Vite) to Vercel
1. Go to [Vercel.com](https://vercel.com/) and create a free account.
2. Click **Add New** > **Project**.
3. Import your GitHub repository.
4. **Configuration Settings**:
   - **Root Directory**: Click "Edit" and choose `frontend`.
   - **Framework Preset**: Vercel should auto-detect "Vite".
5. Expand **Environment Variables**:
   - Key = `VITE_API_BASE`
   - Value = `[Paste your Render URL from Step 3]`. *IMPORTANT: Make sure to add `/api` to the end if your backend routers require it! Example: `https://pqc-backend.onrender.com/api`*.
6. Click **Deploy**.

---

## 🎉 Step 5: You are live!
Vercel will provide you with a green checkmark and a public URL (like `pqc-migration-tool-seven.vercel.app`).
You can now open this URL from anywhere in the world, and it will communicate with the Render backend, which safely communicates through the ngrok tunnel directly to your laptop's SonarQube instance.

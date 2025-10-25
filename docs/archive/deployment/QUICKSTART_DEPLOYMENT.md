# Quick Deployment Guide

## Local Development (5 minutes)

```bash
# 1. Clone and setup
git clone https://github.com/atharv2802/qa_compliance_bot.git
cd qa_compliance_bot
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Configure
copy .env.example .env
# Edit .env - add your API keys

# 3. Run
python start.py
```

✅ API: http://localhost:8000  
✅ Dashboard: http://localhost:8501

---

## Render Deployment (10 minutes)

### Step 1: Prepare Repository
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy to Render
1. Go to https://render.com
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub repo
4. Select `qa_compliance_bot`
5. Click **"Apply"**

Render will create:
- ✅ `qa-compliance-api` service
- ✅ `qa-compliance-dashboard` service

### Step 3: Configure Secrets
For **qa-compliance-api**:
1. Go to service → **Environment**
2. Add variables:
   - `GROQ_API_KEY`: your_groq_key
   - `OPENAI_API_KEY`: your_openai_key
3. Click **"Save Changes"**

For **qa-compliance-dashboard**:
1. Add same API keys
2. Update `API_URL` to: `https://qa-compliance-api.onrender.com`
3. Click **"Save Changes"**

### Step 4: Update CORS
In **qa-compliance-api** environment:
- Set `CORS_ORIGINS` to: `https://qa-compliance-dashboard.onrender.com`

### Step 5: Verify
- ✅ API: `https://qa-compliance-api.onrender.com/health`
- ✅ Dashboard: `https://qa-compliance-dashboard.onrender.com`

---

## Environment Variables Quick Reference

| Variable | Local | Production |
|----------|-------|------------|
| `MODE` | `local` | `production` |
| `GROQ_API_KEY` | Your key | Your key |
| `OPENAI_API_KEY` | Your key | Your key |
| `API_URL` | `http://localhost:8000` | `https://qa-compliance-api.onrender.com` |
| `CORS_ORIGINS` | `*` | `https://qa-compliance-dashboard.onrender.com` |

---

## Troubleshooting

**API not starting locally?**
- Check port 8000 isn't in use
- Verify `.env` file exists with API keys

**Dashboard can't connect to API?**
- Ensure API is running first
- Check `API_URL` in `.env`

**Render deployment failing?**
- Check build logs in Render dashboard
- Verify API keys are set in Environment tab
- Ensure `render.yaml` is in repo root

**Services sleeping (Free tier)?**
- Render free tier sleeps after 15 min
- First request takes ~30 seconds to wake
- Upgrade to paid for always-on

---

📖 **Full documentation:** See [DEPLOYMENT.md](DEPLOYMENT.md)

# Deployment Guide

This guide covers both local development and production deployment to Render.

## Table of Contents
- [Local Development](#local-development)
- [Production Deployment (Render)](#production-deployment-render)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/atharv2802/qa_compliance_bot.git
   cd qa_compliance_bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy example to .env
   copy .env.example .env  # Windows
   cp .env.example .env    # Linux/Mac
   ```
   
   Edit `.env` and add your API keys:
   ```env
   MODE=local
   GROQ_API_KEY=your_groq_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Seed database (optional)**
   ```bash
   python scripts/seed_synthetic.py
   ```

### Running Locally

#### Option 1: Using startup script (Recommended)
```bash
python start.py
```
This will start both API and dashboard automatically.

#### Option 2: Using Makefile
```bash
make dev
```

#### Option 3: Manual start
Terminal 1 - API:
```bash
uvicorn app.api:app --reload --port 8000
```

Terminal 2 - Dashboard:
```bash
streamlit run app/dashboard.py
```

### Access Points
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501

---

## Production Deployment (Render)

### Prerequisites
- GitHub account
- Render account (free tier available)
- API keys for LLM providers

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Select the `qa_compliance_bot` repository

3. **Render Auto-Detection**
   Render will automatically detect the `render.yaml` file and create:
   - `qa-compliance-api` (FastAPI service)
   - `qa-compliance-dashboard` (Streamlit service)

4. **Configure Environment Variables**
   
   For **qa-compliance-api** service:
   - Go to service → Environment
   - Add the following secret keys:
     ```
     GROQ_API_KEY=your_actual_groq_key
     OPENAI_API_KEY=your_actual_openai_key
     ANTHROPIC_API_KEY=your_actual_anthropic_key (optional)
     ```

   For **qa-compliance-dashboard** service:
   - Add the same API keys
   - Update `API_URL` with your deployed API URL:
     ```
     API_URL=https://qa-compliance-api.onrender.com
     ```

5. **Update CORS (Important!)**
   - After dashboard is deployed, get its URL
   - Update API service's `CORS_ORIGINS` environment variable:
     ```
     CORS_ORIGINS=https://qa-compliance-dashboard.onrender.com
     ```

6. **Deploy**
   - Render will automatically build and deploy both services
   - Wait for builds to complete (usually 5-10 minutes)
   - Check logs for any errors

### Post-Deployment

1. **Verify API**
   - Visit: `https://qa-compliance-api.onrender.com`
   - Check: `https://qa-compliance-api.onrender.com/health`

2. **Verify Dashboard**
   - Visit: `https://qa-compliance-dashboard.onrender.com`
   - Test live suggestions

3. **Monitor**
   - Check Render dashboard for service status
   - View logs for any errors
   - Monitor disk usage (DuckDB database)

---

## Environment Variables

### Required Variables

| Variable | Description | Local Example | Production Example |
|----------|-------------|---------------|-------------------|
| `MODE` | Deployment mode | `local` | `production` |
| `GROQ_API_KEY` | Groq API key | `gsk_xxx...` | `gsk_xxx...` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-proj-xxx...` | `sk-proj-xxx...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | None |
| `LLM_PROVIDER` | Primary LLM provider | `groq` |
| `LLM_MODEL` | Primary model name | `llama-3.1-8b-instant` |
| `JUDGE_PROVIDER` | Judge model provider | `openai` |
| `JUDGE_MODEL` | Judge model name | `gpt-4o-mini` |
| `API_HOST` | API host address | `0.0.0.0` |
| `API_PORT` | API port | `8000` (local), `10000` (production) |
| `CORS_ORIGINS` | Allowed CORS origins | `*` (local) |

### Setting Environment Variables

#### Local (.env file)
```env
MODE=local
GROQ_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
API_URL=http://localhost:8000
```

#### Render (Dashboard)
1. Go to service → Environment
2. Click "Add Environment Variable"
3. Enter key and value
4. Click "Save Changes"
5. Service will automatically redeploy

---

## Architecture

### Local Mode
```
┌─────────────────┐         ┌──────────────────┐
│   localhost     │         │   localhost      │
│   :8000         │◄────────│   :8501          │
│   (API)         │         │   (Dashboard)    │
└────────┬────────┘         └──────────────────┘
         │
         ▼
    ┌─────────┐
    │ DuckDB  │
    │ (local) │
    └─────────┘
```

### Production Mode (Render)
```
┌──────────────────────┐         ┌─────────────────────────┐
│ qa-compliance-api    │         │ qa-compliance-dashboard │
│ .onrender.com        │◄────────│ .onrender.com           │
│ (API)                │  HTTPS  │ (Streamlit)             │
└──────────┬───────────┘         └─────────────────────────┘
           │
           ▼
    ┌──────────────┐
    │ Persistent   │
    │ Disk (1GB)   │
    │ DuckDB       │
    └──────────────┘
```

---

## Troubleshooting

### Local Development

**Problem**: API won't start
- Check if port 8000 is already in use
- Verify `.env` file exists with API keys
- Check Python version (requires 3.10+)

**Problem**: Dashboard can't connect to API
- Ensure API is running first
- Check `API_URL` in `.env` (should be `http://localhost:8000`)
- Verify firewall isn't blocking port 8000

**Problem**: Database locked error
- Ensure only one API instance is running
- Dashboard uses read-only mode, API has write lock
- Restart both services if needed

### Render Deployment

**Problem**: Build failing
- Check build logs in Render dashboard
- Verify `requirements.txt` is up to date
- Ensure Python version is specified correctly

**Problem**: API service unhealthy
- Check environment variables are set correctly
- Verify API keys are valid
- Check `/health` endpoint in logs

**Problem**: Dashboard can't connect to API
- Verify `API_URL` in dashboard environment variables
- Check API service is running and healthy
- Ensure CORS is configured correctly in API

**Problem**: Database errors
- Verify persistent disk is mounted
- Check disk space isn't full
- Review DuckDB logs in service logs

**Problem**: Services sleeping (Free tier)
- Render free tier sleeps after 15 min inactivity
- First request after sleep takes ~30 seconds
- Upgrade to paid plan for always-on services

### Performance Issues

**Problem**: Slow response times
- Check LLM provider status
- Verify fallback providers are configured
- Monitor API latency endpoint: `/analytics/latency`

**Problem**: Database growing too large
- Monitor disk usage in Render
- Consider archiving old events
- Upgrade disk size if needed

---

## Maintenance

### Updating the Application

**Local:**
```bash
git pull origin main
pip install -r requirements.txt
python start.py
```

**Render:**
- Push changes to GitHub
- Render auto-deploys on push to main branch
- Monitor deployment in Render dashboard

### Database Backup

**Local:**
```bash
# Backup DuckDB file
copy data\qa_runs.duckdb data\qa_runs_backup.duckdb
```

**Render:**
- Download persistent disk data from Render dashboard
- Or use API to export events data

### Monitoring

**Check API health:**
```bash
curl https://qa-compliance-api.onrender.com/health
```

**Check event statistics:**
```bash
curl https://qa-compliance-api.onrender.com/events/stats
```

**Check latency:**
```bash
curl https://qa-compliance-api.onrender.com/analytics/latency
```

---

## Security Best Practices

1. **Never commit API keys**
   - Use `.env` for local
   - Use Render environment variables for production
   - Add `.env` to `.gitignore`

2. **Configure CORS properly**
   - Use specific origins in production
   - Avoid `*` in production

3. **Monitor access logs**
   - Review Render logs regularly
   - Set up alerts for errors

4. **Rotate API keys periodically**
   - Update in Render environment
   - Service auto-redeploys

---

## Cost Considerations

### Render Free Tier
- 750 hours/month per service
- Services sleep after 15 min inactivity
- 1GB persistent disk included
- Good for development/testing

### Render Paid Plans
- **Starter ($7/month per service):**
  - Always-on
  - Better performance
  - More disk space
  
- **Standard ($25/month per service):**
  - Higher resources
  - Better for production
  - More concurrent connections

### LLM Provider Costs
- **Groq:** Free tier available, very fast
- **OpenAI:** Pay-per-use, reliable
- **Anthropic:** Pay-per-use, premium quality

---

## Support

- **Documentation:** See `docs/` folder
- **Issues:** GitHub issues
- **Logs:** Render dashboard → Service → Logs

---

## Next Steps

After deployment:
1. Test all endpoints
2. Monitor performance
3. Set up alerts
4. Configure backups
5. Document any custom configurations
6. Share dashboard URL with team

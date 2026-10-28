# Deployment Guide - Render.com

This guide walks through deploying the zcalib-project to Render.com with PostgreSQL.

## What Changed

### Files Modified
1. **`requirements.txt`** - Added `psycopg2-binary==2.9.9` for PostgreSQL support
2. **`render.yaml`** - Added PostgreSQL database configuration
3. **`app/main.py`** - Updated CORS to allow Render URLs
4. **`app/db.py`** - Updated to support both SQLite (dev) and PostgreSQL (prod)

### Database Strategy
- **Local Development**: Uses SQLite (`exams.db` file)
- **Production (Render)**: Uses PostgreSQL (persistent data)
- Automatic detection via `DATABASE_URL` environment variable

## Deployment Steps

### 1. Push to GitHub

```bash
git add .
git commit -m "Add Render deployment with PostgreSQL support"
git push origin main
```

### 2. Create Render Account

Go to [render.com](https://render.com) and sign up (free tier available).

### 3. Deploy Using render.yaml

**Option A: Automatic (Recommended)**

1. In Render dashboard, click **"New +"** → **"Blueprint"**
2. Connect your GitHub repository
3. Render will detect `render.yaml` and create:
   - PostgreSQL database (`zcalib-db`)
   - Web service (`zcalib-project`)
4. Click **"Apply"** to deploy

**Option B: Manual Setup**

1. **Create PostgreSQL Database**:
   - Dashboard → New → PostgreSQL
   - Name: `zcalib-db`
   - Plan: Free
   - Click "Create Database"

2. **Create Web Service**:
   - Dashboard → New → Web Service
   - Connect your repo
   - Configure:
     - **Name**: `zcalib-project`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - Add `DATABASE_URL` → Select the database from dropdown
   - Click "Create Web Service"

### 4. Wait for Deployment

- Build takes 2-3 minutes
- Render will run `pip install` and start your app
- Database tables are created automatically on first startup

### 5. Access Your App

Your app will be live at:
```
https://zcalib-project.onrender.com
```

**API Endpoints**:
- Frontend: `https://zcalib-project.onrender.com/`
- Health: `https://zcalib-project.onrender.com/api/health`
- Docs: `https://zcalib-project.onrender.com/docs`

## Important Notes

### Free Tier Limitations

⚠️ **Render Free Tier**:
- Service spins down after 15 minutes of inactivity
- First request after spin-down takes 30-50 seconds (cold start)
- PostgreSQL free tier: 256 MB storage, 100 connections

### Database Persistence

✅ **PostgreSQL keeps data permanently** (unlike SQLite which resets on deploy)
- Questions persist across deployments
- Exam history is saved
- No data loss on restart

### Local Development

Your local environment is **unchanged**:
```bash
# Still works with SQLite locally
uvicorn app.main:app --reload --port 8000
```

## Monitoring

### View Logs

In Render dashboard:
1. Click your web service
2. Go to "Logs" tab
3. See real-time application logs

### Check Database

1. Click your database service
2. Go to "Connect" → External Connection
3. Use provided connection string with tools like:
   - pgAdmin
   - DBeaver
   - psql CLI

## Troubleshooting

### Build Fails

Check logs for errors:
```bash
# Common issues:
- Missing dependencies → Update requirements.txt
- Python version → Check render.yaml python version
```

### Database Connection Fails

Verify environment variable:
1. Web Service → Environment → DATABASE_URL should be set
2. Should look like: `postgres://user:pass@host/dbname`

### CORS Errors

If frontend can't reach API:
- Check `app/main.py` CORS configuration
- Ensure Render URL is in `allowed_origins`

### Cold Start Slow

This is normal for free tier:
- First request after inactivity takes 30-50s
- Upgrade to paid tier for always-on instances

## Updating Your App

1. Make changes locally
2. Test with SQLite: `uvicorn app.main:app --reload`
3. Commit and push: `git push origin main`
4. Render auto-deploys from `main` branch
5. New version live in 2-3 minutes

## Environment Variables

Available in production:

| Variable | Set By | Purpose |
|----------|--------|---------|
| `DATABASE_URL` | Render | PostgreSQL connection string |
| `RENDER_EXTERNAL_URL` | Render | Your app's public URL |
| `PORT` | Render | Port to bind (don't hardcode 8000) |

## Cost Estimates

**Free Tier** (Current Setup):
- Web Service: Free (750 hours/month)
- PostgreSQL: Free (256 MB, shared CPU)
- **Total: $0/month**

**Paid Tier** (For Production):
- Web Service: $7/month (always-on, 512 MB RAM)
- PostgreSQL: $7/month (1 GB storage, dedicated)
- **Total: $14/month**

## Next Steps

After deployment:
1. ✅ Test at your Render URL
2. ✅ Create some exams to verify database persistence
3. 🔄 Set up custom domain (optional)
4. 🔄 Add monitoring/alerts (optional)
5. 🔄 Configure backup strategy (paid tier)

## Support

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

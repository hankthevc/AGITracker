# ⚡ Quick Start - 5 Minute Deployment

**Already done**: ✅ Code committed and pushed to GitHub

**What you need**: 
- Railway account (https://railway.app)
- Vercel account (https://vercel.com)
- Neon database (https://neon.tech)
- OpenAI API key (https://platform.openai.com)

---

## 1️⃣ Setup Database (2 minutes)

### Run Migrations
```bash
cd "/Users/HenryAppel/AI Doomsday Tracker/infra/migrations"
alembic upgrade head
```

### Seed Predictions
```bash
cd "/Users/HenryAppel/AI Doomsday Tracker/services/etl"
python -c "from app.tasks.predictions.seed_expert_predictions import seed_all_predictions; seed_all_predictions()"
```

---

## 2️⃣ Deploy Backend (Railway) (15 minutes)

### Quick Deploy
```bash
cd "/Users/HenryAppel/AI Doomsday Tracker/services/etl"
railway login
railway init --name agi-tracker-api
railway up
```

### Add Environment Variables
Go to Railway dashboard → Variables:
```bash
DATABASE_URL=your_neon_url_here
OPENAI_API_KEY=your_openai_key_here
API_KEY=$(openssl rand -base64 32)  # Generate and save this
CORS_ORIGINS=https://your-vercel-url.vercel.app  # Add after Vercel deploy
```

### Add Redis
Railway dashboard → New → Database → Redis

### Deploy Workers (Optional but Recommended)
Create 2 more services with same env vars:
- **Worker**: Start command = `celery -A app.celery_app worker --loglevel=info`
- **Beat**: Start command = `celery -A app.celery_app beat --loglevel=info`

---

## 3️⃣ Deploy Frontend (Vercel) (10 minutes)

```bash
cd "/Users/HenryAppel/AI Doomsday Tracker/apps/web"
vercel --prod
```

### Add Environment Variable
```bash
vercel env add NEXT_PUBLIC_API_BASE_URL production
# Enter your Railway URL: https://your-railway-url.up.railway.app

vercel --prod  # Redeploy with env var
```

### Update CORS in Railway
Go back to Railway → Variables → Edit `CORS_ORIGINS`:
```
https://your-actual-vercel-url.vercel.app
```

---

## 4️⃣ Verify Everything Works (5 minutes)

### Test API
```bash
curl https://your-railway-url.up.railway.app/health
```

### Test Frontend
Visit: `https://your-vercel-url.vercel.app/events`

Should see event cards with filtering!

### Test Timeline
Visit: `https://your-vercel-url.vercel.app/timeline`

Should see scatter plot or line chart!

---

## 5️⃣ Monitor (Ongoing)

### Check Logs
```bash
railway logs --follow
```

### Check LLM Budget
Visit: `https://your-railway-url.up.railway.app/health/full`

Look for `llm_budget` section.

---

## 🎉 That's It!

Your AGI Tracker is now:
- ✅ Live on the internet
- ✅ Automatically ingesting events twice daily
- ✅ Generating AI analysis for A/B tier events
- ✅ Tracking expert predictions
- ✅ Visualizing timeline

**Next**: Let it run for a week and check back!

---

## 🆘 If Something Breaks

### API not responding
```bash
railway logs -s agi-tracker-api
```

### Frontend shows errors
```bash
# Check browser console
# Verify NEXT_PUBLIC_API_BASE_URL is set correctly
```

### No events showing
```bash
# Run ingestion manually
cd "/Users/HenryAppel/AI Doomsday Tracker/services/etl"
python scripts/run_ingestors.py
```

---

## 📚 Full Documentation

See `DEPLOYMENT_COMMANDS.md` for detailed step-by-step instructions.

**Estimated total time**: 30-45 minutes ⏱️


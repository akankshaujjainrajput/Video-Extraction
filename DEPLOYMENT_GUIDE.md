# YouTube Video Summarizer - Deployment Guide

## 🚀 Quick Start for Deployment

This app can be deployed on various platforms. Here are the best options:

---

## **Option 1: Streamlit Cloud (EASIEST - FREE)**

### Steps:
1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/video_summarizer.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to: https://share.streamlit.io/
   - Click "New app"
   - Connect GitHub repo
   - Select: `Repository: your-repo` / `Branch: main` / `Main file path: app.py`
   - Click "Deploy"

3. **Your app will be live at**: `https://your-username-video-summarizer.streamlit.app`

**Pros:**
- ✅ Completely free
- ✅ Automatic HTTPS
- ✅ Easy updates (just push to GitHub)
- ✅ No server management

**Cons:**
- ❌ Limited CPU/RAM (can be slow for transcription)
- ❌ ~30 second startup time

---

## **Option 2: Heroku (MODERATE - FREE TIER DEPRECATED)**

Heroku discontinued free tier, but you can use:

### Alternative: Railway.app
1. Go to https://railway.app
2. Connect GitHub account
3. Deploy from repo
4. Set environment: `PORT=8501`
5. Each deployment costs ~$5-10/month

---

## **Option 3: Docker + Cloud Deploy (RECOMMENDED FOR PRODUCTION)**

### Create Dockerfile:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY app.py .

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

### Deploy options with Docker:
- **Google Cloud Run**: Free tier available
- **AWS ECS**: Pay-per-use
- **DigitalOcean App Platform**: ~$12/month minimum
- **Azure Container Instances**: Pay-per-use

---

## **Option 4: VPS Deployment (FULL CONTROL)**

### Providers:
- DigitalOcean Droplet ($5-40/month)
- AWS EC2 (free tier available)
- Linode ($5-100/month)
- Vultr ($2.5+/month)

### Steps:
1. Create Ubuntu 22.04 server
2. SSH into server
3. Clone repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/video_summarizer.git
   cd video_summarizer
   ```

4. Install dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install python3.12 python3-pip ffmpeg
   ```

5. Install Python packages:
   ```bash
   pip install -r requirements.txt
   ```

6. Run with Gunicorn + Nginx (reverse proxy):
   ```bash
   pip install gunicorn
   gunicorn --workers 1 --worker-class "uvicorn.workers.UvicornWorker" --bind 0.0.0.0:8501 app:app
   ```

7. (Optional) Use PM2 to keep running:
   ```bash
   npm install -g pm2
   pm2 start "streamlit run app.py" --name summarizer
   pm2 startup
   pm2 save
   ```

---

## 📋 Requirements for Deployment

### System Requirements:
- **Python 3.10+**
- **RAM**: 2GB minimum (for Whisper model)
- **Disk**: 2GB (includes Whisper base model cache)
- **FFmpeg**: Required for audio processing

### Python Dependencies:
All listed in `requirements.txt`

### Environment Variables (Optional):
```bash
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_RUNONCE=true
```

---

## ⚙️ Configuration for Production

### Streamlit Config (`~/.streamlit/config.toml`):
```toml
[server]
port = 8501
headless = true
runOnSave = false
maxUploadSize = 500

[logger]
level = "warning"

[client]
toolbarMode = "minimal"

[theme]
primaryColor = "#3B82F6"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F3F4F6"
textColor = "#1F2937"
font = "sans serif"
```

---

## 📊 Estimated Costs

| Platform | Cost | Notes |
|----------|------|-------|
| Streamlit Cloud | FREE | Limited resources, slow |
| Railway.app | $5-20/mo | Good for small projects |
| Google Cloud Run | FREE (tier) | Pay-per-use after |
| DigitalOcean VPS | $5-40/mo | Full control |
| AWS EC2 | Varies | Free tier first year |
| Heroku | $7+ (paid tier) | No longer free |

---

## 🔧 Optimization Tips

### 1. **Model Caching**
The Whisper model (~1.5GB) is cached locally. On first run it will download - this is normal.

### 2. **Memory Optimization**
- Use `small` model instead of `base` for faster processing (in `app.py` line ~165)
- Reduce transcript text_area height to save memory

### 3. **Concurrent Users**
- Streamlit Cloud: ~1-2 users max per app
- VPS with multiple workers: Use load balancer

### 4. **Cost Optimization**
- Use Streamlit Cloud for demos (free)
- Use Railway.app for production with low traffic
- Use VPS if you have >10 concurrent users

---

## 🚨 Important Notes

### FFmpeg Installation by Platform:

**Streamlit Cloud:**
- FFmpeg is pre-installed ✅

**Local/VPS:**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# MacOS
brew install ffmpeg

# Windows
Download from: https://ffmpeg.org/download.html
```

### NLTK Data Download:
Add this to your app after first deployment:
```python
import nltk
nltk.download('punkt')
```

---

## 🎯 RECOMMENDED SETUP FOR DEPLOYMENT

### Best for Easy Deployment:
**Streamlit Cloud** → Free, automatic HTTPS, easy updates

### Best for Production:
**DigitalOcean VPS** ($5/mo) + Docker → Full control, better performance

### Best Balance:
**Railway.app** ($10-15/mo) → Easy Docker deployment, good performance

---

## 📝 Deployment Checklist

- [ ] Add `.gitignore` with `temp/`, `__pycache__/`, `.streamlit/`
- [ ] Update `requirements.txt` with exact versions
- [ ] Test app locally with: `streamlit run app.py`
- [ ] Create GitHub repository
- [ ] Push code to GitHub
- [ ] Choose deployment platform
- [ ] Deploy!
- [ ] Test with sample YouTube URL
- [ ] Share with users

---

## 🆘 Troubleshooting

### App crashes with "out of memory":
- Reduce model size or reduce max file size
- Increase RAM allocation

### Whisper model takes too long:
- Use smaller model: `model = whisper.load_model("tiny")` or `"small"`
- Add caching to download once

### FFmpeg not found:
- Install FFmpeg on your server
- App handles Windows automatically

---

For more help, visit:
- Streamlit Docs: https://docs.streamlit.io/
- Streamlit Cloud: https://share.streamlit.io/
- Railway.app: https://railway.app/

# Vercel Deployment Guide

## Quick Setup

1. **Go to Vercel Dashboard** → New Project
2. **Import your GitHub repo**: `https://github.com/enzoweiss21/stealthbanking`
3. **Configure Project Settings**:
   - **Framework Preset**: Other
   - **Root Directory**: `.` (root)
   - **Build Command**: `flutter build web --release`
   - **Output Directory**: `build/web`
   - **Install Command**: `flutter pub get` (optional, Vercel may auto-detect)

4. **Environment Variables** (if your backend is deployed separately):
   - Add `VOC_BACKEND_URL` with your backend API URL (e.g., `https://your-backend.vercel.app`)

5. **Deploy!**

## Important Notes

- The `vercel.json` file is already configured for Flutter routing
- Flutter web is enabled and tested
- The build output goes to `build/web/`
- Make sure your backend API is deployed and accessible (if using separate backend)

## Troubleshooting

- **Blank screen**: Check browser console for errors, verify backend URL is correct
- **404 on refresh**: The `vercel.json` rewrite should handle this
- **Build fails**: Make sure Flutter is available in Vercel's build environment (may need custom Docker image)

## Backend Deployment

Your backend (FastAPI) needs to be deployed separately. Options:
- Vercel Serverless Functions
- Railway
- Render
- Fly.io

Update `VOC_BACKEND_URL` in Vercel environment variables to point to your deployed backend.


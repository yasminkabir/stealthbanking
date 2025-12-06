# Alternative: Pre-build and Deploy Static Files

If Vercel's build times out or Flutter installation fails, use this approach:

## Steps:

1. **Build locally:**
   ```bash
   flutter build web --release
   ```

2. **Create a new branch for static files:**
   ```bash
   git checkout -b static-deploy
   git rm -r --cached .
   git add build/web/*
   git commit -m "Static build for Vercel"
   git push origin static-deploy
   ```

3. **In Vercel:**
   - Connect to the `static-deploy` branch
   - **Root Directory**: `build/web`
   - **Build Command**: (leave empty)
   - **Output Directory**: `.` (current directory)
   - **Framework Preset**: Other

This deploys only the pre-built static files, which is much faster and more reliable.


# Vercel Build Settings

## Required Settings in Vercel Dashboard

When setting up your project in Vercel, use these exact settings:

### Project Settings:
- **Framework Preset**: Other
- **Root Directory**: `.` (leave as root, or blank)

### Build & Development Settings:
- **Build Command**: `./build.sh` (or `flutter build web --release` if Flutter is pre-installed)
- **Output Directory**: `build/web`
- **Install Command**: (leave empty, handled by build script)

### Environment Variables (if needed):
- `VOC_BACKEND_URL` - Your backend API URL (e.g., `https://your-backend.vercel.app`)

## Important Notes:

1. The `vercel.json` file handles routing - it's already configured correctly
2. The `build.sh` script installs Flutter and builds your app
3. If build times out, use the pre-build approach (see VERCEL_ALTERNATIVE.md)

## After Deployment:

Visit your Vercel URL - the app should load without 404 errors!


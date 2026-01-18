# Netlify Deployment Instructions

## Quick Deploy to Netlify

### Option 1: Deploy via GitHub (Recommended)
1. Go to [https://app.netlify.com/](https://app.netlify.com/)
2. Click "Add new site" → "Import an existing project"
3. Choose "Deploy with GitHub"
4. Select repository: `zhirkoalexander-maker/snakegame`
5. Build settings:
   - Build command: (leave empty)
   - Publish directory: `.` (root)
6. Click "Deploy site"

Your site will be available at: `https://[your-site-name].netlify.app`

### Option 2: Manual Deploy via Drag & Drop
1. Go to [https://app.netlify.com/drop](https://app.netlify.com/drop)
2. Drag the project folder into the browser
3. Your site will be deployed instantly!

## Files Required for Netlify
- ✅ `snake_game_web.html` - Main game page
- ✅ `snake_game_web.js` - Game logic
- ✅ `netlify.toml` - Netlify configuration
- ✅ `README.md` - Documentation

## After Deployment
Your game will be accessible via HTTPS at your Netlify URL.

## Custom Domain (Optional)
1. Go to Site settings → Domain management
2. Add custom domain
3. Follow DNS configuration instructions

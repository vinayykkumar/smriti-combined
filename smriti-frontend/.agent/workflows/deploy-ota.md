---
description: Deploy OTA update to users automatically
---

# How to Deploy OTA Updates to Users

OTA (Over-The-Air) updates let you push JavaScript/UI changes directly to users' devices **without requiring them to download a new APK**.

## When to Use OTA Updates

✅ **Use OTA for:**
- UI changes (screens, components, styling)
- Bug fixes in JavaScript code
- New features in React Native code
- API endpoint changes
- Business logic updates
- Most ProfileScreen-type changes

❌ **Cannot use OTA for:**
- Native dependency changes (new packages with native code)
- App config changes (app name, icon, permissions)
- Expo SDK version upgrades
- Changes to `app.json` or `eas.json`

(For these, you need to rebuild the APK using `/trigger-build`)

## How to Deploy OTA Update

1. **Go to GitHub Actions:**
   - Open your repository on GitHub
   - Click the **Actions** tab

2. **Run the OTA deployment:**
   - Click **Deploy OTA Update** in the left sidebar
   - Click **Run workflow** dropdown
   - Fill in the form:
     - **Update channel**: `preview` (for testing) or `production` (for all users)
     - **Branch to deploy from**: e.g., `main`, `feature/profile-page`
     - **Update message**: e.g., "Fixed profile screen layout" (users see this)
   - Click **Run workflow**

3. **Update deploys in ~1 minute:**
   - Much faster than building APK (10-15 min)
   - Check workflow summary for confirmation

4. **Users receive update:**
   - **Automatically** when they next open the app
   - Update downloads in background (~seconds)
   - App reloads with new version
   - **No user action required!**

## Update Channels

- **preview**: For testing with a small group before full rollout
- **production**: For all users in production

**Tip:** Deploy to `preview` first, test it, then deploy the same code to `production`.

## Example Workflow

### Scenario: You just updated ProfileScreen

```bash
# 1. Commit and push your code
git add .
git commit -m "feat: improve profile screen layout"
git push origin feature/profile-page

# 2. Go to GitHub Actions → Deploy OTA Update
# 3. Configure:
#    - Channel: preview
#    - Branch: feature/profile-page
#    - Message: "Improved profile screen layout"
# 4. Click Run workflow

# 5. Wait ~1 minute
# 6. Open your app → update downloads automatically!
```

## Local Testing (Optional)

You can also publish updates locally:

```bash
# Publish to preview channel
npx eas update --branch preview --message "Testing locally"

# Publish to production channel
npx eas update --branch production --message "New feature release"
```

## User Experience

**What users see:**
1. Open app
2. Brief loading screen (update downloading)
3. App reloads with new version
4. ✅ Done! No download or install needed

**Update message** appears in Expo Go or dev builds if you want to show a changelog.

## Benefits Over APK Rebuilds

✅ **Instant deployment** (~1 min vs 10-15 min)  
✅ **No user action** (automatic vs manual download)  
✅ **Rollback support** (can revert bad updates)  
✅ **A/B testing** (different channels for different users)  
✅ **Works with stores** (Play Store, App Store users also get OTA updates)

## Important Notes

- **First install:** Users still need the APK/store app first (use `/trigger-build` for this)
- **Compatible updates only:** OTA can't change native code - the app structure must match
- **Runtime version:** We use `appVersion` policy - OTA updates only work for same app version (1.0.0)
- **Network required:** Users need internet to download updates (but it's tiny, just JS bundle)

## Troubleshooting

- **Update not appearing:** Check the user is on the correct channel (preview vs production)
- **"Runtime version mismatch":** User has old APK, need to rebuild and reinstall
- **Workflow fails:** Check EXPO_TOKEN secret is set in GitHub Settings

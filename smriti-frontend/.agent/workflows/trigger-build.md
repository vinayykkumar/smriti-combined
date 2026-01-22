---
description: Trigger automated APK build and distribution
---

# How to Build and Distribute APK Automatically

This workflow allows you to build and distribute APKs to users with a single button click.

## Prerequisites

**One-time setup required:**

1. **Install EAS CLI locally:**
   ```bash
   npm install -g eas-cli
   ```

2. **Login to Expo:**
   ```bash
   npx eas login
   ```

3. **Generate Expo Access Token:**
   ```bash
   npx eas whoami --json
   ```
   Or create one in [Expo Dashboard → Access Tokens](https://expo.dev/accounts/[username]/settings/access-tokens)

4. **Add token to GitHub:**
   - Go to your repository on GitHub
   - Navigate to: **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Name: `EXPO_TOKEN`
   - Value: Paste the token from step 3
   - Click **Add secret**

## How to Build APK

Once setup is complete:

1. **Go to GitHub Actions:**
   - Open your repository on GitHub
   - Click the **Actions** tab

2. **Run the workflow:**
   - Click **Build and Distribute APK** in the left sidebar
   - Click the **Run workflow** dropdown button (top right)
   - Fill in the form:
     - **Branch to build from**: Enter branch name (e.g., `main`, `feature/profile-page`)
     - **Build profile**: Choose `preview` (for testing) or `production` (for Play Store)
     - **Build message**: Optional note about this build
   - Click **Run workflow**

3. **Monitor the build:**
   - The workflow will start running (takes 10-15 minutes)
   - View progress in the Actions tab
   - When complete, check the workflow summary for download links

4. **Share with users:**
   - Copy the **Direct Download** link from the workflow summary
   - Share this link with your users via WhatsApp, email, etc.
   - Users can click the link to download and install the APK

## Build Profiles

- **preview**: Builds an APK for testing, distributes via internal channel, auto-increments version
- **production**: Builds an AAB (App Bundle) for Google Play Store submission

## Troubleshooting

- **Build fails with "EXPO_TOKEN not found"**: Make sure you've added the secret in GitHub Settings
- **Build takes too long**: First builds take longer; subsequent builds are cached and faster
- **Version conflict on install**: Each build auto-increments the version code, so this shouldn't happen

## Benefits

✅ No manual building on your local machine  
✅ Consistent build environment  
✅ Automatic version incrementing  
✅ Shareable download links  
✅ Build from any branch  
✅ Build history tracked in GitHub Actions

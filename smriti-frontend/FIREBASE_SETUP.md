# Firebase Configuration Guide

## Required Files

After installing Firebase dependencies, you need to add configuration files from the Firebase Console.

### Android Configuration

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project (or create one if needed)
3. Go to Project Settings → Your Apps
4. Download `google-services.json` for Android
5. Place the file at: `android/app/google-services.json`

### iOS Configuration

1. In Firebase Console → Project Settings → Your Apps
2. Download `GoogleService-Info.plist` for iOS
3. Open your project in Xcode
4. Drag and drop `GoogleService-Info.plist` into the project
5. Ensure "Copy items if needed" is checked

## Package Name Verification

Make sure your Firebase app configuration matches your app's bundle identifier:
- **Android**: Check `android/app/build.gradle` for `applicationId`
- **iOS**: Check in Xcode project settings for Bundle Identifier

## Building After Configuration

Once files are added:

```bash
# Android
npx expo run:android

# iOS
npx expo run:ios
```

> **Note**: Push notifications don't work in Expo Go. You must create a development build.

## Troubleshooting

- If build fails, verify the config files are in the correct locations
- Ensure package names match exactly between Firebase Console and your app
- Clean build if needed: `cd android && ./gradlew clean && cd ..`

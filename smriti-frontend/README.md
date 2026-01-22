# Smriti Frontend

React Native mobile application for Smriti - a minimal, non-addictive reflection portal.

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Expo CLI
- Android Studio / Xcode (for native builds)

### Installation

```bash
npm install
```

### Configuration

1. Copy `.env.example` to `.env`
2. Configure environment variables:
   - `API_BASE_URL`: Backend API URL
   - Firebase configuration

### Running

```bash
# Start Expo development server
npm start

# Run on Android
npm run android

# Run on iOS
npm run ios

# Run on web
npm run web
```

## Project Structure

```
smriti-frontend/
├── src/
│   ├── components/    # Reusable components
│   ├── screens/       # Screen components
│   ├── services/      # API and external services
│   ├── contexts/      # React contexts
│   ├── hooks/         # Custom hooks
│   ├── navigation/    # Navigation setup
│   ├── styles/        # Theme and styles
│   └── utils/         # Utility functions
├── assets/            # Images and static assets
└── tests/             # Test files
```

## Testing

```bash
npm test
```

## Building

```bash
# Build for Android
eas build --platform android

# Build for iOS
eas build --platform ios
```

## Documentation

See the [docs](./docs/) folder for detailed documentation.

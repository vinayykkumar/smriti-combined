# Implementation Plan - Home Page and Basic Navigation

The goal is to add a `HomeScreen` with a static card and enable navigation from the `AuthScreen` (Sign Up) to this new `HomeScreen` upon successful account creation.

## User Review Required

> [!NOTE]
> We will use **State-Based Navigation** (simple `if/else` in `App.js`) instead of installing a complex navigation library like `React Navigation`. This is easier to understand for beginners and works well for this simple flow.

## Proposed Changes

### New Components

#### [NEW] [HomeScreen.js](file:///Users/kalyanchakravarthi/.gemini/antigravity/scratch/smriti/SmritiApp/src/screens/HomeScreen.js)
- Will display a welcome message.
- Will display a list of cards (initially one static card).
- Card content:
    - Default/Placeholder Image
    - Title
    - Text content
    - External Links section

### Modified Files

#### [MODIFY] [App.js](file:///Users/kalyanchakravarthi/.gemini/antigravity/scratch/smriti/SmritiApp/App.js)
- Introduce state: `const [isLoggedIn, setIsLoggedIn] = useState(false)`
- Pass a function `onLogin={() => setIsLoggedIn(true)}` to `AuthScreen`.
- Conditionally render:
    - If `isLoggedIn` is true -> Show `HomeScreen`
    - Else -> Show `AuthScreen`

#### [MODIFY] [AuthScreen.js](file:///Users/kalyanchakravarthi/.gemini/antigravity/scratch/smriti/SmritiApp/src/screens/AuthScreen.js)
- Accept `onLogin` prop.
- Call `onLogin()` in `handleSignUp` after successful user storage and alert confirmation.

## Verification Plan

### Manual Verification
1.  **Launch App**: Verify `AuthScreen` is shown first.
2.  **Sign Up**: Enter valid details and click "Sign Up".
3.  **Navigation**: Verify app switches to `HomeScreen` after alert is closed.
4.  **UI Check**: Verify `HomeScreen` shows the static card with image, title, text, and links.

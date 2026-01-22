# Smriti App: Beginner's Guide

This guide explains how the Smriti app is built, structured, and how the Sign Up page works. It is designed for someone with no prior programming knowledge to understand the basics of this application.

## 1. How the App Was Created

The app was built using a framework called **Expo**. Expo is a set of tools built on top of **React Native**, which basically allows us to write mobile apps (for both Android and iOS) using JavaScript—the same language used for websites.

Think of it like building a house:
- **React Native** is the bricks and mortar.
- **Expo** is the toolkit (cranes, blueprints, pre-made frames) that makes building the house much faster and easier.

To start this project, we essentially ran a command that said "Create a new Expo project for me," which set up all the necessary files and folders automatically.

## 2. Project Structure (The "House" Blueprint)

Here is a simplified view of the important folders and files in the project and what they do:

```text
SmritiApp/              <-- The main project folder
├── App.js              <-- The Front Door. This is the first file the app reads.
├── app.json            <-- The ID Card. Contains settings like the app name and icon.
├── src/                <-- The "Source" folder. All our custom code lives here.
│   ├── screens/        <-- The Rooms. Each "screen" (page) of the app goes here.
│   │   └── AuthScreen.js   <-- The Sign Up / Login screen.
│   ├── services/       <-- The Workers. Code that does heavy lifting like saving data.
│   │   └── storage.js      <-- Handles saving user info to the phone's memory.
│   ├── styles/         <-- The Decor. Colors, fonts, and spacing rules.
│   │   └── theme.js        <-- Defines our focused color palette (e.g., green for spiritual).
│   └── utils/          <-- The Tools. Helper functions.
│       └── crypto.js       <-- Helper to secure (hash) passwords.
└── package.json        <-- The Instruction Manual. Lists all the external libraries we use.
```

## 3. The Sign Up Page (Deep Dive)

The Sign Up page is located in `src/screens/AuthScreen.js`. It's built using **React Components**. You can think of a component as a LEGO block. We combine smaller blocks (Text, Inputs, Buttons) to build the full page.

### How it Works (Step-by-Step)

1.  **State Management (The Brain)**:
    -   The app needs to "remember" what you type. We use `useState` for this.
    -   Imagine three little boxes inside the app's memory: one for `username`, one for `password`, and one for `confirmPassword`.
    -   Every time you type a letter, the app updates the corresponding box.

2.  **Display (The Face)**:
    -   **`View`**: Like a `div` in HTML or a box. It holds other elements.
    -   **`Text`**: Displays text (like "Create Account").
    -   **`TextInput`**: The box where you type your username and password.
    -   **`TouchableOpacity`**: The "Sign Up" button. We call it "touchable" because it responds when you touch it.

3.  **Validation (The Bouncer)**:
    -   Before letting you sign up, the code checks a few things:
        -   Is the username empty?
        -   Is the password too short (less than 6 characters)?
        -   Do the password and confirm password match?
    -   If any of these fail, it shows an `Alert` (a pop-up message) and stops.

4.  **Saving Data (The Storage)**:
    -   If everything looks good, the app prepares your data.
    -   **Security**: It doesn't save your password directly. It "hashes" it (scrambles it) using `crypto.js` so it's secure.
    -   **Saving**: It calls `saveUser` from `storage.js`.
    -   `storage.js` uses `AsyncStorage`, which is like a tiny database on your phone itself. It saves your user info there permanently, so it's still there when you close and open the app.

### Visual Breakdown of `AuthScreen.js`

Here is a simplified explanation of the code segments:

**The Imports:**
```javascript
import React, { useState } from 'react';
import { View, Text, TextInput... } from 'react-native';
// ... bringing in the tools we need
```
*This is like gathering ingredients before cooking.*

**The Component Logic:**
```javascript
export default function AuthScreen() {
    // 1. The Variables (State)
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    // 2. The Logic (What happens when you press Sign Up)
    const handleSignUp = async () => {
        // ... checks inputs ...
        // ... saves data ...
    };

    // 3. The Visuals (what you see)
    return (
        <View>
            <Text>Smriti</Text>
            <TextInput value={username} onChangeText={setUsername} ... />
            <Button onPress={handleSignUp} title="Sign Up" />
        </View>
    );
}
```

## 4. Deep Dive: The Front Door (`App.js`)

You asked to understand `App.js` and the "front door" concept more deeply. Let's break it down.

### The Key: `index.js`
Before you can open the door, you need a key. `index.js` is that key.
- It is a tiny file that does one job: tell the phone "Hey, the app starts here!".
- It points directly to `App.js`. You almost never need to touch this file. It just hands over control to `App.js`.

### The Door: `App.js`
This is the main entry point. When the app launches, this is the first piece of code that runs to decide what to show on the screen.

Here is the code in `App.js` explained line-by-line:

#### Part 1: Gathering Tools (Imports)
```javascript
import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { StyleSheet, View } from 'react-native';
import AuthScreen from './src/screens/AuthScreen';
```
- **Analogy**: Before you start cooking, you put your tools on the counter.
- **`StatusBar`**: This is the tool to control the little bar at the top of your phone (where time and battery are).
- **`React`**: The core library.
- **`View`**: A box container.
- **`AuthScreen`**: We are importing the "Sign Up Room" we built earlier. We are telling `App.js`: "Hey, bring in that Sign Up page, we're going to use it."

#### Part 2: The Main Function (The Entry Hall)
```javascript
export default function App() {
  return (
    <View style={styles.container}>
      <StatusBar style="dark" />
      <AuthScreen />
    </View>
  );
}
```
- **`export default function App()`**: This declares the main component. "App" is the name of our entire application.
- **`return (...)`**: This describes what the app *looks like* right now.
- **`<View style={styles.container}>`**: We create a main container (the building itself) and apply some styles (paint/layout) to it.
- **`<StatusBar style="dark" />`**: We tell the phone: "Make the battery/time text dark so users can read it."
- **`<AuthScreen />`**: **This is the critical part.** We are placing the `AuthScreen` component inside our App. Because this is the *only* thing we are showing, the entire app *is* just the Sign Up screen right now.
    - If we had a Login screen, we might say: "If user is logged in, show Home; otherwise, show AuthScreen." But for now, we just show AuthScreen.

#### Part 3: The Decor (Styles)
```javascript
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
});
```
- **`flex: 1`**: This means "Expand to fill the whole screen." It ensures the app takes up all available space from top to bottom.
- **`backgroundColor`**: Sets the background color of the main container.

---

## 5. The Construction Materials (`package.json`, `node_modules`, etc.)

You asked about `package.json` and other strange files. Let's use our house analogy.

### `package.json` (The Wishlist)
This file is like the **Architect's Wishlist** or **Shopping List**.
- It lists everything your app *needs* to work, but not the actual items themselves.
- It says: "I need React (bricks), I need Expo (cranes), I need Crypto (locks)."
- It does **not** contain the code for these things, just their names and version numbers.

### `node_modules` (The Warehouse)
This is the **Construction Warehouse**.
- When you run `npm install`, a delivery truck arrives and reads your `package.json` (Wishlist).
- It goes to the global factory (the internet), gets all the bricks, cranes, and locks you asked for, and dumps them into the `node_modules` folder.
- This folder is HUGE. It contains thousands of files. That's why we never edit it manually. It's just a storage room for other people's code that we use to build our house.

### `package-lock.json` (The Official Receipt)
This is the **Detailed Receipt**.
- While `package.json` might say "I need white paint," `package-lock.json` records: "Bought 'Benjamin Moore White Dove, Matte Finish, Batch #99281'."
- It ensures that if another developer works on this project (or you move to a new computer), they get the **exact** same version of every single tool. No surprises.

### What is "Building the App"?

Right now, your code is just a bunch of English-like text files (JavaScript). Your phone doesn't understand "JavaScript"; it understands binary code (0s and 1s).

**Building the App** is the process of translating your blueprints into a real building.
1.  **Translation**: The computer reads your `App.js` and all your text files.
2.  **Bundling**: It grabs the necessary tools from `node_modules`.
3.  **Compilation**: It meshes them all together and translates them into a single file that your phone can run (like an `.apk` file for Android or `.ipa` for iPhone).

**Think of it like this:**
- **Code**: The blueprints on paper.
- **Build Process**: The construction crew working.
- **The Built App**: The finished house you can walk into.

---

## 6. The Home Page & Navigation

We've now added a **Home Page** and a way to get there.

### The Home Page (`HomeScreen.js`)
This is the "Living Room" of your app.
- We created a new file: `src/screens/HomeScreen.js`.
- It currently displays a single "Card" with a picture, title, and some text about Mindfulness.
- **Why a "Card"?** In apps, a "Card" is a common UI pattern. It Groups related information (image + text + link) into a neat little box.

### How Navigation Works (The Doorman)
We updated `App.js` to act like a Doorman who checks ID.

**Old `App.js`:**
> "Welcome! Please go straight to the Sign Up room."

**New `App.js`:**
> "Welcome!
> Are you logged in?
> **YES** -> Go to the **Living Room** (Home Page).
> **NO** -> Go to the **Sign Up Room** (Auth Page)."

**In Code:**
```javascript
{isLoggedIn ? (
  <HomeScreen />
) : (
  <AuthScreen onLogin={() => setIsLoggedIn(true)} />
)}
```
- `isLoggedIn` is a simple switch (True/False).
- When you click "Sign Up" successfully, we flip that switch to **True**.
- `App.js` sees the switch change and *immediately* swaps the Sign Up screen for the Home screen.

---

## 7. Anatomy of a React Component (The Recipe)

You asked "What does a typical React component contain?"
Every component (like `AuthScreen.js` or `HomeScreen.js`) follows the same basic recipe.

Think of a Component as a **Dish** you are cooking.

### 1. The Ingredients (Imports)
At the very top, we grab what we need from the pantry.
```javascript
import React from 'react';
import { View, Text, Button } from 'react-native';
```
*   "I need the React cookbook."
*   "I need a Box (View), some Writing (Text), and a Button."

### 2. The Recipe Instructions (The Function)
This is the main block of code.
```javascript
export default function MyComponent() {
  // ... code goes here ...
}
```
*   `export default`: This means "Serve this dish to anyone who asks for it."
*   `function`: This is the start of the recipe steps.

### 3. The Memory (State/Hooks)
Inside the function, the first thing we do is set up our short-term memory.
```javascript
const [count, setCount] = useState(0);
```
*   "I need to remember a number called `count`. Start it at 0."
*   "If I need to change it, I'll use the `setCount` tool."

### 4. The Actions (Helper Functions)
Next, we define what happens when the user interacts.
```javascript
const handlePress = () => {
    setCount(count + 1);
};
```
*   "When the button is pressed, take the current count and add 1."

### 5. The Presentation (The Return Statement)
Finally, we return the visual "Dish" that shows up on the screen.
```javascript
return (
    <View>
        <Text>You clicked {count} times</Text>
        <Button onPress={handlePress} title="Click Me" />
    </View>
);
```
*   "Here is a Box. Inside, put some text showing the count, and a button that runs `handlePress`."

### 6. The Decor (Styles)
At the very bottom, we define how it looks (colors, spacing, fonts).
```javascript
const styles = StyleSheet.create({ ... });
```

---

## 8. Summary for a Non-Tech Person

1.  We used **Expo** to quickly set up a professional mobile app structure.
2.  We organized our code into folders: **screens** (what you see), **services** (what the app does in the background), and **styles** (how it looks).
3.  **`App.js`** is the **Front Door**. It doesn't do much itself; it just welcomes the user and immediately shows them the room inside.
4.  **`package.json`** is your **Shopping List** of tools, and **`node_modules`** is the **Warehouse**.
5.  A **Component** is like a **Recipe**: It has **Imports** (Ingredients), **State** (Memory), **Logic** (Actions), and **JSX** (The final Dish you serve).

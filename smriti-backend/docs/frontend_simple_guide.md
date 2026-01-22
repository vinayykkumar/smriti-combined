# Frontend Integration Guide - Simple & Clear

## Overview

Your backend uses a modern authentication system similar to popular social apps. Users sign up with a username and can login using either their username or email. Here's everything you need to know to integrate it into your React Native app.

---

## How Authentication Works

### The Big Picture

When a user signs up or logs in, the backend gives you a **token**. This token is like a key that proves the user is logged in. You store this token on the device and send it with every request to protected endpoints.

**Important:** The backend uses an internal `userId` for database operations, but you never see it. The token contains this ID internally, so you don't need to worry about it.

---

## User Data Structure

### What You Collect During Signup

```javascript
{
  username: "win_i",                        // Required, unique (3-30 chars)
  password: "test@12345",                   // Required (6-128 chars)
  email: "kumarvinay0011.vk@gmail.com",    // Optional but recommended
  display_name: "Vinay"                     // Optional (1-50 chars)
}
```

**Rules:**
- **Username:** Must be unique. This is like their handle (@win_i). Users will use this to login and for @mentions.
- **Email OR Phone:** At least one is required. Used for account recovery and verification.
- **Display Name:** Optional. This is what shows in the UI. Multiple users can have the same display name (e.g., "John Doe").
- **Password:** Minimum 6 characters. Backend hashes it securely.

### What You Get Back

```javascript
{
  success: true,
  message: "User registered successfully",
  data: {
    username: "win_i",
    displayName: "Vinay",
    email: "kumarvinay0011.vk@gmail.com",
    phone: null,
    token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Notice:** No `userId` in the response! The backend handles it internally.

---

## Implementation Guide

### 1. Signup Flow

**API Endpoint:** `POST https://smriti-backend-r293.onrender.com/api/auth/signup`

**React Native Example:**

```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';

const signup = async (username, email, password, displayName) => {
  try {
    const response = await fetch('https://smriti-backend-r293.onrender.com/api/auth/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username,
        email: email,
        password: password,
        display_name: displayName  // Optional
      })
    });

    const data = await response.json();

    if (data.success) {
      // Store user data locally
      await AsyncStorage.multiSet([
        ['username', data.data.username],
        ['displayName', data.data.displayName || ''],
        ['email', data.data.email || ''],
        ['token', data.data.token]
      ]);

      return { success: true, user: data.data };
    } else {
      // Handle error (username taken, validation error, etc.)
      return { success: false, error: data.error };
    }
  } catch (error) {
    return { success: false, error: 'Network error' };
  }
};
```

**Common Errors:**
- `409`: Username or email already taken
- `400`: Validation error (username too short, missing email/phone, etc.)

---

### 2. Login Flow

Users can login with **either username OR email**. Your app can have a single input field and detect which one they're using.

**API Endpoint:** `POST https://smriti-backend-r293.onrender.com/api/auth/login`

**React Native Example:**

```javascript
const login = async (identifier, password) => {
  try {
    // Detect if identifier is email or username
    const isEmail = identifier.includes('@');
    
    const response = await fetch('https://smriti-backend-r293.onrender.com/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        [isEmail ? 'email' : 'username']: identifier,
        password: password
      })
    });

    const data = await response.json();

    if (data.success) {
      // Store user data
      await AsyncStorage.multiSet([
        ['username', data.data.username],
        ['displayName', data.data.displayName || ''],
        ['email', data.data.email || ''],
        ['token', data.data.token]
      ]);

      return { success: true, user: data.data };
    } else {
      return { success: false, error: data.error };
    }
  } catch (error) {
    return { success: false, error: 'Network error' };
  }
};
```

**Common Errors:**
- `401`: Wrong password or user doesn't exist
- `400`: Neither username nor email provided

---

### 3. Check Username Availability

Before signup, you can check if a username is already taken. This gives users instant feedback.

**API Endpoint:** `GET https://smriti-backend-r293.onrender.com/api/auth/check-username/{username}`

**React Native Example:**

```javascript
const checkUsername = async (username) => {
  try {
    const response = await fetch(
      `https://smriti-backend-r293.onrender.com/api/auth/check-username/${username}`
    );
    const data = await response.json();
    
    return data.available; // true or false
  } catch (error) {
    return null;
  }
};

// Use in your signup form
const handleUsernameChange = async (text) => {
  setUsername(text);
  
  if (text.length >= 3) {
    const available = await checkUsername(text);
    if (available) {
      setUsernameStatus('✓ Available');
    } else {
      setUsernameStatus('✗ Already taken');
    }
  }
};
```

---

### 4. Making Authenticated Requests

For any protected endpoint (like fetching posts), include the token in the `Authorization` header.

**Example: Get User's Posts**

```javascript
const getPosts = async () => {
  try {
    const token = await AsyncStorage.getItem('token');
    
    const response = await fetch('https://smriti-backend-r293.onrender.com/api/posts/', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    const data = await response.json();
    
    if (data.success) {
      return data.data.posts;
    } else {
      // Token might be expired
      if (response.status === 401) {
        // Redirect to login
      }
      return [];
    }
  } catch (error) {
    return [];
  }
};
```

---

### 5. Displaying User Information

**In Profile Screen:**

```javascript
const ProfileScreen = () => {
  const [username, setUsername] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');

  useEffect(() => {
    const loadUserData = async () => {
      const user = await AsyncStorage.getItem('username');
      const name = await AsyncStorage.getItem('displayName');
      const mail = await AsyncStorage.getItem('email');
      
      setUsername(user);
      setDisplayName(name);
      setEmail(mail);
    };
    
    loadUserData();
  }, []);

  return (
    <View>
      <Text style={styles.displayName}>
        {displayName || username}  {/* Show display name if set, else username */}
      </Text>
      <Text style={styles.handle}>
        @{username}  {/* Always show username as handle */}
      </Text>
      <Text style={styles.email}>{email}</Text>
    </View>
  );
};
```

**In Post/Comment Author:**

```javascript
<View>
  <Text style={styles.authorName}>
    {post.author.displayName || post.author.username}
  </Text>
  <Text style={styles.authorHandle}>
    @{post.author.username}
  </Text>
</View>
```

---

### 6. Logout

Simply clear the stored data.

```javascript
const logout = async () => {
  await AsyncStorage.multiRemove(['username', 'displayName', 'email', 'token']);
  // Navigate to login screen
};
```

---

## Key Concepts

### Username vs Display Name

Think of it like this:

- **Username** = Twitter handle (@win_i) - Unique, used for login and @mentions
- **Display Name** = Your actual name (Vinay) - Not unique, shown in UI

**Example:**
- User 1: `@john_doe` with display name "John Doe"
- User 2: `@johndoe123` with display name "John Doe" ← Same display name, different username

### Why No userId in Frontend?

The backend uses `userId` internally for database operations, but you don't need it. The JWT token contains the userId, so when you send the token with requests, the backend knows who you are.

**This keeps your API responses clean and simple.**

---

## Complete Signup/Login Example

Here's a complete example for your signup/login screens:

```javascript
import React, { useState } from 'react';
import { View, TextInput, Button, Text } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'https://smriti-backend-r293.onrender.com';

const AuthScreen = ({ navigation }) => {
  const [isSignup, setIsSignup] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [error, setError] = useState('');

  const handleAuth = async () => {
    try {
      const endpoint = isSignup ? '/api/auth/signup' : '/api/auth/login';
      const body = isSignup
        ? { username, email, password, display_name: displayName }
        : { [email.includes('@') ? 'email' : 'username']: username || email, password };

      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });

      const data = await response.json();

      if (data.success) {
        // Store user data
        await AsyncStorage.multiSet([
          ['username', data.data.username],
          ['displayName', data.data.displayName || ''],
          ['email', data.data.email || ''],
          ['token', data.data.token]
        ]);

        // Navigate to home screen
        navigation.navigate('Home');
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  return (
    <View>
      <TextInput
        placeholder="Username"
        value={username}
        onChangeText={setUsername}
      />
      
      {isSignup && (
        <>
          <TextInput
            placeholder="Display Name (optional)"
            value={displayName}
            onChangeText={setDisplayName}
          />
          <TextInput
            placeholder="Email"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
          />
        </>
      )}
      
      <TextInput
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      {error ? <Text style={{ color: 'red' }}>{error}</Text> : null}

      <Button
        title={isSignup ? 'Sign Up' : 'Login'}
        onPress={handleAuth}
      />

      <Button
        title={isSignup ? 'Already have an account? Login' : 'Need an account? Sign Up'}
        onPress={() => setIsSignup(!isSignup)}
      />
    </View>
  );
};

export default AuthScreen;
```

---

## Testing

You can test with this real account that's already in the database:

**Username:** `win_i`  
**Email:** `kumarvinay0011.vk@gmail.com`  
**Password:** `test@12345`

Try logging in with both username and email to verify it works!

---

## Common Questions

**Q: Do I need to store userId?**  
A: No! The backend handles it internally through the token.

**Q: Can users change their username later?**  
A: Not yet, but it's easy to add. For now, usernames are permanent.

**Q: Can users change their display name?**  
A: Yes, you can add an update profile endpoint later.

**Q: What if the token expires?**  
A: You'll get a 401 error. Redirect the user to login again.

**Q: Should I validate email format on frontend?**  
A: Yes, for better UX. But the backend also validates it.

---

## Summary

**Signup:** Username + Email + Password → Get token  
**Login:** Username/Email + Password → Get token  
**Authenticated Requests:** Include `Authorization: Bearer {token}` header  
**Display:** Show display name if set, otherwise show username  

**That's it!** Your authentication is simple, secure, and ready to use. 🚀

---
applyTo: "mobile/**"
name: "mobile-app-rules"
description: "React Native and Expo mobile application standards and patterns"
---

# Mobile App Rules - Algo Trading System

> **Mobile App Agent**: This guide contains React Native, Expo, and mobile-specific rules for the trading mobile application.

**Last Updated**: December 7, 2025  
**Stack**: React Native • Expo • TypeScript • React Navigation • AsyncStorage

---

## Table of Contents

1. [Critical Mobile Policies](#critical-mobile-policies)
2. [Project Structure](#project-structure)
3. [Navigation Patterns](#navigation-patterns)
4. [Code Standards](#code-standards)
5. [State Management](#state-management)
6. [API Integration](#api-integration)
7. [Offline Support](#offline-support)

---

## 1. Critical Mobile Policies

### ⚠️ Policy 1: Secure Storage for Credentials

**ALL sensitive data MUST use SecureStore, not AsyncStorage.**

```typescript
// ❌ FORBIDDEN - Plain text storage
import AsyncStorage from '@react-native-async-storage/async-storage'
await AsyncStorage.setItem('token', jwtToken)

// ✅ REQUIRED - Secure storage
import * as SecureStore from 'expo-secure-store'
await SecureStore.setItemAsync('token', jwtToken)
```

### ⚠️ Policy 2: Type Safety Everywhere

**ALL components and functions MUST be fully typed.**

```typescript
// ✅ REQUIRED - Full type safety
interface Strategy {
  id: string
  symbol: string
  buyTime: string
  sellTime: string
  stopLoss: number
  quantity: number
  status: 'ACTIVE' | 'RUNNING' | 'STOPPED'
}

interface StrategyCardProps {
  strategy: Strategy
  onPress: (strategy: Strategy) => void
}

export function StrategyCard({ strategy, onPress }: StrategyCardProps) {
  return (
    <TouchableOpacity onPress={() => onPress(strategy)}>
      <Text>{strategy.symbol}</Text>
    </TouchableOpacity>
  )
}
```

### ⚠️ Policy 3: Platform-Specific Code

**Use Platform module for platform-specific behavior.**

```typescript
import { Platform, StyleSheet } from 'react-native'

const styles = StyleSheet.create({
  container: {
    padding: Platform.select({
      ios: 20,
      android: 16,
      default: 16
    }),
    // Platform-specific shadows
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4
      },
      android: {
        elevation: 4
      }
    })
  }
})
```

### ⚠️ Policy 4: Error Handling

**ALL API calls MUST handle errors gracefully.**

```typescript
// ✅ REQUIRED - Proper error handling
async function fetchStrategies() {
  try {
    const response = await api.getStrategies()
    setStrategies(response.data)
  } catch (error) {
    if (error.response?.status === 401) {
      // Token expired, redirect to login
      navigation.navigate('Login')
    } else {
      // Show user-friendly error
      Alert.alert(
        'Error',
        'Failed to load strategies. Please try again.',
        [{ text: 'OK' }]
      )
    }
  }
}
```

### ⚠️ Policy 5: Performance Optimization

**Use React.memo, useMemo, useCallback for optimization.**

```typescript
// ✅ REQUIRED - Memoized components
import { memo, useMemo, useCallback } from 'react'

interface StrategyListProps {
  strategies: Strategy[]
  onStrategyPress: (id: string) => void
}

export const StrategyList = memo(({ strategies, onStrategyPress }: StrategyListProps) => {
  // Memoize expensive computations
  const sortedStrategies = useMemo(() => {
    return [...strategies].sort((a, b) => a.symbol.localeCompare(b.symbol))
  }, [strategies])
  
  // Memoize callbacks to prevent re-renders
  const handlePress = useCallback((id: string) => {
    onStrategyPress(id)
  }, [onStrategyPress])
  
  return (
    <FlatList
      data={sortedStrategies}
      keyExtractor={item => item.id}
      renderItem={({ item }) => (
        <StrategyCard strategy={item} onPress={() => handlePress(item.id)} />
      )}
    />
  )
})
```

---

## 2. Project Structure

### Mobile Directory Layout

```
mobile/
├── app/
│   ├── (auth)/
│   │   ├── login.tsx              # Login screen
│   │   └── register.tsx           # Registration screen
│   ├── (tabs)/
│   │   ├── _layout.tsx            # Tab navigator
│   │   ├── index.tsx              # Home/Dashboard
│   │   ├── strategies.tsx         # Strategy list
│   │   ├── brokers.tsx            # Broker setup
│   │   └── profile.tsx            # User profile
│   ├── strategies/
│   │   ├── [id].tsx               # Strategy detail
│   │   └── new.tsx                # Create strategy
│   ├── _layout.tsx                # Root layout
│   └── +not-found.tsx             # 404 screen
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   └── LoadingSpinner.tsx
│   ├── auth/
│   │   └── LoginForm.tsx
│   ├── strategies/
│   │   ├── StrategyList.tsx
│   │   ├── StrategyCard.tsx
│   │   └── StrategyForm.tsx
│   └── layout/
│       ├── Header.tsx
│       └── TabBar.tsx
├── hooks/
│   ├── useAuth.ts                 # Authentication hook
│   ├── useStrategies.ts           # Strategy data hook
│   ├── useApi.ts                  # API client hook
│   └── useNetworkStatus.ts        # Network detection hook
├── lib/
│   ├── api.ts                     # API client
│   ├── storage.ts                 # Secure storage utilities
│   ├── validators.ts              # Validation schemas
│   └── types.ts                   # TypeScript types
├── constants/
│   ├── Colors.ts                  # Theme colors
│   └── Config.ts                  # App configuration
├── assets/
│   ├── images/
│   └── fonts/
├── app.json                       # Expo configuration
├── tsconfig.json
└── package.json
```

---

## 3. Navigation Patterns

### Expo Router Navigation

```typescript
// app/(tabs)/_layout.tsx - Tab Navigator
import { Tabs } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        headerShown: false
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Dashboard',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="home" size={size} color={color} />
          )
        }}
      />
      <Tabs.Screen
        name="strategies"
        options={{
          title: 'Strategies',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="trending-up" size={size} color={color} />
          )
        }}
      />
      <Tabs.Screen
        name="brokers"
        options={{
          title: 'Brokers',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="business" size={size} color={color} />
          )
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="person" size={size} color={color} />
          )
        }}
      />
    </Tabs>
  )
}
```

### Screen Navigation

```typescript
// app/(tabs)/strategies.tsx
import { useRouter } from 'expo-router'
import { View, FlatList, TouchableOpacity } from 'react-native'
import { StrategyCard } from '@/components/strategies/StrategyCard'
import { useStrategies } from '@/hooks/useStrategies'

export default function StrategiesScreen() {
  const router = useRouter()
  const { strategies, loading } = useStrategies()
  
  const handleStrategyPress = (id: string) => {
    router.push(`/strategies/${id}`)
  }
  
  const handleNewStrategy = () => {
    router.push('/strategies/new')
  }
  
  return (
    <View style={{ flex: 1 }}>
      <FlatList
        data={strategies}
        keyExtractor={item => item.id}
        renderItem={({ item }) => (
          <StrategyCard 
            strategy={item} 
            onPress={() => handleStrategyPress(item.id)} 
          />
        )}
      />
      <TouchableOpacity onPress={handleNewStrategy}>
        <Text>+ New Strategy</Text>
      </TouchableOpacity>
    </View>
  )
}
```

---

## 4. Code Standards

### TypeScript Configuration

```json
// tsconfig.json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "skipLibCheck": true,
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

### Naming Conventions

```typescript
// Files: PascalCase for components, camelCase for utilities
// components/StrategyCard.tsx
// hooks/useStrategies.ts
// lib/apiClient.ts

// Components: PascalCase
export function StrategyCard() {}
export function LoginForm() {}

// Hooks: camelCase with 'use' prefix
export function useAuth() {}
export function useStrategies() {}

// Functions/Variables: camelCase
const getCurrentUser = () => {}
const strategyList = []

// Constants: UPPER_SNAKE_CASE
const MAX_RETRIES = 3
const API_TIMEOUT = 5000

// Types/Interfaces: PascalCase
interface Strategy {}
type UserRole = 'Admin' | 'User' | 'Broker'
```

### Import Organization

```typescript
// 1. React imports
import { useState, useEffect } from 'react'

// 2. React Native imports
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native'

// 3. Expo imports
import { useRouter } from 'expo-router'
import * as SecureStore from 'expo-secure-store'

// 4. Third-party imports
import axios from 'axios'

// 5. Local imports - use @ alias
import { Button } from '@/components/ui/Button'
import { useAuth } from '@/hooks/useAuth'
import { Strategy } from '@/lib/types'
```

---

## 5. State Management

### Context Pattern for Auth

```typescript
// contexts/AuthContext.tsx
import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import * as SecureStore from 'expo-secure-store'
import { useRouter } from 'expo-router'

interface User {
  id: string
  email: string
  role: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  register: (email: string, password: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  
  useEffect(() => {
    checkAuth()
  }, [])
  
  async function checkAuth() {
    try {
      const token = await SecureStore.getItemAsync('token')
      if (token) {
        // Verify token and get user
        const response = await api.get('/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        })
        setUser(response.data)
      }
    } catch (error) {
      await SecureStore.deleteItemAsync('token')
    } finally {
      setIsLoading(false)
    }
  }
  
  async function login(email: string, password: string) {
    const response = await api.post('/auth/login', { email, password })
    await SecureStore.setItemAsync('token', response.data.access_token)
    setUser(response.data.user)
    router.replace('/(tabs)')
  }
  
  async function logout() {
    await SecureStore.deleteItemAsync('token')
    setUser(null)
    router.replace('/(auth)/login')
  }
  
  async function register(email: string, password: string) {
    await api.post('/auth/register', { email, password })
    await login(email, password)
  }
  
  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
```

### Custom Hooks Pattern

```typescript
// hooks/useStrategies.ts
import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import { Strategy } from '@/lib/types'

export function useStrategies() {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    fetchStrategies()
  }, [])
  
  async function fetchStrategies() {
    try {
      setLoading(true)
      const response = await api.getStrategies()
      setStrategies(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to load strategies')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }
  
  async function createStrategy(data: Partial<Strategy>) {
    const response = await api.createStrategy(data)
    setStrategies(prev => [...prev, response.data])
    return response.data
  }
  
  async function startStrategy(id: string) {
    await api.startStrategy(id)
    setStrategies(prev =>
      prev.map(s => s.id === id ? { ...s, status: 'RUNNING' } : s)
    )
  }
  
  async function stopStrategy(id: string) {
    await api.stopStrategy(id)
    setStrategies(prev =>
      prev.map(s => s.id === id ? { ...s, status: 'STOPPED' } : s)
    )
  }
  
  return {
    strategies,
    loading,
    error,
    fetchStrategies,
    createStrategy,
    startStrategy,
    stopStrategy
  }
}
```

---

## 6. API Integration

### API Client Pattern

```typescript
// lib/api.ts
import axios, { AxiosInstance, AxiosError } from 'axios'
import * as SecureStore from 'expo-secure-store'
import { router } from 'expo-router'

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private client: AxiosInstance
  
  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    // Request interceptor - add auth token
    this.client.interceptors.request.use(async (config) => {
      const token = await SecureStore.getItemAsync('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })
    
    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired, clear and redirect to login
          await SecureStore.deleteItemAsync('token')
          router.replace('/(auth)/login')
        }
        return Promise.reject(error)
      }
    )
  }
  
  // Auth endpoints
  async login(email: string, password: string) {
    return this.client.post('/auth/login', { email, password })
  }
  
  async register(email: string, password: string) {
    return this.client.post('/auth/register', { email, password })
  }
  
  async getCurrentUser() {
    return this.client.get('/auth/me')
  }
  
  // Strategy endpoints
  async getStrategies() {
    return this.client.get('/strategies')
  }
  
  async getStrategy(id: string) {
    return this.client.get(`/strategies/${id}`)
  }
  
  async createStrategy(data: Partial<Strategy>) {
    return this.client.post('/strategies', data)
  }
  
  async startStrategy(id: string) {
    return this.client.post(`/strategies/${id}/start`)
  }
  
  async stopStrategy(id: string) {
    return this.client.post(`/strategies/${id}/stop`)
  }
  
  async deleteStrategy(id: string) {
    return this.client.delete(`/strategies/${id}`)
  }
  
  // Broker endpoints
  async getBrokerCredentials() {
    return this.client.get('/brokers/credentials')
  }
  
  async saveBrokerCredentials(data: BrokerCredentials) {
    return this.client.post('/brokers/credentials', data)
  }
}

export const api = new ApiClient()
```

---

## 7. Offline Support

### Network Detection

```typescript
// hooks/useNetworkStatus.ts
import { useState, useEffect } from 'react'
import NetInfo from '@react-native-community/netinfo'

export function useNetworkStatus() {
  const [isOnline, setIsOnline] = useState(true)
  const [networkType, setNetworkType] = useState<string>('unknown')
  
  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsOnline(state.isConnected ?? false)
      setNetworkType(state.type)
    })
    
    return () => unsubscribe()
  }, [])
  
  return { isOnline, networkType }
}
```

### Offline Queue

```typescript
// lib/offlineQueue.ts
import AsyncStorage from '@react-native-async-storage/async-storage'

interface QueuedRequest {
  id: string
  url: string
  method: string
  data?: any
  timestamp: number
}

class OfflineQueue {
  private QUEUE_KEY = '@offline_queue'
  
  async add(request: Omit<QueuedRequest, 'id' | 'timestamp'>) {
    const queue = await this.getQueue()
    const newRequest: QueuedRequest = {
      ...request,
      id: Date.now().toString(),
      timestamp: Date.now()
    }
    queue.push(newRequest)
    await AsyncStorage.setItem(this.QUEUE_KEY, JSON.stringify(queue))
  }
  
  async getQueue(): Promise<QueuedRequest[]> {
    const data = await AsyncStorage.getItem(this.QUEUE_KEY)
    return data ? JSON.parse(data) : []
  }
  
  async processQueue() {
    const queue = await this.getQueue()
    const processed: string[] = []
    
    for (const request of queue) {
      try {
        await api.client.request({
          url: request.url,
          method: request.method,
          data: request.data
        })
        processed.push(request.id)
      } catch (error) {
        console.error('Failed to process queued request:', error)
      }
    }
    
    // Remove processed requests
    const remaining = queue.filter(r => !processed.includes(r.id))
    await AsyncStorage.setItem(this.QUEUE_KEY, JSON.stringify(remaining))
    
    return { processed: processed.length, remaining: remaining.length }
  }
  
  async clear() {
    await AsyncStorage.removeItem(this.QUEUE_KEY)
  }
}

export const offlineQueue = new OfflineQueue()
```

---

## Quick Reference

### Common Mobile Operations

| Task | Code |
|------|------|
| **Secure storage** | `await SecureStore.setItemAsync('key', 'value')` |
| **Navigation** | `router.push('/strategies/123')` |
| **Network status** | `const { isOnline } = useNetworkStatus()` |
| **Alert dialog** | `Alert.alert('Title', 'Message')` |
| **Loading state** | `const [loading, setLoading] = useState(false)` |
| **API call** | `await api.getStrategies()` |
| **Platform check** | `Platform.OS === 'ios'` |

### Environment Variables

```bash
# .env
EXPO_PUBLIC_API_URL=http://localhost:8000
EXPO_PUBLIC_APP_NAME=Algo Trading
```

### Development Commands

```bash
# Install dependencies
npm install

# Start development server
npx expo start

# Run on iOS simulator
npx expo start --ios

# Run on Android emulator
npx expo start --android

# Build for production
eas build --platform all

# Type check
npx tsc --noEmit
```

---

**Last Updated**: December 7, 2025  
**Maintained by**: Mobile Engineering Team  
**Agent**: mobile-app

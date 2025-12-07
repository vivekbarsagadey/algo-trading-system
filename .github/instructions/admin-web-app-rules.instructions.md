---
applyTo: "admin-web/**"
name: "Admin-Web-App-Rules"
description: "Next.js 16 admin web application standards and patterns"
---

# Admin Web App Rules - Algo Trading System

> **Admin App Agent**: This guide contains Next.js 16, TypeScript, NextAuth.js v5, and Shadcn/ui-specific rules for the admin web application.

**Last Updated**: December 7, 2025  
**Stack**: Next.js 16 • TypeScript • NextAuth.js v5 • Shadcn/ui • Tailwind CSS • Server-Sent Events

---

## Table of Contents

1. [Critical Admin Policies](#critical-admin-policies)
2. [Project Structure](#project-structure)
3. [Authentication Patterns](#authentication-patterns)
4. [Code Standards](#code-standards)
5. [Component Patterns](#component-patterns)
6. [API Integration](#api-integration)
7. [Real-Time Updates](#real-time-updates)

---

## 1. Critical Admin Policies

### ⚠️ Policy 1: Role-Based Access Control

**ALL routes MUST enforce role-based access control.**

```typescript
// ✅ REQUIRED - Server component with role check
import { requireRole } from '@/lib/auth'

export default async function AdminPage() {
  const user = await requireRole('Admin')
  
  // Admin-only content
  return <AdminDashboard user={user} />
}

// ❌ FORBIDDEN - No auth check
export default async function AdminPage() {
  return <AdminDashboard />
}
```

### ⚠️ Policy 2: Server Components First

**Use Server Components by default, Client Components only when needed.**

```typescript
// ✅ PREFERRED - Server component (default)
// app/(dashboard)/strategies/page.tsx
import { requireAuth } from '@/lib/auth'
import { getStrategies } from '@/lib/api'

export default async function StrategiesPage() {
  const user = await requireAuth()
  const strategies = await getStrategies(user.id)
  
  return <StrategyList strategies={strategies} />
}

// ✅ ONLY when needed - Client component for interactivity
// components/StrategyCard.tsx
'use client'

import { useState } from 'react'

export function StrategyCard({ strategy }) {
  const [isRunning, setIsRunning] = useState(false)
  
  return <div onClick={() => setIsRunning(!isRunning)}>...</div>
}
```

### ⚠️ Policy 3: Type Safety Everywhere

**ALL components, functions, and API calls MUST be fully typed.**

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

interface StrategyListProps {
  strategies: Strategy[]
  onStrategySelect?: (strategy: Strategy) => void
}

export function StrategyList({ strategies, onStrategySelect }: StrategyListProps) {
  return (
    <div>
      {strategies.map((strategy) => (
        <div key={strategy.id} onClick={() => onStrategySelect?.(strategy)}>
          {strategy.symbol}
        </div>
      ))}
    </div>
  )
}
```

### ⚠️ Policy 4: API Requests Must Be Authenticated

**ALL backend API requests MUST include JWT token.**

```typescript
// ✅ REQUIRED - Authenticated API call
async function getStrategies(userId: string): Promise<Strategy[]> {
  const session = await getServerSession(authOptions)
  
  const response = await fetch(`${process.env.BACKEND_URL}/strategies?user_id=${userId}`, {
    headers: {
      'Authorization': `Bearer ${session?.accessToken}`,
      'Content-Type': 'application/json'
    }
  })
  
  if (!response.ok) {
    throw new Error('Failed to fetch strategies')
  }
  
  return response.json()
}
```

### ⚠️ Policy 5: Environment Variables Convention

**Use Next.js environment variable conventions.**

```bash
# Public variables (accessible in browser)
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Private variables (server-side only)
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-here
BACKEND_API_KEY=internal-api-key
```

```typescript
// ✅ CORRECT - Public variable in client component
'use client'

export function ApiStatus() {
  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL
  return <div>Backend: {backendUrl}</div>
}

// ✅ CORRECT - Private variable in server component
import { getServerSession } from 'next-auth'

export default async function AdminPage() {
  const apiKey = process.env.BACKEND_API_KEY  // Server-side only
  // ...
}
```

---

## 2. Project Structure

### Admin Web Directory Layout

```
admin-web/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx           # Login page
│   │   └── register/
│   │       └── page.tsx           # Registration page
│   ├── (dashboard)/
│   │   ├── layout.tsx             # Dashboard layout (requires auth)
│   │   ├── page.tsx               # Dashboard home
│   │   ├── strategies/
│   │   │   ├── page.tsx           # Strategy list
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx       # Strategy detail
│   │   │   └── new/
│   │   │       └── page.tsx       # Create strategy
│   │   ├── users/
│   │   │   └── page.tsx           # User management (Admin only)
│   │   ├── brokers/
│   │   │   └── page.tsx           # Broker setup
│   │   └── playground/
│   │       └── page.tsx           # Strategy playground
│   ├── api/
│   │   ├── auth/
│   │   │   └── [...nextauth]/
│   │   │       └── route.ts       # NextAuth.js configuration
│   │   ├── strategies/
│   │   │   ├── route.ts           # Proxy to backend
│   │   │   └── [id]/
│   │   │       └── stream/
│   │   │           └── route.ts   # SSE endpoint
│   │   └── users/
│   │       └── route.ts           # Proxy to backend
│   ├── layout.tsx                 # Root layout
│   └── middleware.ts              # Route protection
├── components/
│   ├── ui/                        # Shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   └── ...
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── ProtectedRoute.tsx
│   ├── strategies/
│   │   ├── StrategyList.tsx
│   │   ├── StrategyCard.tsx
│   │   ├── StrategyForm.tsx
│   │   └── StrategyStream.tsx
│   ├── admin/
│   │   ├── UserTable.tsx
│   │   └── UserActions.tsx
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
├── lib/
│   ├── auth.ts                    # Auth utilities
│   ├── api.ts                     # API client
│   ├── validators.ts              # Zod schemas
│   ├── types.ts                   # TypeScript types
│   └── utils.ts                   # Utility functions
├── hooks/
│   ├── useStrategyStream.ts       # SSE hook
│   ├── useStrategies.ts           # Strategy data hook
│   └── useAuth.ts                 # Auth hook
├── styles/
│   └── globals.css                # Global styles
├── public/
├── .env.local                     # Environment variables
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## 3. Authentication Patterns

### NextAuth.js v5 Configuration

```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'

export const authOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        // Call backend API
        const response = await fetch(`${process.env.BACKEND_URL}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: credentials?.email,
            password: credentials?.password
          })
        })
        
        if (!response.ok) {
          throw new Error('Invalid credentials')
        }
        
        const data = await response.json()
        
        return {
          id: data.user.id,
          email: data.user.email,
          role: data.user.role,
          accessToken: data.access_token
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
        token.role = user.role
        token.accessToken = user.accessToken
      }
      return token
    },
    async session({ session, token }) {
      session.user.id = token.id as string
      session.user.role = token.role as string
      session.accessToken = token.accessToken as string
      return session
    }
  },
  pages: {
    signIn: '/login',
    error: '/login'
  }
}

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }
```

### Auth Helper Functions

```typescript
// lib/auth.ts
import { getServerSession } from 'next-auth'
import { redirect } from 'next/navigation'
import { authOptions } from '@/app/api/auth/[...nextauth]/route'

export async function getCurrentUser() {
  const session = await getServerSession(authOptions)
  return session?.user
}

export async function requireAuth() {
  const user = await getCurrentUser()
  if (!user) {
    redirect('/login')
  }
  return user
}

export async function requireRole(role: string) {
  const user = await requireAuth()
  if (user.role !== role) {
    redirect('/dashboard')
  }
  return user
}

export async function requireAnyRole(roles: string[]) {
  const user = await requireAuth()
  if (!roles.includes(user.role)) {
    redirect('/dashboard')
  }
  return user
}
```

### Middleware Pattern

```typescript
// middleware.ts
import { NextRequest, NextResponse } from 'next/server'
import { getToken } from 'next-auth/jwt'

export async function middleware(req: NextRequest) {
  const token = await getToken({ req })
  const path = req.nextUrl.pathname
  
  // Public routes
  const publicPaths = ['/login', '/register']
  if (publicPaths.some(p => path.startsWith(p))) {
    // Redirect to dashboard if already logged in
    if (token) {
      return NextResponse.redirect(new URL('/dashboard', req.url))
    }
    return NextResponse.next()
  }
  
  // Protected routes
  if (path.startsWith('/dashboard') || path.startsWith('/strategies')) {
    if (!token) {
      return NextResponse.redirect(new URL('/login', req.url))
    }
  }
  
  // Admin-only routes
  if (path.startsWith('/users')) {
    if (!token || token.role !== 'Admin') {
      return NextResponse.redirect(new URL('/dashboard', req.url))
    }
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)']
}
```

---

## 4. Code Standards

### TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "dom", "dom.iterable"],
    "jsx": "preserve",
    "module": "esnext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

### Naming Conventions

```typescript
// Files: kebab-case
// components/strategy-card.tsx
// lib/api-client.ts
// hooks/use-strategies.ts

// Components: PascalCase
export function StrategyCard() {}
export function UserManagement() {}

// Functions/Variables: camelCase
const getCurrentUser = () => {}
const strategyList = []

// Constants: UPPER_SNAKE_CASE
const MAX_STRATEGIES = 100
const DEFAULT_TIMEOUT = 5000

// Types/Interfaces: PascalCase
interface Strategy {}
type UserRole = 'Admin' | 'User' | 'Broker'
```

### Import Organization

```typescript
// 1. React imports
import { useState, useEffect } from 'react'

// 2. Next.js imports
import { redirect } from 'next/navigation'
import Link from 'next/link'

// 3. Third-party imports
import { useSession } from 'next-auth/react'
import { z } from 'zod'

// 4. Local imports - absolute paths with @/
import { Button } from '@/components/ui/button'
import { requireAuth } from '@/lib/auth'
import { Strategy } from '@/lib/types'
```

---

## 5. Component Patterns

### Server Component Pattern

```typescript
// app/(dashboard)/strategies/page.tsx
import { requireAuth } from '@/lib/auth'
import { getStrategies } from '@/lib/api'
import { StrategyList } from '@/components/strategies/StrategyList'

export default async function StrategiesPage() {
  const user = await requireAuth()
  const strategies = await getStrategies(user.id)
  
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">My Strategies</h1>
      <StrategyList strategies={strategies} />
    </div>
  )
}
```

### Client Component Pattern

```typescript
// components/strategies/StrategyCard.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Strategy } from '@/lib/types'

interface StrategyCardProps {
  strategy: Strategy
  onStart: (id: string) => Promise<void>
  onStop: (id: string) => Promise<void>
}

export function StrategyCard({ strategy, onStart, onStop }: StrategyCardProps) {
  const [isLoading, setIsLoading] = useState(false)
  
  const handleToggle = async () => {
    setIsLoading(true)
    try {
      if (strategy.status === 'RUNNING') {
        await onStop(strategy.id)
      } else {
        await onStart(strategy.id)
      }
    } catch (error) {
      console.error('Failed to toggle strategy:', error)
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>{strategy.symbol}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <p>Buy Time: {strategy.buyTime}</p>
          <p>Sell Time: {strategy.sellTime}</p>
          <p>Stop Loss: ₹{strategy.stopLoss}</p>
          <Button 
            onClick={handleToggle} 
            disabled={isLoading}
            variant={strategy.status === 'RUNNING' ? 'destructive' : 'default'}
          >
            {isLoading ? 'Loading...' : strategy.status === 'RUNNING' ? 'Stop' : 'Start'}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
```

### Form Pattern with Validation

```typescript
// components/strategies/StrategyForm.tsx
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'

const strategySchema = z.object({
  symbol: z.string().min(1, 'Symbol is required'),
  buyTime: z.string().regex(/^\d{2}:\d{2}:\d{2}$/, 'Invalid time format (HH:MM:SS)'),
  sellTime: z.string().regex(/^\d{2}:\d{2}:\d{2}$/, 'Invalid time format (HH:MM:SS)'),
  stopLoss: z.number().positive('Stop-loss must be positive'),
  quantity: z.number().int().positive('Quantity must be positive')
})

type StrategyFormData = z.infer<typeof strategySchema>

interface StrategyFormProps {
  onSubmit: (data: StrategyFormData) => Promise<void>
}

export function StrategyForm({ onSubmit }: StrategyFormProps) {
  const form = useForm<StrategyFormData>({
    resolver: zodResolver(strategySchema),
    defaultValues: {
      symbol: '',
      buyTime: '09:15:00',
      sellTime: '15:30:00',
      stopLoss: 0,
      quantity: 1
    }
  })
  
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="symbol"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Symbol</FormLabel>
              <FormControl>
                <Input placeholder="RELIANCE" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <FormField
          control={form.control}
          name="stopLoss"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Stop Loss (₹)</FormLabel>
              <FormControl>
                <Input 
                  type="number" 
                  placeholder="2500.00" 
                  {...field}
                  onChange={e => field.onChange(parseFloat(e.target.value))}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        
        <Button type="submit" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? 'Creating...' : 'Create Strategy'}
        </Button>
      </form>
    </Form>
  )
}
```

---

## 6. API Integration

### API Client Pattern

```typescript
// lib/api.ts
import { getSession } from 'next-auth/react'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL

class ApiClient {
  private async getHeaders(): Promise<HeadersInit> {
    const session = await getSession()
    return {
      'Content-Type': 'application/json',
      ...(session?.accessToken && {
        'Authorization': `Bearer ${session.accessToken}`
      })
    }
  }
  
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers = await this.getHeaders()
    
    const response = await fetch(`${BACKEND_URL}${endpoint}`, {
      ...options,
      headers: {
        ...headers,
        ...options.headers
      }
    })
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }))
      throw new Error(error.message || 'API request failed')
    }
    
    return response.json()
  }
  
  // Strategy operations
  async getStrategies(userId?: string): Promise<Strategy[]> {
    const query = userId ? `?user_id=${userId}` : ''
    return this.request(`/strategies${query}`)
  }
  
  async getStrategy(id: string): Promise<Strategy> {
    return this.request(`/strategies/${id}`)
  }
  
  async createStrategy(data: CreateStrategyData): Promise<Strategy> {
    return this.request('/strategies', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }
  
  async startStrategy(id: string): Promise<void> {
    return this.request(`/strategies/${id}/start`, { method: 'POST' })
  }
  
  async stopStrategy(id: string): Promise<void> {
    return this.request(`/strategies/${id}/stop`, { method: 'POST' })
  }
  
  // User operations (Admin only)
  async getUsers(): Promise<User[]> {
    return this.request('/users')
  }
  
  async updateUserRole(userId: string, role: string): Promise<User> {
    return this.request(`/users/${userId}/role`, {
      method: 'PATCH',
      body: JSON.stringify({ role })
    })
  }
}

export const apiClient = new ApiClient()
```

### Server Action Pattern

```typescript
// app/(dashboard)/strategies/actions.ts
'use server'

import { revalidatePath } from 'next/cache'
import { requireAuth } from '@/lib/auth'
import { apiClient } from '@/lib/api'

export async function createStrategy(formData: FormData) {
  const user = await requireAuth()
  
  const data = {
    symbol: formData.get('symbol') as string,
    buyTime: formData.get('buyTime') as string,
    sellTime: formData.get('sellTime') as string,
    stopLoss: parseFloat(formData.get('stopLoss') as string),
    quantity: parseInt(formData.get('quantity') as string)
  }
  
  try {
    await apiClient.createStrategy(data)
    revalidatePath('/strategies')
    return { success: true }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
}

export async function startStrategy(strategyId: string) {
  await requireAuth()
  
  try {
    await apiClient.startStrategy(strategyId)
    revalidatePath('/strategies')
    return { success: true }
  } catch (error) {
    return { success: false, error: (error as Error).message }
  }
}
```

---

## 7. Real-Time Updates

### Server-Sent Events (SSE) Hook

```typescript
// hooks/useStrategyStream.ts
'use client'

import { useEffect, useState } from 'react'

interface StrategyStreamData {
  strategyId: string
  status: string
  currentPrice: number
  lastAction: string
  timestamp: string
}

export function useStrategyStream(strategyId: string) {
  const [data, setData] = useState<StrategyStreamData | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    const eventSource = new EventSource(
      `/api/strategies/${strategyId}/stream`
    )
    
    eventSource.onopen = () => {
      setIsConnected(true)
      setError(null)
    }
    
    eventSource.onmessage = (event) => {
      try {
        const parsedData = JSON.parse(event.data)
        setData(parsedData)
      } catch (err) {
        console.error('Failed to parse SSE data:', err)
      }
    }
    
    eventSource.onerror = () => {
      setIsConnected(false)
      setError('Connection lost')
      eventSource.close()
    }
    
    return () => {
      eventSource.close()
      setIsConnected(false)
    }
  }, [strategyId])
  
  return { data, isConnected, error }
}
```

### SSE API Route

```typescript
// app/api/strategies/[id]/stream/route.ts
import { NextRequest } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/app/api/auth/[...nextauth]/route'

export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  const session = await getServerSession(authOptions)
  
  if (!session) {
    return new Response('Unauthorized', { status: 401 })
  }
  
  const encoder = new TextEncoder()
  
  const stream = new ReadableStream({
    async start(controller) {
      // Connect to backend SSE endpoint
      const response = await fetch(
        `${process.env.BACKEND_URL}/strategies/${params.id}/stream`,
        {
          headers: {
            'Authorization': `Bearer ${session.accessToken}`
          }
        }
      )
      
      if (!response.ok || !response.body) {
        controller.close()
        return
      }
      
      const reader = response.body.getReader()
      
      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          
          controller.enqueue(value)
        }
      } catch (error) {
        console.error('Stream error:', error)
      } finally {
        controller.close()
      }
    }
  })
  
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    }
  })
}
```

---

## Quick Reference

### Common Admin Operations

| Task | Code |
|------|------|
| **Get current user** | `const user = await getCurrentUser()` |
| **Require auth** | `const user = await requireAuth()` |
| **Require role** | `const user = await requireRole('Admin')` |
| **Client auth** | `const { data: session } = useSession()` |
| **API call** | `await apiClient.getStrategies()` |
| **Revalidate** | `revalidatePath('/strategies')` |
| **Redirect** | `redirect('/dashboard')` |
| **SSE stream** | `const { data } = useStrategyStream(id)` |

### Environment Variables

```bash
# Public (accessible in browser)
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Algo Trading Admin

# Private (server-side only)
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here
BACKEND_API_KEY=internal-api-key
```

### Development Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type check
npm run type-check

# Lint
npm run lint
```

---

**Last Updated**: December 7, 2025  
**Maintained by**: Frontend Engineering Team  
**Agent**: admin-app

# Frontend Architecture Guide

## Overview

This document outlines the technical architecture decisions, patterns, and infrastructure for the Shepherd frontend application.

## Technology Stack

### Core Framework
- **React 18+** with function components and hooks
- **TypeScript 5+** for type safety and developer experience
- **Vite 5+** for fast development and optimized builds

### UI & Styling
- **Tailwind CSS v4** for utility-first styling
- **shadcn/ui** component library built on Radix UI primitives
- **Lucide React** for consistent iconography
- **CSS Custom Properties** for dynamic theming

### State & Data Management
- **TanStack Query (React Query)** for server state management
- **React Context** for global application state
- **Supabase Client** for real-time data and authentication

### Routing & Navigation
- **React Router v6** with modern data loading patterns
- **Nested routes** for complex page layouts
- **Protected routes** with authentication guards

## Application Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── ui/              # Base UI components (shadcn/ui)
│   │   ├── layout/          # Layout components
│   │   └── features/        # Feature-specific components
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utilities and configurations
│   ├── pages/               # Route components
│   ├── styles/              # Global styles and themes
│   └── types/               # Shared TypeScript types
├── public/                  # Static assets
└── build configuration files
```

## Routing Strategy

### Route Structure

Modern React Router v6 with data loading:

```typescript
const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    errorElement: <ErrorPage />,
    children: [
      {
        index: true,
        element: <HomePage />
      },
      {
        path: "dashboard",
        element: <ProtectedRoute><DashboardPage /></ProtectedRoute>
      },
      {
        path: "jobs/:id",
        element: <ProtectedRoute><JobDetailsPage /></ProtectedRoute>,
        loader: async ({ params }) => {
          return queryClient.ensureQueryData({
            queryKey: ['job', params.id],
            queryFn: () => fetchJob(params.id!)
          })
        }
      }
    ]
  }
])
```

### Authentication Guards

```typescript
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) return <PageLoader />
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <>{children}</>
}
```

## Build Configuration

### Vite Configuration

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          supabase: ['@supabase/supabase-js'],
          ui: ['@radix-ui/react-slot', '@radix-ui/react-dialog']
        }
      }
    }
  }
})
```

### Environment Configuration

```bash
# Environment variables
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_APP_ENVIRONMENT=development
```

## TypeScript Configuration

### Base Types

```typescript
// lib/types.ts - Shared type definitions
export interface Job {
  id: string
  user_id: string
  title: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  input_type: 'youtube' | 'audio_file' | 'text'
  settings: JobSettings
  created_at: string
  updated_at: string
}

export interface JobSettings {
  chunk_size_minutes: number
  word_limit: number
  custom_instructions?: string
  model_preference?: string
}

export interface User {
  id: string
  email: string
  credits: number
  daily_quota: number
  quota_used_today: number
}
```

### TypeScript Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

## Data Integration

### Supabase Integration

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### Query Patterns

```typescript
// hooks/use-jobs.ts
export const useJobs = () => {
  return useQuery({
    queryKey: ['jobs'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('jobs')
        .select('*')
        .order('created_at', { ascending: false })

      if (error) throw error
      return data
    }
  })
}

export const useJob = (id: string) => {
  return useQuery({
    queryKey: ['job', id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('jobs')
        .select('*')
        .eq('id', id)
        .single()

      if (error) throw error
      return data
    }
  })
}
```

## Styling Architecture

### Tailwind Configuration

```typescript
// tailwind.config.ts
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
  ],
}
```

### CSS Custom Properties

```css
/* styles/globals.css */
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 222.2 84% 4.9%;
  --primary-foreground: 210 40% 98%;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
}
```

## Error Handling

### Error Boundaries

```typescript
// components/error-boundary.tsx
class ErrorBoundary extends Component<PropsWithChildren, { hasError: boolean }> {
  constructor(props: PropsWithChildren) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(): { hasError: boolean } {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback />
    }

    return this.props.children
  }
}
```

### Query Error Handling

```typescript
// hooks/use-jobs.ts with error handling
export const useJobs = () => {
  return useQuery({
    queryKey: ['jobs'],
    queryFn: fetchJobs,
    retry: (failureCount, error) => {
      // Don't retry on authentication errors
      if (error?.message?.includes('auth')) return false
      return failureCount < 3
    },
    onError: (error) => {
      toast.error(`Failed to load jobs: ${error.message}`)
    }
  })
}
```

This architecture guide provides the technical foundation for building and maintaining the Shepherd frontend application with modern React patterns and best practices.

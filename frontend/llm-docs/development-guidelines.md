# Frontend Development Guidelines

## Overview

This document outlines the development practices and conventions for the Shepherd frontend application. These guidelines ensure consistency, maintainability, and code quality across the project.

## Table of Contents

- [Component Architecture](#component-architecture)
- [Code Organization](#code-organization)
- [State Management](#state-management)
- [Styling Guidelines](#styling-guidelines)
- [TypeScript Conventions](#typescript-conventions)
- [Performance Best Practices](#performance-best-practices)
- [Testing Strategy](#testing-strategy)
- [Accessibility Standards](#accessibility-standards)

## Component Architecture

### Design Principles

Based on modern React best practices:

- **Composition over inheritance** - Use React's component composition patterns
- **Single responsibility** - Each component should have one clear purpose
- **Functional components with hooks** - Prefer function components over class components
- **Explicit prop interfaces** - Define clear TypeScript interfaces for all props

### Component Categories

#### 1. UI Components (`src/components/ui/`)
Reusable, unstyled base components from shadcn/ui:

```typescript
// Example: Button component with variants
interface ButtonProps {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  children: React.ReactNode
  onClick?: () => void
  disabled?: boolean
}

const Button = ({ variant = 'default', size = 'default', ...props }: ButtonProps) => {
  return (
    <button
      className={cn(buttonVariants({ variant, size }))}
      {...props}
    />
  )
}
```

#### 2. Layout Components (`src/components/layout/`)
Structural components for consistent page layouts:

```typescript
// Use context for shared layout state
const Header = () => {
  const { user, signOut } = useAuth()

  return (
    <header className="border-b bg-background/95 backdrop-blur">
      <div className="container flex h-14 items-center">
        <Logo />
        <MainNav />
        <div className="ml-auto flex items-center space-x-4">
          <UserNav user={user} onSignOut={signOut} />
        </div>
      </div>
    </header>
  )
}
```

#### 3. Feature Components (`src/components/features/`)
Business logic components organized by domain:

```typescript
// Example: Feature component with data fetching
interface JobStatusProps {
  jobId: string
}

const JobStatus = ({ jobId }: JobStatusProps) => {
  const { data: job, isLoading, error } = useJob(jobId)

  if (isLoading) return <JobStatusSkeleton />
  if (error) return <ErrorMessage error={error} />

  return (
    <Card>
      <CardHeader>
        <CardTitle>Job Status</CardTitle>
      </CardHeader>
      <CardContent>
        <StatusBadge status={job.status} />
        <ProgressBar progress={job.progress} />
      </CardContent>
    </Card>
  )
}
```

## Code Organization

### File Structure Conventions

```
src/
├── components/
│   ├── ui/              # Reusable UI primitives
│   ├── layout/          # Layout-specific components
│   └── features/        # Domain-specific components
├── hooks/               # Custom React hooks
├── lib/                 # Utilities and configurations
├── pages/               # Route components (page-level)
├── styles/              # Global styles
└── types/               # Shared TypeScript definitions
```

### Import/Export Patterns

- Use **default exports** for main components
- Use **named exports** for utilities and multiple related items
- Import order: external libraries → internal modules → relative imports

```typescript
// ✅ Good import structure
import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { useAuth } from '@/hooks/use-auth'
import { JobStatus } from './job-status'
```

### Component File Organization

Each component should follow this structure:

```typescript
// 1. Imports
import { useState } from 'react'
import { Button } from '@/components/ui/button'

// 2. Types/Interfaces
interface ComponentProps {
  // props definition
}

// 3. Component definition
const Component = ({ prop }: ComponentProps) => {
  // hooks
  // event handlers
  // render logic
  return <div>...</div>
}

// 4. Export
export default Component
```

## State Management

### Context Usage

Use React Context for:
- Authentication state
- Theme preferences
- Global UI state (modals, notifications)

```typescript
// ✅ Proper context definition
interface AuthContextType {
  user: User | null
  session: Session | null
  signIn: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
```

### Server State Management

Use TanStack Query for:
- API data fetching
- Caching and synchronization
- Background updates

```typescript
// ✅ Query hook pattern
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
```

## Performance Best Practices

### Component Optimization

1. **Avoid nested component definitions**:
```typescript
// ❌ Bad - component defined inside render
const Gallery = () => {
  const Profile = () => <div>...</div> // Don't do this
  return <Profile />
}

// ✅ Good - component defined outside
const Profile = () => <div>...</div>
const Gallery = () => <Profile />
```

2. **Use proper key props for lists**:
```typescript
// ✅ Good - stable, unique keys
{items.map(item => (
  <Item key={item.id} data={item} />
))}
```

3. **Implement code splitting**:
```typescript
// ✅ Route-based code splitting
const DashboardPage = lazy(() => import('./pages/dashboard'))

// Usage with Suspense
<Suspense fallback={<PageLoader />}>
  <DashboardPage />
</Suspense>
```

### Bundle Optimization

Configure Vite for optimal bundling:

```typescript
// vite.config.ts
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
```

## Development Workflow

### Code Quality Tools

- **ESLint** with React and TypeScript rules
- **Prettier** for consistent formatting
- **TypeScript** for type safety
- **Husky** for git hooks

### Pre-commit Checks

Ensure code quality with automated checks:

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Format check
npm run format:check
```

This document provides the foundation for consistent, maintainable React development following modern best practices and patterns demonstrated by the React community.

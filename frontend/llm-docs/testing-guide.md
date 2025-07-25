# Testing Guide

## Overview

This document outlines the testing strategy, tools, and best practices for ensuring code quality and reliability in the Shepherd frontend application.

## Testing Strategy

### Testing Pyramid

```
                    E2E Tests (Playwright)
                   /                    \
              Integration Tests (RTL)
             /                        \
        Unit Tests (Vitest + RTL)
       /                            \
  Static Analysis (TypeScript + ESLint)
```

### Test Categories

1. **Unit Tests** - Individual functions, hooks, and components
2. **Integration Tests** - Component interactions and user workflows
3. **End-to-End Tests** - Complete user journeys across the application
4. **Static Analysis** - Type checking and code quality

## Testing Tools

### Core Testing Stack

- **Vitest** - Fast unit test runner with Vite integration
- **React Testing Library** - Component testing utilities
- **@testing-library/jest-dom** - Custom Jest matchers
- **@testing-library/user-event** - User interaction simulation
- **MSW (Mock Service Worker)** - API mocking
- **Playwright** - End-to-end testing

### Setup Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
})
```

```typescript
// src/test/setup.ts
import '@testing-library/jest-dom'
import { server } from './mocks/server'

// Start API mocking
beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

## Unit Testing

### Component Testing

```typescript
// components/ui/button.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './button'

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument()
  })

  it('calls onClick handler when clicked', async () => {
    const user = userEvent.setup()
    const handleClick = vi.fn()

    render(<Button onClick={handleClick}>Click me</Button>)

    await user.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Disabled</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('applies correct variant styles', () => {
    render(<Button variant="destructive">Delete</Button>)
    expect(screen.getByRole('button')).toHaveClass('bg-destructive')
  })
})
```

### Hook Testing

```typescript
// hooks/use-auth.test.ts
import { renderHook, waitFor } from '@testing-library/react'
import { useAuth } from './use-auth'
import { AuthProvider } from '@/components/auth-provider'

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
)

describe('useAuth', () => {
  it('returns user when authenticated', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => {
      expect(result.current.user).toEqual({
        id: '1',
        email: 'test@example.com'
      })
    })
  })

  it('handles sign in correctly', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper })

    await result.current.signIn('test@example.com', 'password')

    await waitFor(() => {
      expect(result.current.user).toBeTruthy()
    })
  })
})
```

### Utility Function Testing

```typescript
// lib/utils.test.ts
import { cn, formatDate, truncateText } from './utils'

describe('utils', () => {
  describe('cn', () => {
    it('combines class names correctly', () => {
      expect(cn('base', 'additional')).toBe('base additional')
    })

    it('handles conditional classes', () => {
      expect(cn('base', false && 'hidden', 'visible')).toBe('base visible')
    })
  })

  describe('formatDate', () => {
    it('formats date correctly', () => {
      const date = new Date('2024-01-15T10:30:00Z')
      expect(formatDate(date)).toBe('Jan 15, 2024')
    })
  })

  describe('truncateText', () => {
    it('truncates long text', () => {
      const longText = 'This is a very long text that should be truncated'
      expect(truncateText(longText, 20)).toBe('This is a very long...')
    })

    it('returns original text if shorter than limit', () => {
      const shortText = 'Short text'
      expect(truncateText(shortText, 20)).toBe('Short text')
    })
  })
})
```

## Integration Testing

### Form Testing

```typescript
// components/forms/login-form.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LoginForm } from './login-form'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

const renderWithProviders = (ui: React.ReactElement) => {
  const queryClient = createTestQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  )
}

describe('LoginForm', () => {
  it('submits form with correct data', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()

    renderWithProviders(<LoginForm onSubmit={onSubmit} />)

    await user.type(screen.getByLabelText(/email/i), 'test@example.com')
    await user.type(screen.getByLabelText(/password/i), 'password123')
    await user.click(screen.getByRole('button', { name: /sign in/i }))

    expect(onSubmit).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123'
    })
  })

  it('shows validation errors for invalid input', async () => {
    const user = userEvent.setup()

    renderWithProviders(<LoginForm onSubmit={vi.fn()} />)

    await user.click(screen.getByRole('button', { name: /sign in/i }))

    expect(screen.getByText(/email is required/i)).toBeInTheDocument()
    expect(screen.getByText(/password is required/i)).toBeInTheDocument()
  })
})
```

### Data Fetching Testing

```typescript
// hooks/use-jobs.test.ts
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useJobs } from './use-jobs'
import { server } from '@/test/mocks/server'
import { http, HttpResponse } from 'msw'

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  })

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

describe('useJobs', () => {
  it('fetches jobs successfully', async () => {
    server.use(
      http.get('/api/jobs', () => {
        return HttpResponse.json([
          { id: '1', title: 'Job 1', status: 'completed' },
          { id: '2', title: 'Job 2', status: 'pending' }
        ])
      })
    )

    const { result } = renderHook(() => useJobs(), {
      wrapper: createWrapper()
    })

    await waitFor(() => {
      expect(result.current.data).toHaveLength(2)
    })

    expect(result.current.data[0].title).toBe('Job 1')
  })

  it('handles error states', async () => {
    server.use(
      http.get('/api/jobs', () => {
        return new HttpResponse(null, { status: 500 })
      })
    )

    const { result } = renderHook(() => useJobs(), {
      wrapper: createWrapper()
    })

    await waitFor(() => {
      expect(result.current.error).toBeTruthy()
    })
  })
})
```

## API Mocking with MSW

### Mock Setup

```typescript
// test/mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  // Authentication
  http.post('/auth/signin', async ({ request }) => {
    const { email, password } = await request.json()

    if (email === 'test@example.com' && password === 'password') {
      return HttpResponse.json({
        user: { id: '1', email: 'test@example.com' },
        session: { access_token: 'mock-token' }
      })
    }

    return new HttpResponse(null, { status: 401 })
  }),

  // Jobs
  http.get('/api/jobs', () => {
    return HttpResponse.json([
      {
        id: '1',
        title: 'Sample Job',
        status: 'completed',
        created_at: '2024-01-15T10:00:00Z'
      }
    ])
  }),

  http.get('/api/jobs/:id', ({ params }) => {
    return HttpResponse.json({
      id: params.id,
      title: 'Job Details',
      status: 'processing',
      progress: 75
    })
  }),

  // Error simulation
  http.get('/api/error', () => {
    return new HttpResponse(null, { status: 500 })
  })
]
```

```typescript
// test/mocks/server.ts
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)
```

## End-to-End Testing with Playwright

### E2E Test Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
})
```

### E2E Test Examples

```typescript
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Authentication', () => {
  test('user can sign in', async ({ page }) => {
    await page.goto('/login')

    await page.fill('[data-testid="email-input"]', 'test@example.com')
    await page.fill('[data-testid="password-input"]', 'password123')
    await page.click('[data-testid="signin-button"]')

    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
  })

  test('shows error for invalid credentials', async ({ page }) => {
    await page.goto('/login')

    await page.fill('[data-testid="email-input"]', 'wrong@example.com')
    await page.fill('[data-testid="password-input"]', 'wrongpassword')
    await page.click('[data-testid="signin-button"]')

    await expect(page.locator('[data-testid="error-message"]')).toBeVisible()
  })
})
```

```typescript
// e2e/jobs.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Job Management', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.goto('/login')
    await page.fill('[data-testid="email-input"]', 'test@example.com')
    await page.fill('[data-testid="password-input"]', 'password123')
    await page.click('[data-testid="signin-button"]')
    await expect(page).toHaveURL('/dashboard')
  })

  test('user can create a new job', async ({ page }) => {
    await page.click('[data-testid="new-job-button"]')

    await page.fill('[data-testid="job-title"]', 'Test Job')
    await page.selectOption('[data-testid="input-type"]', 'youtube')
    await page.fill('[data-testid="youtube-url"]', 'https://youtube.com/watch?v=test')

    await page.click('[data-testid="submit-job"]')

    await expect(page.locator('[data-testid="job-created-toast"]')).toBeVisible()
    await expect(page).toHaveURL('/dashboard')
  })

  test('user can view job details', async ({ page }) => {
    await page.click('[data-testid="job-item"]:first-child')

    await expect(page).toHaveURL(/\/jobs\/\w+/)
    await expect(page.locator('[data-testid="job-status"]')).toBeVisible()
    await expect(page.locator('[data-testid="job-progress"]')).toBeVisible()
  })
})
```

## Test Utilities

### Custom Render Function

```typescript
// test/utils.tsx
import { render } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '@/components/auth-provider'

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

export const renderWithProviders = (
  ui: React.ReactElement,
  options?: { queryClient?: QueryClient }
) => {
  const queryClient = options?.queryClient ?? createTestQueryClient()

  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          {children}
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )

  return render(ui, { wrapper: Wrapper })
}
```

## Testing Best Practices

### 1. Test Structure

```typescript
// Follow AAA pattern: Arrange, Act, Assert
describe('Component', () => {
  it('should do something when condition is met', () => {
    // Arrange
    const props = { value: 'test' }

    // Act
    render(<Component {...props} />)

    // Assert
    expect(screen.getByText('test')).toBeInTheDocument()
  })
})
```

### 2. User-Centric Testing

```typescript
// ✅ Good - test user interactions
await user.click(screen.getByRole('button', { name: /submit/i }))

// ❌ Avoid - testing implementation details
fireEvent.click(screen.getByTestId('submit-button'))
```

### 3. Async Testing

```typescript
// ✅ Good - wait for changes
await waitFor(() => {
  expect(screen.getByText('Loading complete')).toBeInTheDocument()
})

// ❌ Avoid - not waiting for async updates
expect(screen.getByText('Loading complete')).toBeInTheDocument()
```

### 4. Mock External Dependencies

```typescript
// Mock external libraries
vi.mock('@supabase/supabase-js', () => ({
  createClient: vi.fn(() => ({
    auth: {
      signIn: vi.fn(),
      signOut: vi.fn(),
    },
    from: vi.fn(() => ({
      select: vi.fn(),
      insert: vi.fn(),
    })),
  })),
}))
```

## Coverage and Quality Gates

### Coverage Configuration

```json
// vitest.config.ts
test: {
  coverage: {
    provider: 'v8',
    reporter: ['text', 'html', 'lcov'],
    thresholds: {
      global: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80
      }
    }
  }
}
```

### CI Integration

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:coverage
      - run: npm run test:e2e
```

This testing guide provides comprehensive coverage for maintaining code quality and reliability in the Shepherd frontend application.

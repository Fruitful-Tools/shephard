# Styling Guide

## Overview

This document outlines the styling approach, design system, and visual guidelines for the Shepherd frontend application.

## Design System

### Color Palette

Based on CSS custom properties for theme switching:

```css
:root {
  /* Base colors */
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;

  /* UI colors */
  --primary: 222.2 84% 4.9%;
  --primary-foreground: 210 40% 98%;
  --secondary: 210 40% 96%;
  --secondary-foreground: 222.2 84% 4.9%;

  /* Status colors */
  --destructive: 0 84% 60%;
  --destructive-foreground: 210 40% 98%;
  --success: 142 76% 36%;
  --success-foreground: 210 40% 98%;

  /* Interactive colors */
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --primary: 210 40% 98%;
  --primary-foreground: 222.2 84% 4.9%;
  /* ... dark theme values */
}
```

### Typography

```css
/* Font families */
font-family: {
  sans: ['Inter', 'sans-serif'],
  mono: ['JetBrains Mono', 'monospace'],
}

/* Font scales */
.text-xs { font-size: 0.75rem; line-height: 1rem; }
.text-sm { font-size: 0.875rem; line-height: 1.25rem; }
.text-base { font-size: 1rem; line-height: 1.5rem; }
.text-lg { font-size: 1.125rem; line-height: 1.75rem; }
.text-xl { font-size: 1.25rem; line-height: 1.75rem; }
.text-2xl { font-size: 1.5rem; line-height: 2rem; }
.text-3xl { font-size: 1.875rem; line-height: 2.25rem; }
```

### Spacing Scale

Following Tailwind's consistent spacing system:

```
4px  = space-1    16px = space-4    64px = space-16
8px  = space-2    24px = space-6    80px = space-20
12px = space-3    32px = space-8    96px = space-24
```

## Component Styling

### Button Variants

```typescript
// Button component variants
const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```

### Card Components

```tsx
// Consistent card styling
const Card = ({ children, className, ...props }) => (
  <div
    className={cn(
      "rounded-lg border bg-card text-card-foreground shadow-sm",
      className
    )}
    {...props}
  >
    {children}
  </div>
)

const CardHeader = ({ children, className, ...props }) => (
  <div className={cn("flex flex-col space-y-1.5 p-6", className)} {...props}>
    {children}
  </div>
)
```

## Layout Patterns

### Container Layouts

```css
/* Main container */
.container {
  width: 100%;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1rem;
  padding-right: 1rem;
}

@media (min-width: 640px) {
  .container { max-width: 640px; }
}

@media (min-width: 768px) {
  .container { max-width: 768px; }
}

@media (min-width: 1024px) {
  .container { max-width: 1024px; }
}
```

### Grid Systems

```tsx
// Responsive grid patterns
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map(item => (
    <Card key={item.id}>
      {/* Card content */}
    </Card>
  ))}
</div>

// Dashboard layout
<div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
  <div className="lg:col-span-3">
    <MainContent />
  </div>
  <div className="lg:col-span-1">
    <Sidebar />
  </div>
</div>
```

### Flexbox Layouts

```tsx
// Header layout
<header className="flex items-center justify-between h-16 px-6 border-b">
  <div className="flex items-center space-x-4">
    <Logo />
    <Navigation />
  </div>
  <UserMenu />
</header>

// Form layout
<form className="flex flex-col space-y-4">
  <Input placeholder="Email" />
  <Input type="password" placeholder="Password" />
  <Button type="submit">Sign In</Button>
</form>
```

## Animation & Transitions

### Tailwind Animations

```css
/* Built-in animations */
.animate-spin { animation: spin 1s linear infinite; }
.animate-ping { animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite; }
.animate-pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
.animate-bounce { animation: bounce 1s infinite; }

/* Custom animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fadeIn 0.2s ease-out;
}
```

### Transition Classes

```css
/* Smooth transitions */
.transition-all { transition: all 150ms ease-in-out; }
.transition-colors { transition: color, background-color, border-color 150ms ease-in-out; }
.transition-transform { transition: transform 150ms ease-in-out; }

/* Hover effects */
.hover\:scale-105:hover { transform: scale(1.05); }
.hover\:shadow-lg:hover { box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1); }
```

## Status & Feedback

### Loading States

```tsx
// Skeleton loading
const JobSkeleton = () => (
  <Card>
    <CardHeader>
      <div className="h-4 bg-muted rounded animate-pulse" />
      <div className="h-3 bg-muted rounded w-2/3 animate-pulse" />
    </CardHeader>
    <CardContent>
      <div className="space-y-2">
        <div className="h-3 bg-muted rounded animate-pulse" />
        <div className="h-3 bg-muted rounded w-4/5 animate-pulse" />
      </div>
    </CardContent>
  </Card>
)

// Loading spinner
const Spinner = () => (
  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary" />
)
```

### Status Indicators

```tsx
// Status badges
const StatusBadge = ({ status }: { status: JobStatus }) => {
  const variants = {
    pending: "bg-yellow-100 text-yellow-800 border-yellow-200",
    processing: "bg-blue-100 text-blue-800 border-blue-200",
    completed: "bg-green-100 text-green-800 border-green-200",
    failed: "bg-red-100 text-red-800 border-red-200",
  }

  return (
    <span className={cn(
      "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border",
      variants[status]
    )}>
      {status}
    </span>
  )
}
```

## Responsive Design

### Breakpoint Strategy

```css
/* Mobile first approach */
/* Default: mobile (0px+) */
.text-sm { font-size: 0.875rem; }

/* Tablet (768px+) */
@media (min-width: 768px) {
  .md\:text-base { font-size: 1rem; }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
  .lg\:text-lg { font-size: 1.125rem; }
}
```

### Responsive Components

```tsx
// Responsive navigation
const Navigation = () => (
  <nav className="flex flex-col md:flex-row space-y-2 md:space-y-0 md:space-x-6">
    <NavLink href="/dashboard">Dashboard</NavLink>
    <NavLink href="/jobs">Jobs</NavLink>
    <NavLink href="/settings">Settings</NavLink>
  </nav>
)

// Responsive grid
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {/* Grid items */}
</div>
```

## Dark Mode Implementation

### Theme Toggle

```tsx
const ThemeToggle = () => {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
    >
      {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
    </Button>
  )
}
```

### Theme Provider

```tsx
const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    return localStorage.getItem('theme') as 'light' | 'dark' || 'light'
  })

  useEffect(() => {
    localStorage.setItem('theme', theme)
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}
```

## Best Practices

### CSS Organization

1. **Use Tailwind utilities** for most styling needs
2. **Create custom components** for repeated patterns
3. **Use CSS custom properties** for dynamic values
4. **Follow mobile-first** responsive design

### Performance Considerations

1. **Minimize custom CSS** - prefer Tailwind utilities
2. **Use CSS containment** for complex components
3. **Optimize critical rendering path** with inline critical CSS
4. **Lazy load** non-critical styles

### Accessibility

1. **Maintain color contrast** ratios (WCAG AA minimum)
2. **Use semantic HTML** with proper ARIA labels
3. **Ensure keyboard navigation** works properly
4. **Test with screen readers**

This styling guide ensures consistent, maintainable, and accessible visual design across the Shepherd frontend application.

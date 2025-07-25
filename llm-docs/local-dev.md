# Supabase Local Development Guide

This guide provides step-by-step instructions for setting up and running a local Supabase instance for development.

## Prerequisites

- **Docker Desktop** or compatible container runtime
- **Supabase CLI** installed

## Installing Supabase CLI

### macOS (Homebrew)
```bash
brew install supabase/tap/supabase
```

## Setting Up Local Supabase Instance

### 1. Initialize Supabase Project

Navigate to your project root directory and initialize Supabase:

```bash
supabase init
```

This creates a `supabase/` directory with configuration files.

### 2. Start Local Development Stack

```bash
supabase start
```

**What this does:**
- Downloads Docker images (first run only)
- Starts PostgreSQL database
- Starts Supabase services (API, Studio, Auth, Storage, etc.)
- Displays local development credentials

**Expected output:**
```
         API URL: http://127.0.0.1:54321
     GraphQL URL: http://127.0.0.1:54321/graphql/v1
  S3 Storage URL: http://127.0.0.1:54321/storage/v1/s3
          DB URL: postgresql://postgres:postgres@127.0.0.1:54322/postgres
      Studio URL: http://127.0.0.1:54323
    Inbucket URL: http://127.0.0.1:54324
      JWT secret: super-secret-jwt-token-with-at-least-32-characters-long
        anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Accessing Local Services

### Supabase Studio Dashboard
Open your browser and navigate to: **http://127.0.0.1:54323**

Use the Studio to:
- View and edit database tables
- Manage authentication settings
- Configure storage buckets
- Write and test SQL queries

### API Endpoints
- **REST API:** http://127.0.0.1:54321/rest/v1/
- **GraphQL:** http://127.0.0.1:54321/graphql/v1
- **Storage:** http://127.0.0.1:54321/storage/v1/
- **Auth:** http://127.0.0.1:54321/auth/v1/

### Database Connection
- **Host:** 127.0.0.1
- **Port:** 54322
- **Username:** postgres
- **Password:** postgres
- **Database:** postgres

## Testing Your Setup

### 1. Check Service Status
```bash
supabase status
```

### 2. Test API Endpoint
```bash
curl -f http://127.0.0.1:54321/rest/v1/
```

### 3. Test Database Connection
```bash
PGPASSWORD=postgres psql -h 127.0.0.1 -p 54322 -U postgres -d postgres -c "SELECT version();"
```

### 4. Access Studio
Open http://127.0.0.1:54323 in your browser to confirm the Studio is running.

## Managing Your Local Instance

### View Current Status
```bash
supabase status
```

### Stop All Services
```bash
supabase stop
```

### Reset Database (Removes All Data)
```bash
supabase db reset
```

## Working with Database Changes

### Creating Migrations
```bash
# Create a new migration file
supabase migration new create_users_table
```

### Applying Migrations
```bash
# Apply pending migrations
supabase db reset
```

### Generating Types
```bash
# Generate TypeScript types from your database schema
supabase gen types typescript --local > database.types.ts
```

## Common Use Cases

### Seeding Initial Data
Create a `supabase/seed.sql` file with your initial data:

```sql
-- Example seed data
INSERT INTO profiles (id, username, email) VALUES
  ('550e8400-e29b-41d4-a716-446655440000', 'user1', 'user1@example.com'),
  ('550e8400-e29b-41d4-a716-446655440001', 'user2', 'user2@example.com');
```

### Testing Authentication
```bash
# Test user signup
curl -X POST 'http://127.0.0.1:54321/auth/v1/signup' \
-H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
-H "Content-Type: application/json" \
-d '{"email": "test@example.com", "password": "password123"}'
```

## Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Check what's using the ports
lsof -i :54321
lsof -i :54322
lsof -i :54323
```

**Docker issues:**
```bash
# Reset Docker state
docker system prune -a
supabase stop
supabase start
```

**Database connection fails:**
```bash
# Ensure PostgreSQL is running
docker ps | grep postgres

# Check logs
docker logs supabase_db_[your_project_name]
```

**Studio not loading:**
```bash
# Check Kong gateway logs
docker logs supabase_kong_[your_project_name]
```

### Getting Help

- **Supabase CLI docs:** https://supabase.com/docs/guides/cli
- **Local development:** https://supabase.com/docs/guides/local-development
- **GitHub issues:** https://github.com/supabase/cli/issues

## Next Steps

1. **Configure your application** to use the local Supabase instance
2. **Set up your database schema** using migrations
3. **Test your application** against the local instance
4. **Deploy your changes** to production when ready

The local Supabase instance provides a complete development environment that mirrors production, allowing you to develop and test your application without affecting live data.

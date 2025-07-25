# Shepherd Monorepo Project Specification

## Overview

Shepherd is a **monorepo** containing multiple interconnected projects that provide an automated audio transcription and summarization service. This repository houses both the backend processing pipeline and the frontend web application as separate, independently deployable projects.

## Repository Structure

```
shepard/
├── llm-docs/                 # 📋 Shared project documentation
│   ├── project-spec.md       # This file - monorepo overview
│   ├── product-spec.md       # Product requirements & features
│   └── system-spec.md        # Technical architecture & security
│
├── pipeline/                 # 🔧 Backend processing system
│   ├── llm-docs/ .           # pipeline specific AI docs
│   ├── src/                  # Python pipeline code
│   ├── requirements.txt      # Python dependencies
│   └── docker-compose.yml    # Local development setup
│
└── frontend/                 # 🌐 React web application
│   ├── llm-docs/ .           # frontend specific AI docs
    ├── src/                  # React TypeScript code
    ├── package.json          # Node.js dependencies
    └── vite.config.ts        # Build configuration
```

## Project Components

### 🔧 Pipeline (Backend)

**Purpose**: Audio processing and AI workflow orchestration
**Technology**: Python + Prefect + Supabase
**Responsibilities**:

- Audio ingestion (file upload, YouTube links)
- Transcription, translation, and summarization
- Job status tracking and result storage

📖 **Implementation details**: See [`pipeline/llm-docs/project-spec.md`](../pipeline/llm-docs/project-spec.md)

### 🌐 Frontend (Web Application)

**Purpose**: User interface and experience
**Technology**: React + TypeScript + Tailwind CSS + shadcn/ui
**Responsibilities**:

- User authentication and profile management
- Job submission and configuration
- Real-time status monitoring and result access

📖 **Implementation details**: See [`frontend/llm-docs/project-spec.md`](../frontend/llm-docs/project-spec.md)

## Shared Infrastructure

### 🗄️ Supabase (Shared Data Layer)

Both projects integrate with a single Supabase instance:

- **Authentication**: Shared user accounts and sessions
- **Database**: Common schema for users, jobs, and results
- **Real-time**: Live updates between pipeline and frontend
- **Storage**: File uploads and result artifacts

### 🔐 Security Model

- **Row-Level Security (RLS)**: Database-level access control
- **API Authentication**: Service-to-service communication
- **User Isolation**: Each user can only access their own data

## Development Workflow

### Prerequisites

```bash
# Required tools
- Node.js 18+ (frontend)
- Python 3.9+ (pipeline)
- Docker & Docker Compose (local development)
- Supabase CLI (database management)
```

### Local Development Setup

#### 1. Repository Setup

```bash
# Clone and navigate to repo
git clone <repository-url>
cd shepherd
```

#### 2. Supabase Local Environment

```bash
# Start local Supabase (shared by both projects)
supabase start
supabase db reset  # Initialize schema
```

### Project Independence

Each project can be developed **independently**:

- **Frontend**: Can run with mocked data or staging backend
- **Pipeline**: Can process jobs without frontend interaction
- **Shared Testing**: Use local Supabase for integration testing

## Integration Points

### Data Flow

```
User (Frontend) → Supabase → Pipeline → Supabase → Frontend (Results)
```

### Communication Patterns

1. **Job Submission**: Frontend writes to `jobs` table → Pipeline reads
2. **Status Updates**: Pipeline updates job status → Frontend receives real-time updates
3. **Authentication**: Shared user sessions across both applications
4. **File Handling**: Frontend uploads to Supabase Storage → Pipeline processes

### API Boundaries

| Component | Supabase Usage | Direct Communication |
|-----------|----------------|---------------------|
| Frontend  | ✅ Direct client connection | ❌ No direct pipeline calls |
| Pipeline  | ✅ Service account access | ❌ No frontend dependencies |

## Deployment Strategy

### Independent Deployments

- **Frontend**: Static hosting (Github Pages).
- **Pipeline**: Container deployment (Docker, Kubernetes)
- **Database**: Managed Supabase (shared between both)

### Environment Management

| Environment | Frontend URL | Pipeline Deployment | Supabase Project |
|-------------|--------------|-------------------|------------------|
| Development | localhost:5173 | Local Docker | Local instance |
| Staging | shepherd-stg.fruitful-tools.com | Staging cluster | Staging project |
| Production | shepherd.fruitful-tools.com | Production cluster | Production project |

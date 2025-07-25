# Shepard Pipeline Spec

## Overview

This document defines the architectural blueprint for implementing Shepard's data pipeline system using Prefect, with robust local development and flexible cloud/self-hosted deployment in mind. It addresses environment management, dependency management, deployment strategy, Supabase integration (DB schema, RLS, API keys), and pipeline modularity for three user entry points.

## Development & Deployment Environment

### Development Tooling

1. pyenv for Python version management.
2. uv for dependency management.

### Local Dev & Testing

1. Use Docker and docker-compose to provide full local environments mirroring production.
2. All core services (Prefect, API server, worker) run as containers.
3. Instruction to run supabase locally

### Future Deployment

1. Architect with Prefect Cloud and Kubernetes in mind (stateless Prefect code, use env vars for config).

## Prefect Pipeline Design
### Entry Points

| Entry | Steps | Flexibility |
|---|---|---|
| 1. YouTube Video | Download → Extract Audio → Chunk Audio → Transcribe → (Translate/Correct) → Summarize | Configurable models, chunk size, instructions |
| 2. Audio File | Upload → Chunk Audio → Transcribe → (Translate/Correct) → Summarize | Configurable at each step |
| 3. Text Summary | Accept Transcript → Summarize – with custom instruction, model, and word limits | Instructions and model/word limit adjustable |

Each flow must allow component model and parameter selection at runtime (via Prefect parameters).

Modular Tasks: Break down into atomic Prefect Tasks for easy swapping/configuration.

# Shepherd System Architecture Specification

## 1. Authentication & Authorization

- **Frontend Authentication**: Users log in via Supabase Auth, supporting Google OAuth as the main identity provider. User profiles and sessions are managed within Supabase.
- **Row-Level Security (RLS)**: Critical operations—such as starting a pipeline job and fetching job status, quota, and pricing—are guarded by RLS policies in Supabase to ensure users can only access their own data and actions. These policies strictly control access at the database level.
- **Service-to-Service API Auth**:
  - The frontend web application communicates with the backend (api server or Prefect orchestrator) using service-to-service tokens to validate user actions and enforce permissions when initiating jobs.
  - When the Prefect pipeline needs to write results or statuses back to Supabase, it utilizes a privileged Supabase API key with scoped permissions, allowing for secure updates without exposing database access credentials on the web.
- **Quota & Pricing Access**: Pricing plans, quota use, and available credits are all managed through Supabase, accessible via authenticated queries restricted by RLS.

## 2. Rate Limiting & Quota Enforcement

- **Application-Level Quota**: Each user is assigned a daily job submission quota (e.g., 2 jobs/day by default), tracked and enforced at the Supabase level through RLS policies. The quota data is surfaced in the user dashboard and prevents job submission when limits are reached.
- **Credit System**: Credits (purchasable via pricing plans) are required to run jobs. 1 credit typically processes up to 1 hour of audio; jobs exceeding the 1-hour mark deduct multiple credits proportionally. Failed jobs do not consume credits.
- **Pipeline-Level Concurrency**: Prefect’s built-in concurrency controls are configured to enforce account-wide and system-wide maximum simultaneous job runs. This prevents resource starvation and overuse from any single user or account.
- **Combined Enforcement**: Both RLS-based quota checks and Prefect concurrency limits work together to provide defense-in-depth against abuse or accidental overuse.

## 3. Model Configuration & Modularity

- **Transcription**: The workflow starts with Voxtral for speech-to-text transcription, operating on configurable 10-minute audio chunks for large files. The chunk size can be adjusted per request.
- **Text Correction/Translation**: The raw transcript is passed to the Mistral model (misstral) to correct errors and produce high-quality output in Traditional Chinese (zh-TW). Model choice and language can be parameterized per pipeline run.
- **Summarization**: Corrected text is merged and summarized, typically using an external LLM API. Summarization instructions and word limits can be supplied by users on the frontend.
- **Pluggable Design**: All key steps (transcription, model, chunk size, summarization method) are defined as Prefect parameters and can be swapped or extended via modular task definitions. This allows easy integration of alternative models or service endpoints as requirements or best practices evolve[2].

## 4. Full Request Workflow

1. **User Action**: User logs in (via Google/Supabase) and submits a job from the frontend web UI, providing an audio file, YouTube link, or transcript text, along with any custom instructions or model preferences.
2. **Backend Validation**: The web backend verifies the user’s quota, credit balance, and permissions using Supabase Auth and RLS policies.
3. **Pipeline Trigger**: If passes, the backend dispatches a pipeline run in Prefect on behalf of the user, authenticating the service request to the pipeline using a JWT or signed API token.
4. **Workflow Execution**:
   - Download/process audio and split into defined chunks.
   - Transcribe via Voxtral.
   - Text chunks processed through misstral for zh-TW correction.
   - Results aggregated and summarized with the selected LLM.
   - Step-by-step modular Prefect tasks enable plug-and-play upgrades[2].
5. **Status Updates**: The pipeline posts status and results back to Supabase using a privileged API key, enabling the frontend to reflect real-time progress and provide notifications to the user.
6. **Result Retrieval**: User fetches completed transcript and summary via the dashboard. Download access and usage statistics are subject to RLS and credit logic.

## Key Principles

- **Security by Design**: All user data access, job execution, and updates are tied to Supabase RLS and scoped API credentials.
- **Modularity**: Models, chunk size, and workflow steps are runtime-configurable, future-proofing the system.
- **Transparent Usage**: End users can always view their quota, credit use, and job statuses in the dashboard.

This architecture ensures robust security, flexible AI modeling, and transparent cost controls, fit for rapid adaptation and growth.

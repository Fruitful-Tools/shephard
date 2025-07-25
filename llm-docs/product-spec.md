# Shepherd Product Spec

## Overview

This product provides users with a streamlined interface to initiate, monitor, and retrieve results from automated data pipelines. Users can authenticate via Google, trigger pipelines on-demand, and view the status and results directly through the frontend.

## Target Users

Non-technical professionals (e.g. pastor, church leader, regular believer)

## Core Features

### Authentication

1. Google login powered by Supabase.
2. User profile stored and managed via Supabase Auth.

## Key Feature

1. Users can initiate a job to start transcipting and simmarizing through the web interface.
2. User can upload a file or paste YouTube link (no more than 3 hours).
3. User can fine tune summarization instruction, audio chunk side, word limit for summary.

## Status Dashboard

1. Users can view real-time and historical statuses of their pipeline runs.
2. User can see progress with running job.

## Result Access

1. Once completed, user can download transcript and summary via frontend.

## Usage Limits and Pricing

1. Each user has a rate-limited quota (e.g., 2 runs/day by default).
2. Usage and quota stats shown in the user dashboard.
3. User buy credit, 1 credit runs 1 job or max of 1 hour video, failed job does not count. For example, a 15 min and 60 minutes video both cost 1 credet, but a 61 minutes video cost 2 credets.
4. Will provide plan to buy 10 NTD for 1 credit, 90 NTD for 10 credets, ..., price plan adjustable by admin.

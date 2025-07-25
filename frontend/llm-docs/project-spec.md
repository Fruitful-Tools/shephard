# Shepherd Frontend Project Specification

## Overview

This document details the product-specific features and user interface requirements for the Shepherd web application frontend. For technical implementation guidelines, see the modular documentation:

- [Development Guidelines](./development-guidelines.md) - Component architecture, coding conventions
- [Architecture Guide](./architecture-guide.md) - Technical stack, configuration, patterns
- [Styling Guide](./styling-guide.md) - Design system, themes, responsive design
- [Testing Guide](./testing-guide.md) - Testing strategy, tools, best practices

For overall project structure and monorepo information, see the [main project specification](../../llm-docs/project-spec.md).

## Product Features

### Core User Workflows

1. **Authentication & User Management**
   - User registration and login
   - Profile management with credit tracking
   - Daily quota monitoring

2. **Job Submission & Configuration**
   - Multi-format input support (YouTube, audio files, text)
   - Customizable processing settings
   - Bulk job submission

3. **Real-time Job Monitoring**
   - Live status updates via Supabase subscriptions
   - Progress indicators and estimated completion times
   - Error handling and retry mechanisms

4. **Results Management**
   - Transcript viewing and editing
   - Summary generation with different formats
   - Export capabilities (PDF, text, structured data)

### Technology Stack Summary

- **React 18+** with TypeScript for type-safe component development
- **Tailwind CSS + shadcn/ui** for consistent, accessible UI components
- **TanStack Query + Supabase** for real-time data management
- **React Router v6** for modern routing with data loading

## User Interface Specifications

### Page Layouts

#### Dashboard Page
- **Header**: Logo, navigation menu, user profile dropdown
- **Sidebar**: Quick actions, recent jobs, system status
- **Main Content**:
  - Job overview cards with status indicators
  - Quick submission form
  - Usage statistics and quota information
- **Footer**: Links, version info, support

#### Job Submission Page
- **Multi-step Form**:
  1. Input selection (YouTube URL, file upload, text paste)
  2. Processing configuration (chunk size, word limits, custom instructions)
  3. Review and confirmation
- **Real-time Validation**: URL checking, file size validation
- **Progress Indicators**: Visual feedback for each step

#### Job Details Page
- **Status Panel**: Current phase, progress bar, estimated completion
- **Configuration Summary**: Chosen settings, input details
- **Live Updates**: Real-time status changes via WebSocket
- **Results Panel**: Transcript, summary, export options (when complete)

#### Results Management Page
- **Table View**: Sortable list of completed jobs
- **Search & Filter**: By date, type, status, custom tags
- **Bulk Operations**: Export multiple results, archive, delete
- **Preview Cards**: Quick summary with expand options

## Feature Components

### Authentication Components
- **LoginForm**: Email/password authentication with validation
- **SignupForm**: User registration with terms acceptance
- **UserProfile**: Display and edit user information, credit balance
- **ProtectedRoute**: Route guard for authenticated users

### Job Management Components
- **JobSubmissionForm**: Multi-step form for creating new jobs
  - Input selection (URL/file/text)
  - Configuration settings
  - Review and confirmation
- **JobCard**: Compact job display with status and actions
- **JobStatusBadge**: Visual status indicator with colors
- **JobProgressBar**: Real-time progress visualization
- **JobList**: Filterable and sortable job collection

### Results Components
- **TranscriptViewer**: Display and edit transcript text
- **SummaryDisplay**: Formatted summary with customizable views
- **ExportDialog**: Multiple format export options
- **ResultsTable**: Tabular view with search and filter
- **PreviewCard**: Quick result preview with expand option

### Dashboard Components
- **QuickStats**: Usage metrics and quota information
- **RecentJobs**: Latest job activities
- **SystemStatus**: Pipeline health indicators
- **QuickActions**: Common task shortcuts

## Data Management

### User Data Flow
1. **Authentication State**: User login status, profile, credits
2. **Job Lifecycle**: Creation → Processing → Completion → Results
3. **Real-time Updates**: Live status changes via Supabase subscriptions
4. **Offline Support**: Cache results for offline viewing

### API Integration Points
- **Authentication**: Supabase Auth for login/registration
- **Jobs Database**: CRUD operations on job records
- **File Storage**: Upload audio files to Supabase Storage
- **Real-time**: Subscribe to job status changes
- **Pipeline Communication**: Status updates from processing system

## User Experience Features

### Navigation Structure
```
/ (Home)                    - Landing page, marketing content
/login                      - Authentication forms
/dashboard                  - Main user interface
/jobs/new                   - Job creation wizard
/jobs/:id                   - Individual job details and results
/results                    - Results management page
/profile                    - User account and settings
/help                       - Documentation and support
```

### Real-time Features
- **Live Status Updates**: WebSocket connection for job progress
- **Notifications**: Toast messages for important events
- **Auto-refresh**: Periodic data updates without user action
- **Optimistic Updates**: Immediate UI feedback before server confirmation

### Responsive Design
- **Mobile-first**: Touch-friendly interface for phone usage
- **Tablet Support**: Optimized layouts for medium screens
- **Desktop Experience**: Full feature set with advanced layouts
- **Progressive Enhancement**: Works without JavaScript for basic functions

## Accessibility & Usability

### Accessibility Standards
- **WCAG AA Compliance**: Color contrast, keyboard navigation, screen reader support
- **Semantic HTML**: Proper heading structure, landmarks, form labels
- **Focus Management**: Clear focus indicators, logical tab order
- **Error Handling**: Clear error messages, validation feedback

### Usability Features
- **Keyboard Shortcuts**: Power user efficiency
- **Undo/Redo**: For transcript editing and configuration changes
- **Bulk Operations**: Multi-select for managing multiple jobs
- **Search & Filter**: Quick content discovery
- **Contextual Help**: Inline tooltips and guidance

## Data Model

### Job Lifecycle States
- **pending**: Job created, waiting for processing
- **processing**: Currently being transcribed/summarized
- **completed**: Successfully finished with results
- **failed**: Encountered error, may be retryable

### Input Types
- **YouTube URL**: Direct video/audio processing from YouTube
- **Audio File**: User-uploaded audio files (MP3, WAV, M4A)
- **Text Input**: Direct text for summarization only

### Configuration Options
- **Chunk Size**: Processing segments (1-30 minutes)
- **Word Limit**: Summary length constraints
- **Custom Instructions**: User-defined processing guidelines
- **Model Preference**: AI model selection for summarization

## Error Handling & Recovery

### User-Friendly Error Messages
- **File Upload Errors**: Clear guidance on supported formats and size limits
- **Network Issues**: Offline indicators and retry mechanisms
- **Processing Failures**: Detailed error descriptions and suggested fixes
- **Authentication Errors**: Clear login prompts and account recovery options

### Recovery Mechanisms
- **Auto-retry**: Automatic retry for transient failures
- **Manual Retry**: User-initiated retry for failed jobs
- **Partial Recovery**: Save progress during interruptions
- **Data Persistence**: Local storage for draft configurations

## Performance & User Experience

### Loading States
- **Skeleton Screens**: Content placeholders during data loading
- **Progress Indicators**: Clear progress bars for uploads and processing
- **Lazy Loading**: Deferred loading of non-critical components
- **Optimistic Updates**: Immediate UI feedback before server confirmation

### Caching Strategy
- **Result Caching**: Store completed results for offline access
- **Configuration Caching**: Remember user preferences and settings
- **Image Caching**: Optimize avatar and UI image loading
- **Query Caching**: Smart data fetching with TanStack Query

## Security Considerations

### User Data Protection
- **Client-side Validation**: Input sanitization and validation
- **Secure File Handling**: Safe upload and storage practices
- **Authentication State**: Secure session management
- **Data Encryption**: Sensitive data protection in transit and at rest

### Content Security
- **XSS Prevention**: Safe rendering of user-generated content
- **CSRF Protection**: Secure form submissions
- **File Upload Security**: Virus scanning and type validation
- **API Security**: Authenticated requests with proper authorization

This specification focuses on the product features and user experience requirements for the Shepherd frontend application, with technical implementation details now properly modularized into separate guideline documents.

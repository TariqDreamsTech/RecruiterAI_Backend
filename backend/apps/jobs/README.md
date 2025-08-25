# Job Posting System with LinkedIn Integration

This Django app provides a comprehensive job posting system that integrates with LinkedIn through the Unipile API.

## Features

### Core Job Management
- **Job Postings**: Create, edit, publish and manage job postings
- **Job Categories & Skills**: Organize jobs with categories and required skills
- **Job Templates**: Create reusable templates for common job types
- **Application Management**: Track and manage job applications
- **Advanced Search**: Filter jobs by location, type, experience level, salary, etc.

### LinkedIn Integration via Unipile
- **Account Management**: Connect and manage multiple LinkedIn accounts
- **Auto-Posting**: Automatically post jobs to LinkedIn when published
- **Webhook Integration**: Real-time updates for account status, messaging, etc.
- **Profile Search**: Search for potential candidates on LinkedIn
- **Messaging**: Send messages to candidates via LinkedIn

### Application Tracking
- **Application Status**: Track applications through the hiring pipeline
- **Resume Management**: Store and manage candidate resumes
- **Interview Feedback**: Record interview notes and feedback
- **Automated Notifications**: Email notifications for status changes

## API Endpoints

### Job Management
- `GET /api/jobs/jobs/` - List all jobs (published for public, all for recruiters)
- `POST /api/jobs/jobs/` - Create a new job
- `GET /api/jobs/jobs/{id}/` - Get job details
- `PUT /api/jobs/jobs/{id}/` - Update job
- `DELETE /api/jobs/jobs/{id}/` - Delete job
- `POST /api/jobs/jobs/{id}/publish/` - Publish job (optionally to LinkedIn)
- `GET /api/jobs/jobs/stats/` - Get job statistics for recruiter
- `GET /api/jobs/jobs/search/` - Advanced job search

### Applications
- `GET /api/jobs/applications/` - List applications (for recruiter's jobs)
- `POST /api/jobs/applications/` - Submit job application
- `GET /api/jobs/applications/{id}/` - Get application details
- `PATCH /api/jobs/applications/{id}/update_status/` - Update application status

### Templates
- `GET /api/jobs/templates/` - List job templates
- `POST /api/jobs/templates/` - Create job template
- `POST /api/jobs/templates/create_job/` - Create job from template

### LinkedIn Integration
- `GET /api/jobs/unipile/accounts/` - Get all Unipile accounts
- `GET /api/jobs/unipile/linkedin-accounts/` - Get LinkedIn accounts only
- `POST /api/jobs/unipile/setup-webhooks/` - Setup Unipile webhooks

### Webhooks (for Unipile)
- `POST /api/jobs/webhooks/account-status/` - Account status updates
- `POST /api/jobs/webhooks/messaging/` - Messaging events
- `POST /api/jobs/webhooks/mailing/` - Email events
- `POST /api/jobs/webhooks/mail-tracking/` - Email tracking events
- `POST /api/jobs/webhooks/users-relations/` - Connection events

### Public API
- `GET /api/jobs/categories/` - Get job categories
- `GET /api/jobs/skills/` - Get job skills

## Usage Examples

### 1. Create a Job Posting

```bash
curl -X POST "http://localhost:8000/api/jobs/jobs/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Python Developer",
    "company_name": "Tech Corp",
    "description": "We are looking for an experienced Python developer...",
    "responsibilities": "- Develop backend APIs\n- Write clean, maintainable code",
    "requirements": "- 5+ years Python experience\n- Django/FastAPI knowledge",
    "location": "San Francisco, CA",
    "job_type": "full_time",
    "experience_level": "senior",
    "salary_min": 120000,
    "salary_max": 180000,
    "salary_currency": "USD",
    "salary_period": "yearly"
  }'
```

### 2. Publish Job to LinkedIn

```bash
curl -X POST "http://localhost:8000/api/jobs/jobs/{job_id}/publish/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "post_to_linkedin": true,
    "linkedin_account_id": "linkedin_account_123",
    "custom_message": "Exciting opportunity for a Senior Python Developer!"
  }'
```

### 3. Search Jobs

```bash
curl "http://localhost:8000/api/jobs/jobs/search/?query=python&job_type=full_time&location=san francisco&salary_min=100000"
```

### 4. Submit Application

```bash
curl -X POST "http://localhost:8000/api/jobs/applications/" \
  -H "Content-Type: application/json" \
  -d '{
    "job": "job_uuid_here",
    "applicant_name": "John Doe",
    "applicant_email": "john@example.com",
    "applicant_phone": "+1234567890",
    "cover_letter": "I am very interested in this position..."
  }'
```

### 5. Test Unipile Connection

```bash
curl --request GET \
  --url "http://localhost:8000/api/jobs/unipile/accounts/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Unipile Webhook Setup

The system supports the following webhook types:

1. **Account Status**: Updates when LinkedIn accounts are connected/disconnected
2. **Messaging**: New messages, message delivery status
3. **Mailing**: Email delivery, opens, clicks
4. **Mail Tracking**: Email engagement tracking
5. **Users Relations**: New connections, profile updates

### Webhook URLs
- Account Status: `https://yourdomain.com/api/jobs/webhooks/account-status/`
- Messaging: `https://yourdomain.com/api/jobs/webhooks/messaging/`
- Mailing: `https://yourdomain.com/api/jobs/webhooks/mailing/`
- Mail Tracking: `https://yourdomain.com/api/jobs/webhooks/mail-tracking/`
- Users Relations: `https://yourdomain.com/api/jobs/webhooks/users-relations/`

## Configuration

### Environment Variables

```env
# Unipile Configuration
UNIPILE_API_KEY=your_unipile_api_key
UNIPILE_BASE_URL=https://api10.unipile.com:14090/api/v1
UNIPILE_WEBHOOK_URL=https://yourdomain.com/api/jobs/webhooks
```

### Django Settings

Add to `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'apps.jobs',
]
```

## Models

### Job
Main job posting model with all job details, LinkedIn integration status, and tracking metrics.

### JobApplication  
Tracks applications from candidates with status management and recruiter notes.

### JobCategory & JobSkill
Organize jobs with categories and required skills for better searchability.

### JobTemplate
Reusable templates for common job types to speed up job creation.

### UnipileWebhook
Logs all webhook events from Unipile for debugging and processing.

## Admin Interface

All models are registered in Django admin with comprehensive list views, filters, and search functionality:

- Job management with application tracking
- Application status management
- Category and skill management  
- Template management
- Webhook event monitoring

## Error Handling

The system includes comprehensive error handling for:
- Unipile API failures
- LinkedIn posting errors  
- Webhook processing errors
- Application validation errors

All errors are logged and webhook failures are stored for retry processing.

# LinkedIn Job Posting via Unipile API

## Overview

This system provides comprehensive LinkedIn job posting functionality using the Unipile API. Recruiters can create, publish, and manage job postings directly on LinkedIn through our Django application.

## Features

### ✨ Core Functionality

- **🚀 Create LinkedIn Job Postings**: Post jobs directly to LinkedIn with structured data
- **📤 Publish Jobs**: Support for both free and promoted job postings
- **📋 Job Management**: List, view, and manage LinkedIn job postings
- **👥 Applicant Tracking**: Retrieve and track job applicants
- **🎨 Rich Formatting**: HTML-formatted job descriptions with proper structure
- **🔧 Smart Mapping**: Automatic job type and workplace mapping

### 🎯 API Endpoints

#### LinkedIn Job Management
- `POST /api/jobs/linkedin/create-job/` - Create a LinkedIn job posting
- `POST /api/jobs/linkedin/publish-job/` - Publish a job posting
- `GET /api/jobs/linkedin/jobs/` - List all LinkedIn job postings
- `GET /api/jobs/linkedin/job-details/` - Get specific job details
- `GET /api/jobs/linkedin/job-applicants/` - Get job applicants

#### LinkedIn Integration
- `GET /api/jobs/unipile/accounts/` - Get all Unipile accounts
- `GET /api/jobs/unipile/linkedin-accounts/` - Get LinkedIn accounts only
- `POST /api/jobs/unipile/setup-webhooks/` - Setup webhooks

## Usage Examples

### 1. Create and Publish a LinkedIn Job

```bash
# Step 1: Get LinkedIn accounts
curl -X GET "https://your-domain.com/api/jobs/unipile/linkedin-accounts/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Step 2: Create LinkedIn job posting
curl -X POST "https://your-domain.com/api/jobs/linkedin/create-job/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "123",
    "linkedin_account_id": "account_123",
    "auto_rejection_template": "Thank you for applying. Unfortunately...",
    "screening_questions": [
      {
        "question": "How many years of experience do you have?",
        "required": true,
        "type": "text"
      }
    ],
    "publish_options": {
      "free": true
    }
  }'

# Step 3: Publish the job (if not auto-published)
curl -X POST "https://your-domain.com/api/jobs/linkedin/publish-job/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "linkedin_job_id": "linkedin_job_123",
    "linkedin_account_id": "account_123",
    "publish_options": {"free": true}
  }'
```

### 2. Monitor Job Performance

```bash
# Get job details
curl -X GET "https://your-domain.com/api/jobs/linkedin/job-details/?account_id=account_123&job_id=linkedin_job_123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get applicants
curl -X GET "https://your-domain.com/api/jobs/linkedin/job-applicants/?account_id=account_123&job_id=linkedin_job_123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Job Data Mapping

### Workplace Types
| Job Type | LinkedIn Workplace |
|----------|-------------------|
| remote | REMOTE |
| hybrid | HYBRID |
| full_time | ON_SITE |
| part_time | ON_SITE |
| contract | ON_SITE |
| freelance | REMOTE |
| internship | ON_SITE |

### Employment Status
| Job Type | LinkedIn Employment |
|----------|-------------------|
| full_time | FULL_TIME |
| part_time | PART_TIME |
| contract | CONTRACT |
| freelance | CONTRACT |
| internship | INTERNSHIP |
| remote | FULL_TIME |
| hybrid | FULL_TIME |

## Job Description Formatting

The system automatically formats job descriptions into structured HTML:

```html
<h2>About the Role</h2>
<p>Job description...</p>

<h3>Key Responsibilities</h3>
<ul>
  <li>Responsibility 1</li>
  <li>Responsibility 2</li>
</ul>

<h3>Requirements</h3>
<ul>
  <li>Requirement 1</li>
  <li>Requirement 2</li>
</ul>

<h3>Nice to Have</h3>
<ul>
  <li>Optional requirement 1</li>
</ul>

<h3>Compensation</h3>
<p>Salary range information</p>

<h3>Location</h3>
<p>Job location</p>
```

## Testing

### Run the Test Suite

```bash
cd backend
python test_linkedin_job_posting.py
```

The test script will:
1. Test job type mapping functions
2. Test HTML formatting
3. Create a test LinkedIn job posting
4. Publish the job
5. Retrieve job details and applicants

### Expected Output

```
🧪 Testing LinkedIn Job Posting via Unipile
============================================================
📡 Getting LinkedIn accounts...
✅ Using LinkedIn account: John Doe (ID: account_123)

📝 Test Job Data:
  - Title: Senior Python Developer - Test Job
  - Company: Tech Innovations Inc.
  - Location: San Francisco, CA
  - Type: full_time
  - Workplace: ON_SITE
  - Employment: FULL_TIME

🚀 Creating LinkedIn job posting...
✅ LinkedIn job created successfully!
  - LinkedIn Job ID: linkedin_job_123

📤 Publishing job (free option)...
✅ Job published successfully!
  - Job URL: https://linkedin.com/jobs/...

🎉 All tests completed successfully!
```

## Configuration

### Environment Variables

Make sure these are set in your environment:

```bash
# Unipile Configuration
UNIPILE_API_KEY=your_api_key_here
UNIPILE_BASE_URL=https://api10.unipile.com:14090/api/v1
UNIPILE_WEBHOOK_URL=https://your-domain.com/api/jobs/webhooks
```

### Django Settings

The following apps should be in your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'apps.jobs',
    'rest_framework',
    'drf_spectacular',
    # ...
]
```

## API Documentation

The LinkedIn job posting endpoints are organized into the following sections in the Swagger UI:

- **📋 Job Management** - Core job CRUD operations
- **📝 Job Applications** - Application management
- **📑 Job Templates** - Template management
- **🔍 Job Search** - Advanced search functionality
- **🔗 LinkedIn Integration** - Basic Unipile integration
- **💼 LinkedIn Job Management** - LinkedIn-specific job operations
- **🌐 Public API** - Public endpoints for categories and skills

Visit your API documentation at: `https://your-domain.com/api/docs/`

## Error Handling

The system includes comprehensive error handling:

### Common Errors

1. **401 Unauthorized** - Invalid or expired LinkedIn account
2. **403 Forbidden** - Insufficient permissions for job posting
3. **422 Unprocessable Entity** - Invalid account for job posting feature
4. **404 Not Found** - Job or account not found
5. **500 Internal Server Error** - API or network issues

### Error Response Format

```json
{
  "error": "Error description",
  "details": "Additional error details"
}
```

## Webhooks

The system supports various Unipile webhooks for real-time updates:

- **Account Status** - `POST /api/jobs/webhooks/account-status/`
- **Messaging** - `POST /api/jobs/webhooks/messaging/`
- **Mailing** - `POST /api/jobs/webhooks/mailing/`
- **Mail Tracking** - `POST /api/jobs/webhooks/mail-tracking/`
- **Users Relations** - `POST /api/jobs/webhooks/users-relations/`

## Security

- All endpoints require JWT authentication
- Users can only manage their own job postings
- Webhook endpoints include CSRF protection
- API rate limiting is handled by Unipile

## Troubleshooting

### Common Issues

1. **LinkedIn Account Not Connected**
   - Solution: Connect LinkedIn account through Unipile dashboard

2. **Job Posting Permission Denied**
   - Solution: Ensure LinkedIn account has job posting permissions

3. **API Key Invalid**
   - Solution: Check Unipile API key configuration

4. **Webhook Not Receiving Data**
   - Solution: Verify ngrok tunnel and webhook URLs

### Debug Mode

Enable debug logging by setting:

```python
LOGGING = {
    'loggers': {
        'apps.jobs.unipile_service': {
            'level': 'DEBUG',
        },
    },
}
```

## Support

For issues with:
- **Unipile API**: Contact Unipile support
- **LinkedIn Integration**: Check LinkedIn Developer documentation
- **Django Application**: Check application logs and error responses

## Future Enhancements

Potential improvements:
- Bulk job posting
- Advanced job performance analytics
- LinkedIn company page integration
- Automated job reposting
- Custom job templates with LinkedIn-specific fields

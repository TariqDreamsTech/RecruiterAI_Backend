# Unipile Webhooks Setup Guide

## ngrok URL
Base URL: `https://0b72c5ff662f.ngrok-free.app`

## Webhook Callback URLs

Configure these URLs in your Unipile dashboard:

### 1. Account Status Update
- **Name**: Account Status Update
- **URL**: `https://0b72c5ff662f.ngrok-free.app/api/jobs/webhooks/account-status/`
- **Events**: 
  - `account.status_updated`
  - `account.connected`
  - `account.disconnected`
- **Description**: Handles LinkedIn account connection status changes

### 2. Messaging Events
- **Name**: Messaging Multiple events
- **URL**: `https://0b72c5ff662f.ngrok-free.app/api/jobs/webhooks/messaging/`
- **Events**: 
  - `message.sent`
  - `message.received`
  - `message.failed`
- **Description**: Handles LinkedIn messaging events (for candidate communication)

### 3. Mailing Events
- **Name**: Mailing Multiple events
- **URL**: `https://0b72c5ff662f.ngrok-free.app/api/jobs/webhooks/mailing/`
- **Events**: 
  - `email.sent`
  - `email.delivered`
  - `email.failed`
  - `email.bounced`
- **Description**: Handles email delivery status for job-related emails

### 4. Mail Tracking Events
- **Name**: Mail Tracking Multiple events
- **URL**: `https://0b72c5ff662f.ngrok-free.app/api/jobs/webhooks/mail-tracking/`
- **Events**: 
  - `email.opened`
  - `email.clicked`
  - `email.unsubscribed`
- **Description**: Tracks engagement with job-related emails

### 5. Users Relations Events
- **Name**: Users Relations events
- **URL**: `https://0b72c5ff662f.ngrok-free.app/api/jobs/webhooks/users-relations/`
- **Events**: 
  - `connection.added`
  - `connection.removed`
  - `profile.updated`
- **Description**: Tracks new LinkedIn connections and profile updates

## Manual Setup Steps

1. **Login to Unipile Dashboard**
   - Go to your Unipile dashboard
   - Navigate to Webhooks section

2. **Create Webhooks**
   For each webhook above:
   - Click "Create New Webhook"
   - Enter the webhook name
   - Enter the callback URL
   - Select the events to subscribe to
   - Set as Active
   - Save the webhook

3. **Test Webhooks**
   - Use the test functionality in Unipile dashboard
   - Monitor Django logs for incoming webhook events
   - Check webhook status in Unipile dashboard

## Programmatic Setup

Run the setup script:
```bash
python setup_unipile_webhooks.py
```

This will:
- Test Unipile API connection
- Automatically create all required webhooks
- Show setup results
- Provide manual setup instructions if needed

## Testing Webhooks

### Test Webhook Endpoints
```bash
# Test each webhook endpoint
curl -X POST "https://0b72c5ff662f.ngrok-free.app/api/jobs/webhooks/account-status/" \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'

curl -X POST "https://0b72c5ff662f.ngrok-free.app/api/jobs/webhooks/messaging/" \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'

# ... repeat for all webhook endpoints
```

### Monitor Webhook Events
```bash
# In Django, check logs for webhook events
python manage.py shell
>>> from apps.jobs.models import UnipileWebhook
>>> UnipileWebhook.objects.all()
```

## Webhook Event Processing

Each webhook handler:
1. **Receives** the event from Unipile
2. **Stores** the event in `UnipileWebhook` model
3. **Processes** the event based on type
4. **Updates** related models (jobs, users, etc.)
5. **Logs** the processing result

## Environment Variables

Ensure these are set in your environment:
```env
UNIPILE_API_KEY=P0P4J3SX.MX5Dvt2lWBiny9TDqdfRp88uKBEcRFk6TWuMi+5bXiY=
UNIPILE_BASE_URL=https://api10.unipile.com:14090/api/v1
UNIPILE_WEBHOOK_URL=https://0b72c5ff662f.ngrok-free.app/api/jobs/webhooks
```

## Security Considerations

1. **HTTPS Required**: All webhook URLs use HTTPS (ngrok provides this)
2. **CSRF Exempt**: Webhook endpoints are exempt from CSRF protection
3. **Event Validation**: All events are validated and stored
4. **Error Handling**: Failed processing is logged with error details

## Troubleshooting

### Common Issues

1. **Webhook Not Receiving Events**
   - Check ngrok is running and accessible
   - Verify webhook URL in Unipile dashboard
   - Check Django server is running

2. **Processing Errors**
   - Check Django logs for error details
   - Verify webhook event structure
   - Check UnipileWebhook model for failed events

3. **Authentication Issues**
   - Verify UNIPILE_API_KEY is correct
   - Check API key permissions in Unipile

### Debug Commands
```bash
# Check webhook events
python manage.py shell -c "
from apps.jobs.models import UnipileWebhook
print('Total webhooks:', UnipileWebhook.objects.count())
print('Processed:', UnipileWebhook.objects.filter(processed=True).count())
print('Failed:', UnipileWebhook.objects.filter(processed=True, processing_error__isnull=False).count())
"

# Test Unipile connection
python test_unipile_connection.py

# Test job system
python test_job_system.py
```

## Next Steps

After webhook setup:
1. Test job posting to LinkedIn
2. Monitor webhook events
3. Test candidate messaging
4. Verify email tracking
5. Check connection events

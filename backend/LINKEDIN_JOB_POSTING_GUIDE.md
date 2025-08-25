# LinkedIn Job Posting Guide - Step by Step

## 🎯 **Complete Workflow for LinkedIn Job Posting**

### **Step 1: Get LinkedIn Account ID**
```bash
GET /api/jobs/unipile/linkedin-accounts/
```
This returns your connected LinkedIn accounts with their IDs.

### **Step 2: Get LinkedIn Location ID**
```bash
GET /api/jobs/linkedin/search-parameters/?account_id=YOUR_ACCOUNT_ID&type=LOCATION&query=San Francisco
```
This returns location IDs that LinkedIn recognizes. You MUST use one of these IDs.

### **Step 3: Create Job in Your System**
```bash
POST /api/jobs/jobs/
```
Create a job with basic information (title, company, description, etc.)

### **Step 4: Post to LinkedIn**
```bash
POST /api/jobs/linkedin/create-job/
```

## 📋 **Required Fields for LinkedIn Job Posting**

According to Unipile API documentation:

### **🔑 Required Fields:**
- `account_id` - Your LinkedIn account ID from Step 1
- `job_title` - Job title (can be plain text or LinkedIn ID)
- `company` - Company name (can be plain text or LinkedIn ID)
- `workplace` - ON_SITE, REMOTE, or HYBRID
- `location` - **MUST be LinkedIn location ID** (from Step 2)
- `description` - Job description with HTML formatting

### **📝 Optional Fields:**
- `employment_status` - FULL_TIME, PART_TIME, CONTRACT, etc.
- `auto_rejection_template` - Auto-rejection message
- `screening_questions` - Array of screening questions
- `recruiter` - Recruiter object

## 🚨 **Common Issues & Solutions**

### **Issue 1: 400 Bad Request - Location Field**
**Problem**: Location must be a LinkedIn location ID, not plain text
**Solution**: Use the search parameters endpoint to get location IDs

### **Issue 2: Missing Required Fields**
**Problem**: API requires specific fields
**Solution**: Ensure all required fields are provided

### **Issue 3: Invalid Account ID**
**Problem**: LinkedIn account not connected or invalid
**Solution**: Check account connection status

## 🔧 **Example Complete Request**

```json
{
  "job_id": "123",
  "linkedin_account_id": "account_67890",
  "location_id": "location_123",  // From search parameters
  "auto_rejection_template": "Thank you for your application...",
  "screening_questions": [
    {
      "question": "How many years of experience?",
      "required": true,
      "type": "text"
    }
  ],
  "publish_options": {
    "free": true
  }
}
```

## 📊 **API Endpoints Reference**

### **LinkedIn Integration**
- `GET /api/jobs/unipile/accounts/` - Get all Unipile accounts
- `GET /api/jobs/unipile/linkedin-accounts/` - Get LinkedIn accounts only

### **LinkedIn Job Management**
- `GET /api/jobs/linkedin/search-parameters/` - Get location/company IDs
- `POST /api/jobs/linkedin/create-job/` - Create LinkedIn job posting
- `POST /api/jobs/linkedin/publish-job/` - Publish job posting
- `GET /api/jobs/linkedin/jobs/` - List LinkedIn jobs
- `GET /api/jobs/linkedin/job-details/` - Get job details
- `GET /api/jobs/linkedin/job-applicants/` - Get applicants

## 🎯 **Testing Workflow**

1. **Test Account Connection**:
   ```bash
   curl -X GET "https://your-domain.com/api/jobs/unipile/linkedin-accounts/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

2. **Get Location IDs**:
   ```bash
   curl -X GET "https://your-domain.com/api/jobs/linkedin/search-parameters/?account_id=YOUR_ACCOUNT_ID&type=LOCATION&query=San Francisco" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
   ```

3. **Create LinkedIn Job**:
   ```bash
   curl -X POST "https://your-domain.com/api/jobs/linkedin/create-job/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "job_id": "123",
       "linkedin_account_id": "YOUR_ACCOUNT_ID",
       "location_id": "LOCATION_ID_FROM_STEP_2"
     }'
   ```

## 🔍 **Debugging Tips**

1. **Check Logs**: Look for detailed error messages in Django logs
2. **Validate Data**: Ensure all required fields are present
3. **Location IDs**: Always use LinkedIn location IDs, not plain text
4. **Account Status**: Verify LinkedIn account is properly connected
5. **API Limits**: Check if you've hit any Unipile API limits

## 📞 **Support**

- **Unipile API Issues**: Check Unipile documentation and support
- **Django Application Issues**: Check application logs and error responses
- **LinkedIn Integration Issues**: Verify account permissions and connection status

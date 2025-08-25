import requests
import logging
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.utils import timezone
from decouple import config


logger = logging.getLogger(__name__)


class UnipileService:
    """Service class for integrating with Unipile API"""
    
    def __init__(self):
        self.api_key = config('UNIPILE_API_KEY', default='')
        self.base_url = config('UNIPILE_BASE_URL', default='https://api10.unipile.com:14090/api/v1')
        self.webhook_url = config('UNIPILE_WEBHOOK_URL', default='https://0b72c5ff662f.ngrok-free.app/api/jobs/webhooks')
        
        if not self.api_key:
            logger.warning("UNIPILE_API_KEY not configured")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Unipile API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            'X-API-KEY': self.api_key,
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Log the request details for debugging
        logger.info(f"Making {method.upper()} request to: {url}")
        if data:
            logger.info(f"Request data: {data}")
        if params:
            logger.info(f"Request params: {params}")
        
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=30
            )
            
            # Log response details for debugging
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            if response.status_code >= 400:
                logger.error(f"API Error Response: {response.text}")
                logger.error(f"Response status: {response.status_code}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Unipile API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Error response: {e.response.text}")
                logger.error(f"Error status: {e.response.status_code}")
            raise UnipileAPIError(f"API request failed: {str(e)}")
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """Get all connected accounts"""
        try:
            response = self._make_request('GET', '/accounts')
            # Handle Unipile API response format
            if isinstance(response, dict) and 'items' in response:
                return response['items']
            elif isinstance(response, list):
                return response
            else:
                logger.warning(f"Unexpected accounts response format: {type(response)}")
                return []
        except Exception as e:
            logger.error(f"Failed to get accounts: {e}")
            return []
    
    def get_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        """Get specific account details"""
        try:
            return self._make_request('GET', f'/accounts/{account_id}')
        except Exception as e:
            logger.error(f"Failed to get account {account_id}: {e}")
            return None
    
    def get_linkedin_accounts(self) -> List[Dict[str, Any]]:
        """Get LinkedIn accounts only"""
        accounts = self.get_accounts()
        return [acc for acc in accounts if acc.get('type', '').upper() == 'LINKEDIN']
    
    def post_to_linkedin(self, account_id: str, content: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Post content to LinkedIn"""
        post_data = {
            'content': content,
            'provider': 'linkedin',
            **kwargs
        }
        
        try:
            response = self._make_request('POST', f'/accounts/{account_id}/posts', data=post_data)
            logger.info(f"Successfully posted to LinkedIn account {account_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to post to LinkedIn account {account_id}: {e}")
            return None
    
    def create_linkedin_job_posting(self, account_id: str, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a job posting on LinkedIn using Unipile LinkedIn Projects API"""
        
        # Validate required fields according to Unipile API
        required_fields = ['title', 'company_name', 'location', 'description']
        for field in required_fields:
            if not job_data.get(field):
                logger.error(f"Missing required field: {field}")
                return None
        
        # First, try to get proper IDs for location and company
        location_id = None
        company_id = None
        
        try:
            # Search for location ID
            locations = self.search_linkedin_locations(account_id, job_data.get('location', ''))
            if locations:
                location_id = locations[0].get('id')
                logger.info(f"Found location ID: {location_id} for '{job_data.get('location')}'")
            
            # Search for company ID
            companies = self.get_linkedin_search_parameters(account_id, "COMPANY")
            if companies:
                # Try to find a matching company
                company_name = job_data.get('company_name', '').lower()
                for company in companies:
                    if company.get('title', '').lower() == company_name:
                        company_id = company.get('id')
                        logger.info(f"Found company ID: {company_id} for '{job_data.get('company_name')}'")
                        break
        except Exception as e:
            logger.warning(f"Could not get location/company IDs, using text values: {e}")
        
        # Prepare job posting data according to Unipile API specification
        job_posting_data = {
            "account_id": account_id,
            "job_title": {"text": job_data.get('title', '')},  # Must be object with 'text' field
            "company": company_id if company_id else {"text": job_data.get('company_name', '')},
            "workplace": self._map_workplace_type(job_data.get('job_type', 'full_time')),
            "employment_status": self._map_employment_status(job_data.get('job_type', 'full_time')),
            "description": self._format_job_description_for_linkedin(job_data),
        }
        
        # Only add location if we have a numeric ID (API requires numeric ID, not text)
        if location_id:
            job_posting_data["location"] = location_id
            logger.info(f"Using location ID: {location_id}")
        else:
            # Try to use a fallback location ID for San Francisco area
            # Based on the documentation examples, these seem to be valid location IDs
            fallback_location_id = "102277331"  # This appears to be a valid location ID from the docs
            logger.warning(f"No location ID found - using fallback location ID: {fallback_location_id}")
            job_posting_data["location"] = fallback_location_id
        
        # Also try alternative field names that might be expected
        alt_job_posting_data = {
            "account_id": account_id,
            "title": {"text": job_data.get('title', '')},  # Alternative: 'title' instead of 'job_title'
            "company_name": company_id if company_id else {"text": job_data.get('company_name', '')},
            "workplace_type": self._map_workplace_type(job_data.get('job_type', 'full_time')),
            "employment_type": self._map_employment_status(job_data.get('job_type', 'full_time')),
            "job_description": self._format_job_description_for_linkedin(job_data),  # Alternative: 'job_description'
        }
        
        # Only add location if we have a numeric ID for alternative format
        if location_id:
            alt_job_posting_data["location_name"] = location_id
        else:
            # Use the same fallback location ID for alternative format
            alt_job_posting_data["location_name"] = "102277331"
        
        # Remove empty fields to avoid API errors
        job_posting_data = {k: v for k, v in job_posting_data.items() if v is not None and v != ''}
        
        # Add optional fields if available
        if job_data.get('auto_rejection_template'):
            job_posting_data["auto_rejection_template"] = job_data['auto_rejection_template']
        
        if job_data.get('screening_questions'):
            # Transform screening questions to match API format
            transformed_questions = []
            for i, question in enumerate(job_data['screening_questions']):
                answer_type = self._map_answer_type(question.get('type', 'text'))
                
                transformed_question = {
                    "question": question['question'],
                    "position": i,
                    "must_match": question.get('required', True),
                    "answer_type": answer_type,
                }
                
                # Add type-specific fields based on the mapped answer type
                if answer_type == "numeric":
                    # For numeric questions, we need min_expectation and max_expectation
                    # Since we don't have specific expectations, use reasonable defaults
                    transformed_question["min_expectation"] = 0
                    transformed_question["max_expectation"] = 100
                elif answer_type == "multiple_choices":
                    # For multiple choice questions, we need choices and expected_choices
                    # Since we don't have predefined choices, create generic ones
                    transformed_question["choices"] = ["Yes", "No"]
                    transformed_question["expected_choices"] = ["Yes"]
                
                transformed_questions.append(transformed_question)
            
            job_posting_data["screening_questions"] = transformed_questions
        
        # Log the data being sent for debugging
        logger.info(f"Sending LinkedIn job posting data: {job_posting_data}")
        

        
        try:
            # Use the correct LinkedIn jobs endpoint
            response = self._make_request('POST', '/linkedin/jobs', data=job_posting_data)
            logger.info(f"Successfully created LinkedIn job posting: {response}")
            return response
        except Exception as e:
            logger.error(f"Failed to create LinkedIn job posting: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    logger.error(f"Unipile API error details: {error_details}")
                except:
                    logger.error(f"Unipile API error response: {e.response.text}")
                    logger.error(f"Status code: {e.response.status_code}")
            return None
    
    def publish_linkedin_job(self, account_id: str, job_id: str, publish_options: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Publish a LinkedIn job posting"""
        if publish_options is None:
            publish_options = {"mode": "FREE"}  # Default to free posting
        
        publish_data = {
            "account_id": account_id,
            "service": "CLASSIC",
            "hiring_photo_frame": True,
            **publish_options
        }
        
        try:
            response = self._make_request('POST', f'/linkedin/jobs/{job_id}/publish', data=publish_data)
            logger.info(f"Successfully published LinkedIn job {job_id}: {response}")
            return response
        except Exception as e:
            logger.error(f"Failed to publish LinkedIn job {job_id}: {e}")
            return None
    
    def get_linkedin_job(self, account_id: str, job_id: str) -> Optional[Dict[str, Any]]:
        """Get LinkedIn job posting details"""
        try:
            params = {"account_id": account_id}
            response = self._make_request('GET', f'/linkedin/jobs/{job_id}', params=params)
            return response
        except Exception as e:
            logger.error(f"Failed to get LinkedIn job {job_id}: {e}")
            return None
    
    def list_linkedin_jobs(self, account_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """List all LinkedIn job postings"""
        try:
            params = {"account_id": account_id, "limit": limit}
            response = self._make_request('GET', '/linkedin/jobs', params=params)
            return response.get('jobs', []) if response else []
        except Exception as e:
            logger.error(f"Failed to list LinkedIn jobs: {e}")
            return []
    
    def close_linkedin_job(self, account_id: str, job_id: str) -> bool:
        """Close a LinkedIn job posting"""
        try:
            data = {"account_id": account_id}
            self._make_request('POST', f'/linkedin/jobs/{job_id}/close', data=data)
            logger.info(f"Successfully closed LinkedIn job {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to close LinkedIn job {job_id}: {e}")
            return False
    
    def get_job_applicants(self, account_id: str, job_id: str) -> List[Dict[str, Any]]:
        """Get applicants for a LinkedIn job posting"""
        try:
            params = {"account_id": account_id}
            response = self._make_request('GET', f'/linkedin/jobs/{job_id}/applicants', params=params)
            return response.get('applicants', []) if response else []
        except Exception as e:
            logger.error(f"Failed to get job applicants for {job_id}: {e}")
            return []
    
    def get_linkedin_search_parameters(self, account_id: str, param_type: str = "LOCATION") -> List[Dict[str, Any]]:
        """Get LinkedIn search parameters (locations, job titles, companies)"""
        try:
            params = {
                "account_id": account_id,
                "type": param_type
            }
            response = self._make_request('GET', '/linkedin/search/parameters', params=params)
            return response.get('items', []) if response else []
        except Exception as e:
            logger.error(f"Failed to get LinkedIn search parameters for type {param_type}: {e}")
            return []
    
    def test_api_endpoints(self) -> Dict[str, bool]:
        """Test various API endpoints to see which ones are available"""
        endpoints_to_test = [
            '/linkedin/jobs',
            '/accounts',
            '/linkedin/search/parameters',
            '/webhooks',
            '/linkedin/parameters',  # Try alternative endpoint
            '/linkedin/locations',   # Try direct locations endpoint
            '/linkedin/companies',   # Try direct companies endpoint
        ]
        
        results = {}
        
        for endpoint in endpoints_to_test:
            try:
                logger.info(f"Testing endpoint: {endpoint}")
                response = self._make_request('GET', endpoint)
                results[endpoint] = True
                logger.info(f"✅ Endpoint {endpoint} is available")
            except Exception as e:
                results[endpoint] = False
                logger.error(f"❌ Endpoint {endpoint} failed: {e}")
        
        return results
    
    def search_linkedin_locations(self, account_id: str, query: str = "") -> List[Dict[str, Any]]:
        """Search for LinkedIn locations by query"""
        try:
            params = {
                "account_id": account_id,
                "type": "LOCATION",
                "keywords": query
            }
            response = self._make_request('GET', '/linkedin/search/parameters', params=params)
            return response.get('items', []) if response else []
        except Exception as e:
            logger.error(f"Failed to search LinkedIn locations: {e}")
            return []
    
    def _map_workplace_type(self, job_type: str) -> str:
        """Map job type to LinkedIn workplace type"""
        workplace_mapping = {
            'remote': 'REMOTE',
            'hybrid': 'HYBRID',
            'full_time': 'ON_SITE',
            'part_time': 'ON_SITE',
            'contract': 'ON_SITE',
            'freelance': 'REMOTE',
            'internship': 'ON_SITE',
        }
        return workplace_mapping.get(job_type, 'ON_SITE')
    
    def _map_employment_status(self, job_type: str) -> str:
        """Map job type to LinkedIn employment status"""
        employment_mapping = {
            'full_time': 'FULL_TIME',
            'part_time': 'PART_TIME',
            'contract': 'CONTRACT',
            'freelance': 'CONTRACT',
            'internship': 'INTERNSHIP',
            'remote': 'FULL_TIME',
            'hybrid': 'FULL_TIME',
        }
        return employment_mapping.get(job_type, 'FULL_TIME')
    
    def _map_answer_type(self, question_type: str) -> str:
        """Map question type to LinkedIn answer type"""
        # According to the API error, only 'numeric' and 'multiple_choices' are valid
        type_mapping = {
            'text': 'numeric',  # Map text questions to numeric since text is not supported
            'boolean': 'numeric',  # Map boolean to numeric since boolean is not supported
            'numeric': 'numeric',
            'multiple_choice': 'multiple_choices',
            'single_choice': 'multiple_choices',  # Map single choice to multiple choices
        }
        return type_mapping.get(question_type, 'numeric')
    
    def _format_job_description_for_linkedin(self, job_data: Dict[str, Any]) -> str:
        """Format job data into LinkedIn job description with HTML"""
        title = job_data.get('title', '')
        company = job_data.get('company_name', '')
        location = job_data.get('location', '')
        description = job_data.get('description', '')
        responsibilities = job_data.get('responsibilities', '')
        requirements = job_data.get('requirements', '')
        nice_to_have = job_data.get('nice_to_have', '')
        salary_range = job_data.get('salary_range', '')
        category_name = job_data.get('category_name', '')
        skills_list = job_data.get('skills_list', [])
        
        # Create structured HTML description
        html_description = f"""
        <h2>About the Role</h2>
        <p>{description}</p>
        """
        
        # Add category if available
        if category_name:
            html_description += f"""
            <h3>Category</h3>
            <p>{category_name}</p>
            """
        
        html_description += f"""
        <h3>Key Responsibilities</h3>
        <p>{self._format_text_to_html(responsibilities)}</p>
        
        <h3>Requirements</h3>
        <p>{self._format_text_to_html(requirements)}</p>
        """
        
        if nice_to_have:
            html_description += f"""
            <h3>Nice to Have</h3>
            <p>{self._format_text_to_html(nice_to_have)}</p>
            """
        
        # Add skills if available
        if skills_list:
            skills_html = ', '.join([f'<strong>{skill}</strong>' for skill in skills_list])
            html_description += f"""
            <h3>Required Skills</h3>
            <p>{skills_html}</p>
            """
        
        if salary_range:
            html_description += f"""
            <h3>Compensation</h3>
            <p>{salary_range}</p>
            """
        
        html_description += f"""
        <h3>Location</h3>
        <p>{location}</p>
        
        <p><strong>Apply now to join our team at {company}!</strong></p>
        """
        
        return html_description.strip()
    
    def _format_text_to_html(self, text: str) -> str:
        """Convert plain text with bullet points to HTML"""
        if not text:
            return ""
        
        # Convert bullet points to HTML list
        lines = text.split('\n')
        html_lines = []
        in_list = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                # Remove bullet point and add as list item
                item_text = line[1:].strip()
                html_lines.append(f'<li>{item_text}</li>')
            else:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                if line:
                    html_lines.append(f'<p>{line}</p>')
        
        if in_list:
            html_lines.append('</ul>')
        
        return ''.join(html_lines)
    
    def create_job_post(self, account_id: str, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a job posting on LinkedIn (legacy method, use create_linkedin_job_posting instead)"""
        # Keep for backward compatibility, but redirect to new method
        return self.create_linkedin_job_posting(account_id, job_data)
    
    def _format_job_for_linkedin(self, job_data: Dict[str, Any]) -> str:
        """Format job data into LinkedIn post content"""
        title = job_data.get('title', '')
        company = job_data.get('company_name', '')
        location = job_data.get('location', '')
        job_type = job_data.get('job_type', '').replace('_', ' ').title()
        description = job_data.get('description', '')
        
        # Create a formatted post
        content = f"""🚀 We're Hiring: {title}
        
🏢 Company: {company}
📍 Location: {location}
💼 Type: {job_type}

{description[:500]}{'...' if len(description) > 500 else ''}

#hiring #jobs #linkedin #career #opportunity
        """
        
        return content.strip()
    
    def setup_webhooks(self) -> Dict[str, bool]:
        """Setup all required webhooks"""
        webhook_types = [
            ('account_status', 'Account Status Update'),
            ('messaging', 'Messaging Multiple events'),
            ('mailing', 'Mailing Multiple events'),
            ('mail_tracking', 'Mail Tracking Multiple events'),
            ('users_relations', 'Users Relations events'),
        ]
        
        results = {}
        
        for webhook_type, description in webhook_types:
            success = self.create_webhook(webhook_type, description)
            results[webhook_type] = success
        
        return results
    
    def create_webhook(self, webhook_type: str, name: str) -> bool:
        """Create a webhook for specific event type"""
        webhook_data = {
            'name': name,
            'url': f"{self.webhook_url}/{webhook_type}/",
            'events': self._get_webhook_events(webhook_type),
            'active': True
        }
        
        try:
            response = self._make_request('POST', '/webhooks', data=webhook_data)
            logger.info(f"Created webhook for {webhook_type}: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to create webhook for {webhook_type}: {e}")
            return False
    
    def _get_webhook_events(self, webhook_type: str) -> List[str]:
        """Get events to subscribe to for each webhook type"""
        event_mapping = {
            'account_status': ['account.status_updated', 'account.connected', 'account.disconnected'],
            'messaging': ['message.sent', 'message.received', 'message.failed'],
            'mailing': ['email.sent', 'email.delivered', 'email.failed', 'email.bounced'],
            'mail_tracking': ['email.opened', 'email.clicked', 'email.unsubscribed'],
            'users_relations': ['connection.added', 'connection.removed', 'profile.updated'],
        }
        
        return event_mapping.get(webhook_type, [])
    
    def get_webhooks(self) -> List[Dict[str, Any]]:
        """Get all configured webhooks"""
        try:
            return self._make_request('GET', '/webhooks')
        except Exception as e:
            logger.error(f"Failed to get webhooks: {e}")
            return []
    
    def delete_webhook(self, webhook_id: str) -> bool:
        """Delete a webhook"""
        try:
            self._make_request('DELETE', f'/webhooks/{webhook_id}')
            logger.info(f"Deleted webhook {webhook_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete webhook {webhook_id}: {e}")
            return False
    
    def send_message(self, account_id: str, recipient: str, message: str) -> Optional[Dict[str, Any]]:
        """Send a message via LinkedIn"""
        message_data = {
            'recipient': recipient,
            'message': message,
            'provider': 'linkedin'
        }
        
        try:
            response = self._make_request('POST', f'/accounts/{account_id}/messages', data=message_data)
            logger.info(f"Message sent via account {account_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to send message via account {account_id}: {e}")
            return None
    
    def get_messages(self, account_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get messages from account"""
        try:
            params = {'limit': limit}
            response = self._make_request('GET', f'/accounts/{account_id}/messages', params=params)
            return response.get('messages', [])
        except Exception as e:
            logger.error(f"Failed to get messages from account {account_id}: {e}")
            return []
    
    def search_profiles(self, account_id: str, query: str, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for profiles on LinkedIn"""
        search_data = {
            'query': query,
            'provider': 'linkedin',
            **(filters or {})
        }
        
        try:
            response = self._make_request('POST', f'/accounts/{account_id}/search/profiles', data=search_data)
            return response.get('profiles', [])
        except Exception as e:
            logger.error(f"Failed to search profiles: {e}")
            return []


class UnipileAPIError(Exception):
    """Custom exception for Unipile API errors"""
    pass


# Utility functions for webhook processing
def process_webhook_payload(webhook_type: str, payload: Dict[str, Any]) -> bool:
    """Process incoming webhook payload"""
    try:
        if webhook_type == 'account_status':
            return _process_account_status_webhook(payload)
        elif webhook_type == 'messaging':
            return _process_messaging_webhook(payload)
        elif webhook_type == 'mailing':
            return _process_mailing_webhook(payload)
        elif webhook_type == 'mail_tracking':
            return _process_mail_tracking_webhook(payload)
        elif webhook_type == 'users_relations':
            return _process_users_relations_webhook(payload)
        else:
            logger.warning(f"Unknown webhook type: {webhook_type}")
            return False
    except Exception as e:
        logger.error(f"Error processing {webhook_type} webhook: {e}")
        return False


def _process_account_status_webhook(payload: Dict[str, Any]) -> bool:
    """Process account status update webhook"""
    event_type = payload.get('event_type')
    account_id = payload.get('account_id')
    
    logger.info(f"Account status update: {event_type} for account {account_id}")
    
    # Handle account disconnection
    if event_type == 'account.disconnected':
        # Update any jobs that were posted via this account
        from .models import Job
        jobs = Job.objects.filter(unipile_account_id=account_id, posted_to_linkedin=True)
        jobs.update(posted_to_linkedin=False)
        logger.info(f"Updated {jobs.count()} jobs due to account disconnection")
    
    return True


def _process_messaging_webhook(payload: Dict[str, Any]) -> bool:
    """Process messaging webhook"""
    event_type = payload.get('event_type')
    message_data = payload.get('data', {})
    
    logger.info(f"Messaging event: {event_type}")
    
    # Handle message responses (could be job application inquiries)
    if event_type == 'message.received':
        # Log the message for potential job application follow-ups
        logger.info(f"Received message: {message_data.get('content', '')[:100]}")
    
    return True


def _process_mailing_webhook(payload: Dict[str, Any]) -> bool:
    """Process mailing webhook"""
    event_type = payload.get('event_type')
    email_data = payload.get('data', {})
    
    logger.info(f"Mailing event: {event_type}")
    
    # Handle email delivery status for job-related emails
    if event_type in ['email.delivered', 'email.failed', 'email.bounced']:
        email_id = email_data.get('email_id')
        logger.info(f"Email {email_id} status: {event_type}")
    
    return True


def _process_mail_tracking_webhook(payload: Dict[str, Any]) -> bool:
    """Process mail tracking webhook"""
    event_type = payload.get('event_type')
    tracking_data = payload.get('data', {})
    
    logger.info(f"Mail tracking event: {event_type}")
    
    # Track engagement with job-related emails
    if event_type == 'email.opened':
        logger.info(f"Email opened: {tracking_data.get('email_id')}")
    elif event_type == 'email.clicked':
        logger.info(f"Email link clicked: {tracking_data.get('link_url')}")
    
    return True


def _process_users_relations_webhook(payload: Dict[str, Any]) -> bool:
    """Process users relations webhook"""
    event_type = payload.get('event_type')
    relation_data = payload.get('data', {})
    
    logger.info(f"Users relations event: {event_type}")
    
    # Track new connections (potential candidates)
    if event_type == 'connection.added':
        connection_info = relation_data.get('connection', {})
        logger.info(f"New connection added: {connection_info.get('name')}")
    
    return True

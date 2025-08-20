# RecruiterAI Backend

A comprehensive Django-based recruitment platform backend with REST API and Swagger documentation.

## Features

- **User Authentication & Management**: Custom user model with different user types (Recruiter, Job Seeker, Admin)
- **Recruiter Management**: Company profiles, recruiter profiles, and job posting capabilities
- **Job Management**: Job search, bookmarks, and AI-powered recommendations
- **Application Tracking**: Complete job application lifecycle management
- **Interview Management**: Interview scheduling and tracking
- **Swagger Documentation**: Complete API documentation using drf-spectacular
- **Modern Django**: Built with Django 4.2+ and Django REST Framework

## Project Structure

```
backend/
├── config/                 # Main Django configuration
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   ├── admin.py          # Admin interface configuration
│   ├── wsgi.py           # WSGI configuration
│   └── asgi.py           # ASGI configuration
├── apps/                  # Django applications
│   ├── authentication/    # User authentication and profiles
│   ├── users/            # User activities and notifications
│   ├── recruiters/       # Recruiter and company management
│   ├── jobs/             # Job search and recommendations
│   └── applications/     # Job applications and interviews
├── requirements.txt       # Python dependencies
├── manage.py             # Django management script
└── env.example           # Environment variables template
```

## Installation

### Option 1: Poetry Setup with Supabase (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RecruiterAI_Backend/backend
   ```

2. **Run the Poetry setup script**
   ```bash
   python poetry_setup.py
   ```
   This script will:
   - Install Poetry if not present
   - Set up Poetry project and virtual environment
   - Install all dependencies
   - Test Supabase database connection
   - Create environment configuration
   - Run migrations
   - Set up pre-commit hooks
   - Optionally create a superuser

3. **Start the development server**
   ```bash
   poetry run python manage.py runserver
   ```

### Option 2: Manual Poetry Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RecruiterAI_Backend/backend
   ```

2. **Install Poetry** (if not already installed)
   ```bash
   pip install poetry
   ```

3. **Install dependencies**
   ```bash
   poetry install
   poetry install --with dev
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your Supabase database configuration
   ```

5. **Run migrations**
   ```bash
   poetry run python manage.py makemigrations
   poetry run python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   poetry run python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   poetry run python manage.py runserver
   ```

### Option 3: Traditional pip Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RecruiterAI_Backend/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your Supabase database configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## API Documentation

The API documentation is automatically generated using drf-spectacular and available at:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/update/` - Update user profile
- `POST /api/auth/change-password/` - Change password

### Users
- `GET /api/users/activities/` - Get user activities
- `GET /api/users/notifications/` - Get user notifications
- `POST /api/users/notifications/{id}/read/` - Mark notification as read

### Recruiters
- `GET /api/recruiters/companies/` - Get company list
- `GET /api/recruiters/companies/{id}/` - Get company details
- `GET /api/recruiters/profile/` - Get recruiter profile
- `GET /api/recruiters/jobs/` - Get recruiter's job posts
- `POST /api/recruiters/jobs/create/` - Create new job post

### Jobs
- `GET /api/jobs/search/` - Search for jobs
- `GET /api/jobs/categories/` - Get job categories
- `GET /api/jobs/bookmarks/` - Get job bookmarks
- `GET /api/jobs/recommendations/` - Get job recommendations

### Applications
- `GET /api/applications/` - Get user applications
- `POST /api/applications/create/` - Create job application
- `GET /api/applications/{id}/` - Get application details
- `GET /api/applications/{id}/interviews/` - Get application interviews

## Models

### Core Models
- **User**: Custom user model with authentication
- **UserProfile**: Extended user profile information
- **Company**: Company information for recruiters
- **RecruiterProfile**: Recruiter-specific profile data
- **JobPost**: Job posting details
- **JobApplication**: Job application tracking
- **Interview**: Interview scheduling and management

### Supporting Models
- **UserActivity**: User activity tracking
- **UserNotification**: User notification system
- **JobCategory**: Job categorization
- **JobSearch**: Search history and preferences
- **JobBookmark**: Job bookmarks
- **JobRecommendation**: AI-powered job recommendations

## Configuration

### Supabase Database Configuration

The project is configured to use Supabase PostgreSQL database by default:

```bash
# Database Settings - Supabase PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=
DB_HOST=db.ummbhscjtbrynnicptpm.supabase.co
DB_PORT=5432
DB_SSL_MODE=require
```

### Environment Variables
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_ENGINE`: Database engine (default: postgresql)
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DB_PORT`: Database port
- `DB_SSL_MODE`: SSL mode for database connection

### Database
- **Development & Production**: PostgreSQL via Supabase (default)
- **Alternative**: SQLite3 for local development (change DB_ENGINE in .env)

### File Storage
- **Development**: Local file system
- **Production**: AWS S3 (configurable)

## Development

### Poetry Commands

```bash
# Install dependencies
poetry install                    # Install all dependencies
poetry install --with dev        # Install dev dependencies

# Add/Remove packages
poetry add <package>             # Add a dependency
poetry add --group dev <package> # Add dev dependency
poetry remove <package>          # Remove a dependency

# Update dependencies
poetry update                    # Update all dependencies
poetry update <package>          # Update specific package

# Run commands
poetry run python manage.py <cmd> # Run Django commands
poetry shell                     # Activate virtual environment

# Project info
poetry show                      # Show installed packages
poetry env info                  # Show environment info
poetry version                   # Show project version
```

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Use type hints where appropriate

### Testing

#### Poetry Setup Test
```bash
python test_poetry.py
```

#### Database Connection Test
```bash
poetry run python test_supabase.py
```

#### Django Tests
```bash
poetry run python manage.py test
poetry run pytest
```

### Code Quality
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run linting
flake8 .
black .
isort .
```

## Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure production database
- [ ] Set up static file serving
- [ ] Configure email backend
- [ ] Set up logging
- [ ] Configure CORS settings
- [ ] Set up SSL/TLS
- [ ] Configure backup strategy

### Docker Deployment

#### Using Poetry (Recommended)
```bash
# Build image with Poetry
docker build -f Dockerfile.poetry -t recruiterai-backend .

# Run with docker-compose
docker-compose -f docker-compose.poetry.yml up

# Or run container directly
docker run -p 8000:8000 recruiterai-backend
```

#### Traditional pip
```bash
# Build image
docker build -t recruiterai-backend .

# Run container
docker run -p 8000:8000 recruiterai-backend
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on GitHub or contact the development team.

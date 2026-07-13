# Image-Processing-Service

Image processing service REST API built with Python and FastAPI

## Features

### Registration
- User can create account

### Login
- User can login after creating account

### Upload Image
- Authentication is required
- User can upload image
- maximal resolution: 5000 x 5000 pixels
- Maximal file size: 10MB
- Allowed formats: JPEG, PNG, WEBP

## Installation
1. Clone the repository:

```bash
git clone https://github.com/Eeernest/Image-Processing-Service.git
cd Image-Processing-Service
```

2. Creae virtual environment:

```bash
python -m venv .venv
source .venv\bin\activate # Linux/macOS
.venv\Scripts\activate    # Windows
```

3. Create an .env file in the project root:

```env
# POSTGRESQL

POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_postgres_db

# Database URL format: postgresql://USER:PASSWORD@HOST:PORT/DB
POSTGRES_URL=your_postgres_url

# IMAGE

MAX_IMAGE_WIDTH
MAX_IMAGE_HEIGHT

# ADMIN

ADMIN_USERNAME
ADMIN_EMAIL
ADMIN_PASSWORD
ADMIN_HASHED_PASSWORD

# SECURITY

DUMMY_PASSWORD
SECRET_KEY
ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES


# AWS

S3_BUCKET_NAME
S3_BUCKET_REGION
S3_ACCESS_KEY_ID
S3_SECRET_ACCESS_KEY
```

> Do not commit real credentials. Replace all values with your own before running the application.

4. Run the application using Docker Compose:

```bash
docker compose up --build
```

5. Run tests locally:

```bash
pytest
```

## Access:
- API Documentation: http://localhost:8000/docs
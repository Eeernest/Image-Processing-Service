# Image-Processing-Service

Image processing service REST API built with Python and FastAPI

## Features

### Registration
- User can create account

## Instalation
1. Clone the repository:

```bash
git clone https://github.com/Eeernest/Image-Processing-Service.git
cd Image-Processing-Service
```

2. Creae virtual environment:

```bash
python -m venv venv
source venv\bin\activate # Linux/macOS
venv\Scripts\activate    # Windows
```

3. Create an .env file in the project root:

```env
# POSTGRESQL

POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_postgres_db

# Database URL format: postgresql://USER:PASSWORD@HOST:PORT/DB
POSTGRES_URL=your_postgres_url
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
# AI Tools Registry API
A Django REST API for managing and exploring AI tools with NLP-powered recommendations.

## Features
- Tool registry: browse, add, and retrieve AI tools.
- User favourites: save favourite tools and manage them per user.
- Email alerts: notify users about new tools matching their interests.
- NLP-powered recommendations: recommend relevant tools based on user queries.
- Async job processing: submit long-running jobs (e.g., NLP processing). Receive results via HTTP polling or Websocket connection.
- JWT authentication: secure endpoints with token-based auth.
- Permissions: fine-grained access control: public, authenticated users, or staff-only.
- OpenAPI docs: auto-generated Swagger/Redoc via `drf-spectacular`.

## Setup
```bash
# Install dependencies in Pipenv environment
pipenv install

# Enter Pipenv shell
pipenv shell

# Create database
python manage.py migrate

# Fill with dataset
python manage.py download_dataset

# Compute embeddings for NLP queries
python manage.py compute_embeddings

# Optionally, set up superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```
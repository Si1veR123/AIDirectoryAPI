Setup:
```
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
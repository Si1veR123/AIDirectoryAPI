AI usages:
- i am using django with django rest framework. how do i set up an api in a 'user' app for sign up and authentication
- how do i extend the user model to add custom fields
Good question — this is very important to get right early, because changing the user model later is painful.

In Django you have two ways to extend the user model:

✅ Best practice (recommended): Create a Custom User model

⚠️ Alternative: Create a Profile model with OneToOneField

Since you’re building an API with Django REST Framework, I strongly recommend custom user model.

- how do i use django models outside of django. i want to set up the database from a downloaded dataset before the server starts
✅ Best Practice: Use a Custom Django Management Command

This is the most “Django-native” way.

Why this is best:

Uses Django properly

Has full ORM access

Runs before server

Works in production + CI

Clean and maintainable

- import kagglehub
import csv
import os
from django.core.management.base import BaseCommand
from tool.models import Tool, Developer, Domain, Accessibility, ContextWindow

DB_PATH = "../../../db.sqlite3"
FILE_NAME = "AI_Landscape_19k_Tools_2026.csv"
DATASET_NAME = "harshlakhani2005/ai-tool-directory-2026-10000-real-world-tools"

class Command(BaseCommand):
    help = "Load initial dataset into database"

    def handle(self, *args, **kwargs):
        # Download latest version
        path = kagglehub.dataset_download(DATASET_NAME)

        # Clear existing data
        Tool.objects.all().delete()
        Developer.objects.all().delete()
        Domain.objects.all().delete()
        Accessibility.objects.all().delete()
        ContextWindow.objects.all().delete()

        # Load data into database
        with open(os.path.join(path, FILE_NAME), 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                developer, _ = Developer.objects.get_or_create(name=row['Developer'])
                domain, _ = Domain.objects.get_or_create(name=row['Primary_Domain'])
                accessibility, _ = Accessibility.objects.get_or_create(name=row['Accessibility'])
                context_window, _ = ContextWindow.objects.get_or_create(name=row['Context_Window'])

                Tool.objects.create(
                    ai_name=row['AI_Name'],
                    developer=developer,
                    release_year=int(row['Release_Year']),
                    intelligence_type=row['Intelligence_Type'],
                    primary_domain=domain,
                    key_functionality=row['Key_Functionality'],
                    pricing_model=row['Pricing_Model'],
                    api_availability=(row['API_Availability']),
                    context_window=context_window,
                    accessibility=accessibility,
                    popularity_votes=int(row['Popularity_Votes']),
                    website_url=row['Website_URL']
                )
        
        self.stdout.write(self.style.SUCCESS('Dataset loaded successfully!'))

make this code more efficient for inserting bulk rows. dataset is 10k rows.

minutes to instant

- what python frameworks are there that work with django to generate documentation. i also want to be able to add structured docstrings to functions that will be included

- give me an overview of features in spectacular and how i can use it in my project with drf

- prefix vs basename in rest framework router.register
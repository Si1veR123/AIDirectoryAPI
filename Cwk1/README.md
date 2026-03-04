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

- how do i add authentication requirements to endpoints. i want tool endpoints to be read only for normal users, any operation for admin/superuser

✅ Step 1 — Create a Custom Permission Class

Create a new file:

tools/permissions.py

Add:

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Allow read-only access to anyone.
    Only admins/superusers can modify.
    """

    def has_permission(self, request, view):
        # SAFE_METHODS = GET, HEAD, OPTIONS
        if request.method in SAFE_METHODS:
            return True
        
        # Write permissions only for admin users
        return request.user and request.user.is_staff
Why is_staff and not is_superuser?

is_staff → Django admin access

is_superuser → full unrestricted access

For coursework clarity, is_staff is standard.

If you want strictly superusers only:

return request.user and request.user.is_superuser
✅ Step 2 — Apply It to Your ViewSet

In your ToolViewSet:

from rest_framework.viewsets import ModelViewSet
from .models import Tool
from .serializers import ToolSerializer
from .permissions import IsAdminOrReadOnly

class ToolViewSet(ModelViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    permission_classes = [IsAdminOrReadOnly]

That’s it.

🔐 Step 3 — Ensure Authentication Is Enabled

In settings.py, make sure you have:

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",  # default for other views
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
}

- validate doesnt run on patch
Good — this is a very important DRF behaviour detail.

You're correct:

validate() does not behave the way you expect on PATCH.

Here’s why.

🔍 Why validate() “doesn’t run” on PATCH

It does run, but:

On PATCH (partial update):

Only the fields provided are in attrs

Missing fields are NOT included

So your logic breaks if you expect both username and password to exist

Example PATCH:

{
  "password": "john"
}

Inside validate(self, attrs):

attrs == {
    "password": "john"
}

There is no username in attrs.

So when you do:

user = User(
    username=attrs.get("username"),
    email=attrs.get("email"),
)

Both are None.

So Django can’t compare password to username.
So similarity validation does nothing.

✅ Correct Solution: Use self.instance During Update

When updating, DRF gives you the existing object via self.instance.

So you must merge:

Existing user values

New incoming values

✅ Correct Implementation
def validate(self, attrs):
    # If updating, use existing instance values
    if self.instance:
        username = attrs.get("username", self.instance.username)
        email = attrs.get("email", self.instance.email)
    else:
        username = attrs.get("username")
        email = attrs.get("email")

    password = attrs.get("password")

    if password:
        temp_user = User(
            username=username,
            email=email,
        )
        validate_password(password, temp_user)

    return attrs
🔥 Why This Works

On PATCH:

{
  "password": "john"
}

If current user is:

username = "john"

Then:

attrs.get("username") → None

fallback to self.instance.username → "john"

similarity validator now works

So "password": "john" will correctly fail.

🧠 Key Concept

DRF update flow:

POST → self.instance is None

PUT/PATCH → self.instance is the object being updated

PATCH → attrs only contains changed fields

You must manually merge old + new values during validation.
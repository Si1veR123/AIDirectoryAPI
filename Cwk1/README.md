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

- Suggest ways to extend my current project that implement modern standards, complex database structures and more advanced endpoints
1. Data Model & CRUD Extensions

You already have a basic data model with endpoints. To go beyond the minimum:

Relational enhancements

Introduce related models with foreign keys and nested CRUD operations.

Example: User → Project → Tool hierarchy, where each user can have multiple projects and each project multiple tools.

Implement cascade or restricted deletes, and show how API handles them (complex behavior = originality).

GraphQL Option:

Consider a GraphQL API for nested data retrieval.

Example: query a user and get all projects + tools in a single request with filtering and sorting.

Justify the choice: reduces over-fetching, flexible for GenAI clients that may want contextual data dynamically.

2. Advanced Endpoint Ideas

Beyond basic CRUD, consider endpoints that add value:

Search & Filter:

GET /tools?name=drill&category=hardware

Could integrate full-text search using SQLite FTS or PostgreSQL.

Batch Operations:

POST /tools/batch to create multiple tools at once, return per-item status.

Analytics Endpoints:

Count of tools per user/project, average usage, or last updated timestamp.

Custom Actions / GenAI Integration:

Example: /tools/suggest → takes a partial description and returns AI-suggested new tools (leveraging OpenAI GPT or similar).

Could be modeled as a “creative assistant” endpoint, directly connecting your API to GenAI.

3. Error Handling & Status Codes

Expand your API to handle business logic errors, not just 404/500.

Example: “Cannot delete project with active tools” → 409 Conflict.

Demonstrate nested validation, e.g., updating a tool requires valid project ownership.

4. Authentication & Personalisation

Add JWT or session-based auth with per-user data isolation.

Provide role-based endpoints:

Admin can CRUD all projects/tools, users can only CRUD their own.

Extend with rate-limiting per user for creative AI endpoints to show production awareness.

5. Novel Features / Generative AI Applications

This is where you can score high marks:

AI-Assisted CRUD

POST /tools/auto-create → user provides a description, AI fills in missing fields, tags, or categories.

Could use prompt engineering to generate realistic tool specs.

Data Augmentation / Enrichment

AI endpoint can generate example use cases, images, or documentation for each tool.

Predictive Suggestions

/tools/recommend → suggest similar tools based on existing user projects. Could use embeddings or GPT-4 style similarity searches.

Interactive Documentation / Playground

Embed Redoc or Swagger UI with live examples.

AI could generate example payloads automatically from your models.

6. Design / Architecture Innovation

Consider async FastAPI or Django Channels for real-time endpoints.

Use caching (Redis) for repeated AI queries to reduce latency.

Implement OpenAPI / GraphQL schema generation, emphasizing best practices.

- make a viewset that has parameters q (search query for field ai_name), and a parameter for each field in Tool. it should check if the value is equal to the field. for the integer fields, it should have a parameter field-max and field-min that returns results between the 2 values. if only field-max is given, return everything less than the value and vice versa for field-min. also have a sort-by and order=desc/asc parameter that takes a field and sorts by the given field. add documentation.

Below is a clean DRF ViewSet implementation that supports everything you asked:

Features:

q → search ai_name

field=value → exact match filter for every Tool field

field-min / field-max → range filtering for integer fields

sort-by → choose field to sort

order=asc|desc

documented query parameters using drf-spectacular

This assumes:

Tool model exists

you are using DRF + drf-spectacular

ToolSearchViewSet
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Tool
from .serializers import ToolSerializer


class ToolSearchViewSet(ViewSet):

    @extend_schema(
        description="""
Search tools using flexible query parameters.

Query Parameters
----------------
q:
    Searches the ai_name field.

Field filters:
    Any Tool field can be filtered using ?field=value.

Range filters for integer fields:
    ?field-min=value
    ?field-max=value

Examples:
    /tools/search?q=vision  
    /tools/search?category=nlp  
    /tools/search?downloads-min=1000  
    /tools/search?downloads-min=1000&downloads-max=10000  

Sorting:
    sort-by=<field>
    order=asc|desc

Examples:
    /tools/search?sort-by=downloads&order=desc
""",
        parameters=[
            OpenApiParameter(
                name="q",
                description="Search query for ai_name",
                required=False,
                type=str
            ),
            OpenApiParameter(
                name="sort-by",
                description="Field to sort by",
                required=False,
                type=str
            ),
            OpenApiParameter(
                name="order",
                description="Sorting order (asc or desc)",
                required=False,
                type=str
            ),
        ],
    )
    def list(self, request):

        queryset = Tool.objects.all()
        params = request.query_params

        # --- search query ---
        q = params.get("q")
        if q:
            queryset = queryset.filter(ai_name__icontains=q)

        # --- dynamic field filtering ---
        for field in Tool._meta.fields:

            name = field.name

            # skip id field if desired
            if name == "id":
                continue

            # exact match filter
            value = params.get(name)
            if value is not None:
                queryset = queryset.filter(**{name: value})

            # range filters for integer fields
            if field.get_internal_type() in ["IntegerField", "BigIntegerField", "FloatField"]:

                min_param = params.get(f"{name}-min")
                max_param = params.get(f"{name}-max")

                if min_param is not None:
                    queryset = queryset.filter(**{f"{name}__gte": min_param})

                if max_param is not None:
                    queryset = queryset.filter(**{f"{name}__lte": max_param})

        # --- sorting ---
        sort_by = params.get("sort-by")
        order = params.get("order", "asc")

        if sort_by:
            if order == "desc":
                sort_by = f"-{sort_by}"
            queryset = queryset.order_by(sort_by)

        serializer = ToolSerializer(queryset, many=True)
        return Response(serializer.data)

- does the documentation support having a dynamic number of fields
Short answer: not really.
OpenAPI (which tools like drf-spectacular generate) expects the set of query parameters to be known at schema-generation time. A truly runtime-dynamic set of parameters isn’t part of the spec.

But there are three practical approaches.

1️⃣ Generate Parameters Dynamically at Schema Time (Best Option)

You can dynamically generate parameters from the model fields when the schema is built. The number of parameters is dynamic in your code, but the generated schema is still static.

Example:

from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Tool


def build_search_params():
    params = [
        OpenApiParameter("q", str, description="Search ai_name"),
        OpenApiParameter("sort-by", str, description="Field to sort by"),
        OpenApiParameter("order", str, description="asc or desc"),
    ]

    for field in Tool._meta.fields:
        name = field.name

        params.append(
            OpenApiParameter(
                name=name,
                type=str,
                description=f"Exact match filter for {name}",
                required=False,
            )
        )

        if field.get_internal_type() in ["IntegerField", "FloatField"]:
            params.append(
                OpenApiParameter(
                    name=f"{name}-min",
                    type=float,
                    description=f"Minimum {name}",
                    required=False,
                )
            )
            params.append(
                OpenApiParameter(
                    name=f"{name}-max",
                    type=float,
                    description=f"Maximum {name}",
                    required=False,
                )
            )

    return params

Then:

@extend_schema(parameters=build_search_params())
def list(self, request):

✔ Docs automatically update if your model changes
✔ Looks very polished for coursework

- i want to get an update when a tool is given a specific domain. how should i do this? can i detect when a new foreign key to a domain is created in the domain model? or should i do this in tool serializer/viewset?
Better: Detect If The Domain Actually Changed

Use pre_save to compare the old value.

from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Tool

@receiver(pre_save, sender=Tool)
def detect_domain_change(sender, instance, **kwargs):

    if not instance.pk:
        return  # new object

    old = Tool.objects.get(pk=instance.pk)

    if old.domain != instance.domain:
        print(
            f"Domain changed from {old.domain} to {instance.domain}"
        )

This triggers when:

Tool A
domain = NLP → Vision
Where to Put This

Create a file:

tools/signals.py

Then register it in:

tools/apps.py
class ToolsConfig(AppConfig):
    name = "tools"

    def ready(self):
        import tools.signals

- i want to send an email on signal. should i do this instantly or schedule it with a job scheduler (celery?)
For your use case (send an email when a tool gets assigned a domain), the decision depends on reliability and user experience, but for most APIs the best practice is:

Trigger the event with a signal → send the email asynchronously with a task queue.

So the architecture becomes:

Tool saved
   ↓
Django signal fires
   ↓
enqueue background task
   ↓
worker sends email

This prevents API requests from blocking while the email is sent.

Why You Should Not Send Email Directly in the Signal

If you do:

send_mail(...)

inside the signal:

Problems:

Slow API response

SMTP calls can take seconds.

Failure breaks the request

Email server timeout → API request fails.

Poor scalability

Many events → your API becomes slow.

Best Architecture

Use a task queue like Celery.

Flow:

Tool save
   ↓
Signal
   ↓
Celery task
   ↓
Email sent by worker

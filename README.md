# AI Tools Registry API
A Django REST API for managing and exploring AI tools with NLP-powered recommendations.

Models are based on the Kaggle dataset [here](https://www.kaggle.com/datasets/harshlakhani2005/ai-tool-directory-2026-10000-real-world-tools).

Presentation slides [here](https://docs.google.com/presentation/d/1Fn1ep_j_10npwcVNG09A1xmPbFCN9b2-84frUnoNELk/edit?usp=sharing).

## Full Setup
Steps 3 and 4 can be skipped if the existing database is used. It has a superuser with the credentials:
```
User: superuser
Pass: superuser
```

```bash
# 1) (In /Cwk1 directory) Install dependencies in Pipenv environment
pipenv install

# 2) Enter Pipenv shell
pipenv shell

# 3) Create database
python manage.py migrate

# 4) Set up superuser
python manage.py createsuperuser

# 5) Fill with dataset
python manage.py download_dataset

# 6) Compute embeddings for NLP queries
python manage.py compute_embeddings

# Run server
python manage.py runserver
```


## Features
- Tool registry: browse, add, and retrieve AI tools.
- User favourites: save favourite tools and manage them per user.
- Email alerts: notify users about new tools matching their interests.
    - Enabled by providing the environment variable: `AIDIRECTORYAPI_EMAIL_CREDENTIALS=email;apppassword`
    - Default settings are configured for an AOL SMTP server but can be modified by `EMAIL_HOST` and `EMAIL_PORT` settings
- NLP-powered recommendations: recommend relevant tools based on user queries.
- Async job processing: submit long-running jobs (e.g., NLP processing). Receive results via HTTP polling or Websocket connection.
- JWT authentication: secure endpoints with token-based auth.
- Permissions: fine-grained access control: public, authenticated users, or staff-only.
- Throttling: endpoints are throttled to prevent excessive usage. Rate is higher for authenticated users.
- OpenAPI docs: auto-generated Swagger/Redoc via `drf-spectacular`.

## API Overview
See Swagger Documentation in the [PDF](AI%20Tools%20API.pdf) for details such as payload and response formats.

### Register
- `POST /api/user/register/` - create a user account

### User Auth
- `POST /api/user/token/` - get a JWT token from credentials
- `POST /api/user/token/refresh/` - use a refresh token to get a new access token

### Current User
- `GET/PUT/PATCH/DELETE /api/user/current/` - REST endpoint for currently authenticated user

### Admin User Management
A REST endpoint for admin/staff users to access any user. The serializer ensures that a user can only modify fields that it has permissions for (e.g. a staff cannot set `is_superuser: true`)
- `GET/POST /api/user/`
- `GET/PUT/PATCH/DELETE /api/user/{id}`

### Favourites
A REST endpoint to easily manage a user's favourites list by `ai_name` field. This allows a user can use this to keep a record of tools they like. The user endpoints also allow modifying favourites list, so this endpoint is an ease-of-use feature.

- `GET/POST /api/user/{user_id}/favourites/` - staff only
- `DELETE /api/user/{user_id}/favourites/{ai_name}/` - staff only
- `GET/POST /api/user/current/favourites/`
- `DELETE /api/user/current/favourites/{ai_name}/`

### Tools
A REST endpoint for the main AI tools table. This is read only for non-staff.

- `GET /api/tools/` - Paginated endpoint to view tools - open to anyone
- `POST /api/tools/` - staff only
- `GET /api/tools/{id}/`- retrieve information on a specific tool by ID - open to anyone
- `PUT/PATCH/DELETE /api/tools/{id}/` - staff only

### Tool Search
An endpoint that allows searching the tools table, with pagination. This has the following query parameters:
- `q` - Search by partial match in `ai_name`
- `field=value` - Search for an exact match on a specific Tool field
- `field-min=value, field-max=value` - On integer fields, search by a given range
- `sort-by=field, order=asc|desc` - Sort by a given field and order
- `page, page_size` - pagination parameters

#### Endpoints
- `GET /api/tools/search/`

### Recommendations
Endpoints to manage NLP powered tool recommendations from a query. This is powered by the `all-MiniLM-L6-v2` model. Internally, it is implemented with tasks so the result is not ready instantly. Instead, a results item is created on a POST request. This results item can be used to retrieve results from a HTTP endpoint, or subscribe to a websocket endpoint that sends the result when it is ready. Normal users can only access recommendations that they created.

- `GET /api/tools/recommend/` - get a list of all recommendation results. Query parameter `completed=true|false` can be used to filter completed recommendations. Normal users can only access their own results
- `POST /api/tools/recommend/` - create a recommendation by a natural language query and number of tools to recommend
- `GET/DELETE /api/tools/recommend/{id}/` - get/delete the results of a specific recommendation task by ID
- `ws://hostserver.com/ws/recommend/{id}` - creating a websocket connection to this endpoint will return the recommendation results when they are available

### Tool Subtables
REST endpoints to manage categories of a Tool object. Read only for non-staff.

- `Accessibilities` - ways to access this AI tool e.g. Browser Extension
- `Context Windows` - length of the tool's context window e.g. 32k tokens
- `Developers` - name of the tool's developer
- `Domains` - the primary domain of the tool e.g. Video

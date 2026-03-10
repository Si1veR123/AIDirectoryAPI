# Plan
1) Intro
2) Open endpoints
    - Paginated tool list
    - Search
    - Get developers
3) Register User
4) Login user
5) Current user GET
6) Current user PATCH
7) Create recommendation
9) HTTP recommendation result
8) Websocket python demo
10) Get superuser token
11) List all users


# Script
export API=http://localhost:8000

# 1
curl "$API/api/tools/?page=1&page_size=5"

# 2
curl "$API/api/tools/search/?q=video&sort-by=ai_name&order=asc&page_size=5"

# 3
curl "$API/api/tools/developers/"

# 4
curl -X POST "$API/api/user/register/" \
-H "Content-Type: application/json" \
-d '{
  "username": "demo_user",
  "email": "demo@example.com",
  "password": "password123"
}'

# 5
curl "$API/api/user/current/" \
-H "Authorization: Bearer $TOKEN"

# 6
curl -X POST "$API/api/user/token/" \
-H "Content-Type: application/json" \
-d '{
  "username": "demo_user",
  "password": "password123"
}'

# 6
curl -X PATCH "$API/api/user/current/" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "email": "updated@example.com"
}'

curl "$API/api/user/current/" \
-H "Authorization: Bearer $TOKEN"

# 7
curl -X POST "$API/api/tools/recommend/" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "q": "AI tool for editing youtube videos",
  "top_n": 5
}'


# 8
curl "$API/api/tools/recommend/$RESULT_ID/" \
-H "Authorization: Bearer $TOKEN"


# 9
python websocket_demo.py

# 10
curl -X POST "$API/api/user/token/" \
-H "Content-Type: application/json" \
-d '{
  "username": "admin",
  "password": "adminpassword"
}'

export ADMIN_TOKEN=

# 11
curl "$API/api/user/" \
-H "Authorization: Bearer $ADMIN_TOKEN"

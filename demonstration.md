# Script
export API=http://localhost:8000

## 1 - GET Tools Pagination
curl "$API/api/tools/?page=1&page_size=3" | jq

curl "$API/api/tools/?page=2&page_size=3" | jq

## 2 - Search tools
curl "$API/api/tools/search/?q=video&sort-by=popularity_votes&order=desc&page_size=5" | jq

## 3 - GET domains sub table
curl "$API/api/tools/domains/" | jq

## 4 - Register account - bad password, and correct password
curl -X POST "$API/api/user/register/" \
-H "Content-Type: application/json" \
-d '{
  "username": "demo",
  "email": "demo@example.com",
  "password": "password123"
}'  | jq

curl -X POST "$API/api/user/register/" \
-H "Content-Type: application/json" \
-d '{
  "username": "demo",
  "email": "demo@example.com",
  "password": "Something_123",
  "interested_domain": "Audio",
  "email_alerts": true
}'  | jq

## 5 - Login
curl -X POST "$API/api/user/token/" -H "Content-Type: application/json" \
-d '{
  "username": "demo",
  "password": "Something_123"
}' | jq

export TOKEN=

## 6 - Current User
curl "$API/api/user/current/" -H "Authorization: Bearer $TOKEN"  | jq

## 7 - Update email
curl -X PATCH "$API/api/user/current/" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "email": "sc23cg@leeds.ac.uk"
}' | jq

curl "$API/api/user/current/" \
-H "Authorization: Bearer $TOKEN" | jq

## 8 - HTTP recommendations
curl -X POST "$API/api/tools/recommend/" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "q": "AI tool for editing youtube videos",
  "top_n": 5
}' | jq

## 9 - Get results
curl "$API/api/tools/recommend/1/" \
-H "Authorization: Bearer $TOKEN" | jq

## 10 - Websocket recommendations
python websocket_demo.py

## 11 - Superuser login
curl -X POST "$API/api/user/token/" \
-H "Content-Type: application/json" \
-d '{
  "username": "superuser",
  "password": "superuser"
}' | jq

export ADMIN_TOKEN=

## 12 - Email Test
curl -X PATCH "$API/api/tools/1000/" \
-H "Authorization: Bearer $ADMIN_TOKEN" \
-H "Content-Type: application/json" \
-d '{
  "primary_domain": "Audio"
}' | jq

## 13 - Get ALL users - shows permissions
curl "$API/api/user/" | jq

curl "$API/api/user/" \
-H "Authorization: Bearer $ADMIN_TOKEN" | jq

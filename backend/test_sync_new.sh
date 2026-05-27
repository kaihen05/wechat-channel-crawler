#!/bin/bash
TOKEN=$(curl -s http://localhost:8000/api/auth/login -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"admin2026"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['token'])")
echo "Token: $TOKEN"
curl -s http://localhost:8000/api/articles/sync -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{}'
echo ""
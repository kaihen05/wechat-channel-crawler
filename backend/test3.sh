#!/bin/bash
RESP=$(curl -s http://localhost:8000/api/auth/login -X POST -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin2026\"}")
echo "Login: $RESP"
TOKEN=$(echo $RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
echo "Token: $TOKEN"
curl -s http://localhost:8000/api/articles/sync -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d "{}"
echo ""
#!/bin/bash
curl -s http://localhost:8000/api/auth/login -X POST -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin2026\"}"
echo ""
curl -s http://localhost:8000/api/articles/sync -X POST -H "Content-Type: application/json" -d "{}"
echo ""
#!/bin/bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdXRoZW50aWNhdGVkIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzc5ODQ5NDUxfQ.tVQgTW4M_f3TIe45ea45ISH5NhtgvWroMbN99SMPGOA"
curl -s http://localhost:8000/api/articles/sync -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
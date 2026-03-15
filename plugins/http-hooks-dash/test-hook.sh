#!/bin/bash
curl -X POST http://localhost:3001/hooks \
  -H "Content-Type: application/json" \
  -d '{"type":"tool_call","tool_name":"Read","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","payload":{"file_path":"/example/test.js"}}'
echo ""
echo "Event sent! Check the dashboard at http://localhost:3001"

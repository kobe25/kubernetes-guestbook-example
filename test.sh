#!/bin/bash

echo 'Status of the app: '
curl -s -o /dev/null -w "%{http_code}" 'http://localhost:8080/healthz'
echo

curl -X POST 'http://localhost:8080/api/data/messages/READY'
echo
curl         'http://localhost:8080/api/data/messages'
echo
curl -X POST 'http://localhost:8080/api/data/messages/a,b'
echo
curl         'http://localhost:8080/api/data/messages'
echo

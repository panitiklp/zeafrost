# ShotGrid Module Summary

This module provides a task search functionality by user. 

## Endpoint
The endpoint for this functionality is:
```
http://pip-oceanus/zeafrost/api/v1/task/search-by-user
```

## Request
The request should be a POST request with the following headers and body:

Headers:
```json
{
    "Content-Type": "application/json",
    "Accept": "application/json"
}
```

Body:
```json
{
    "user": "<username>"
}
```
Replace `<username>` with the username you want to search tasks for.

## Response
The response will be a JSON object with the following structure:

```json
{
    "code": 200,
    "data": [...], // Array of tasks
    "entity": "task",
    "message": "OK",
    "payload": {...}, // Additional data
    "timestamp": "<timestamp>"
}
```
The `timestamp` field will contain the time when the response was generated.
# Testing
1. ## Registering with missing data: `http://127.0.0.1:5000/register/`
- *Request body*
```
{
    "username": "newtestdev",
    "field": "developer"
}
```
- *Response body*
```
{
    "message": {
        "email": "Info required but missing",
        "password": "Info required but missing"
    },
    "status": "error"
}
```

2. Getting user without login: `http://127.0.0.1:5000/api/users/newtestdev`
- *Response body*
```
{
    "message": "No API Authentication Token",
    "status": "error"
}
```

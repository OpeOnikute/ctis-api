from jsonschema import Draft4Validator

register_user_schema = Draft4Validator(
    schema={
        "title": "Register User",
        "type": "object",
        "properties": {
            "firstName": {
                "type": "string"
            },
            "lastName": {
                "type": "string"
            },
            "email": {
                "description": "email address",
                "type": "string"
            },
            "accountType": {
                "description": "Account type",
                "type": "string",
                "enum": ['driver', 'user', 'admin']
            },
            "password": {
                "type": "string"
            },
        },
        "required": ["firstName", "lastName", "password", "email", "accountType"]
    }
)

login_schema = Draft4Validator(
    schema={
        "title": "Login User",
        "type": "object",
        "properties": {
            "email": {
                "description": "email address",
                "type": "string"
            },
            "password": {
                "type": "string"
            },
        },
        "required": ["password", "email"]
    }
)

confirm_registration_schema = Draft4Validator(
    schema={
        "title": "Confirm Registration",
        "type": "object",
        "properties": {
            "registrationCode": {
                "type": "integer",
            },
        },
        "required": ["registrationCode"]
    }
)

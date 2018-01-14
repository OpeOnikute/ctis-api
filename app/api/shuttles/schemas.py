from jsonschema import Draft4Validator

create_shuttle_schema = Draft4Validator(
    schema={
        "title": "Create Shuttle",
        "type": "object",
        "properties": {
            "brand": {
                "type": "string"
            },
            "ac": {
                "description": "Whether the shuttle has an air conditioner or not",
                "type": "boolean"
            },
            "size": {
                "type": "string",
                "enum": ['small', 'medium', 'full']
            }
        },
        "required": ["brand", "ac", "size"]
    }
)

add_location_schema = Draft4Validator(
    schema={
        "title": "Add Location",
        "type": "object",
        "properties": {
            "name": {
                "type": "string"
            },
            "description": {
                "type": "string"
            },
            "type": {
                "type": "string",
                "enum": ['building', 'bus_stop']
            },
            "latitude": {
                "type": "number"
            },
            "longitude": {
                "type": "number"
            },
            "directions": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "number"
                    },
                    "driving": {
                        "type": "string"
                    },
                    "walking": {
                        "type": "string"
                    },
                    "transit": {
                        "type": "string"
                    }
                },
                "required": ["location_id", "driving", "walking", "transit"]
            },
        },
        "required": ["name", "type", "latitude", "longitude"]
    }
)

update_location_schema = Draft4Validator(
    schema={
        "title": "Update Location",
        "type": "object",
        "properties": {
            "directions": {
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "number"
                    },
                    "driving": {
                        "type": "string"
                    },
                    "walking": {
                        "type": "string"
                    },
                    "transit": {
                        "type": "string"
                    }
                },
                "required": ["location_id", "driving", "walking", "transit"]
            },
        }
    }
)

switch_shuttle_mode_schema = Draft4Validator(
    schema={
        "title": "Switch Shuttle Mode",
        "type": "object",
        "properties": {
            "location": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number"
                    },
                    "longitude": {
                        "type": "number"
                    }
                },
                "required": ["latitude", "longitude"]
            },
        },
        "required": ["location"]
    }
)

update_shuttle_location_schema = Draft4Validator(
    schema={
        "title": "Update shuttle location",
        "type": "object",
        "properties": {
            "lat": {
                "type": "number"
            },
            "lng": {
                "type": "number"
            }
        },
        "required": ["latitude", "longitude"]
    }
)

add_directions_schema = Draft4Validator(
    schema={
        "title": "Add directions to a location",
        "type": "object",
        "properties": {
            "driving": {
                "type": "string"
            },
            "walking": {
                "type": "string"
            },
            "transit": {
                "type": "string"
            }
        },
        "required": ["driving", "walking", "transit"]
    }
)

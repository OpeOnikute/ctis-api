URLS = {
    'users': {
        'token': '/token',
        'get': '/<user_id>',
        'get_all': '/',
        'register': '/register',
        'confirm': '/<username>/confirm',
        'get_drivers': '/drivers',
        'update': '/<user_id>',
        'login': '/login'
    },
    'drivers': {
        'get': '/'
    },
    'shuttles': {
        'create': '/<user_id>',
        'get': '/<shuttle_id>',
        'get_all': '/',
        'update': '/<shuttle_id>',
        'switch_mode': '/<shuttle_id>/mode/<driver_id>',
        'update_location': '/<shuttle_id>/location/<driver_id>',
        'get_distance_matrix': '/distance-matrix'
    },
    'locations': {
        'create': '/',
        'get': '/<location_id>',
        'get_all': '/',
        'update': '/<location_id>'
    }
}

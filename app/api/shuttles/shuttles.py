import googlemaps
from googlemaps.distance_matrix import distance_matrix
from googlemaps.directions import directions

from flask import (Blueprint,
                   jsonify,
                   request,
                   make_response,
                   url_for,
                   current_app as app)

from sqlalchemy.exc import SQLAlchemyError

from app import auth, db
from app.lib.validation import validate_schema
from app.lib.helpers import convert_to_snake_case
from app.models.shuttles import Shuttle, StatusEnum, Location, Directions
from app.models.users import User, AccountTypeEnum

from app.api.shuttles.schemas import (
    create_shuttle_schema,
    add_location_schema,
    switch_shuttle_mode_schema,
    update_shuttle_location_schema,
    add_directions_schema,
    update_location_schema
)

from app.api.urls import URLS

shuttles = Blueprint('shuttles', __name__, url_prefix='/shuttles')
locations = Blueprint('locations', __name__, url_prefix='/locations')
urls = URLS['shuttles']
location_urls = URLS['locations']


# with app.app_context():
#     @app.errorhandler(404)
#     def not_found(error):
#         return make_response(jsonify({'status': 'error', 'message': 'Sorry, we could not find this endpoint.', 'data': error}))


@shuttles.route(urls['create'], methods=['POST'])
@validate_schema(create_shuttle_schema)
def create_shuttle(user_id):

    user = User.get_user(user_id)

    if user is None:
        return jsonify({'code': 400, 'status': 'error', 'message': 'We could not find this user.'})

    brand = request.json.get('brand')
    size = request.json.get('size')
    ac = request.json.get('ac')
    no_of_seats = request.json.get('no_of_seats')

    shuttle = Shuttle(user_id, size, brand, ac, no_of_seats)

    try:
        db.session.add(shuttle)
        db.session.commit()
    except SQLAlchemyError as ex:
        unknown_error = "Could not add shuttle {0}: {1}".format(brand, ex)
        app.logger.error(unknown_error)
        return jsonify({'status': 'error', 'message': unknown_error, 'code': 500})

    return_obj = shuttle.serialize
    return_obj['uri'] = url_for('shuttles.get_shuttle',
                                shuttle_id=shuttle.id,
                                _external=True)

    return jsonify({'status': 'success', 'data': return_obj})


@shuttles.route(urls['get'], methods=['GET'])
def get_shuttle(shuttle_id):
    shuttle = db.session.query(Shuttle).filter_by(id=int(shuttle_id)).first()

    if shuttle is None:
        message = 'Shuttle {0} not found.'.format(shuttle_id)
        app.logger.info(message)
        return jsonify({'status': 'error', 'message': message, 'code': 400})

    return jsonify(shuttle.serialize)


@shuttles.route(urls['update'], methods=['PUT'])
def update_shuttle(shuttle_id):

    payload = request.json

    shuttle = db.session.query(Shuttle).filter_by(id=shuttle_id).first()

    if shuttle is None:
        message = 'We could not find this shuttle.'
        app.logger.info(message)
        return jsonify({'status': 'error', 'message': message, 'code': 400})

    try:
        update_entry(payload, shuttle, ['created'])

    except SQLAlchemyError as ex:
        unknown_error = "Could not update shuttle {0}: {1}".format(shuttle.brand, ex)
        app.logger.error(unknown_error)
        return jsonify({'status': 'error', 'message': unknown_error, 'code': 500})

    return jsonify({"status": 'success', 'data': shuttle.serialize})


@shuttles.route(urls['get_all'], methods=['GET'])
def get_all_shuttles():

    status_query = request.args.get('status') or StatusEnum.enabled
    en_route = request.args.get('en_route')
    user_id = request.args.get('user_id')
    user_location = request.args.get('user_location')

    query_args = {
        'status': status_query
    }

    bool_converter = {
        'true': True,
        'false': False
    }

    if en_route is not None and (en_route in bool_converter.keys()):
        query_args['en_route'] = bool_converter[en_route]

    if user_id is not None:
        query_args['user_id'] = user_id

    shuttles = db.session.query(Shuttle).filter_by(**query_args).all()

    if len(shuttles) <= 0:
        return jsonify({'code': 500, 'status': 'error', 'message': 'No shuttles were found.'})

    serialized = [shuttle.serialize for shuttle in shuttles]

    # get the distances of all the shuttles and determine the closest one (if the user's location is provided
    if user_location is not None:

        shuttle_locations = ["{0}, {1}".format(shuttle["latitude"], shuttle["longitude"]) for shuttle in serialized]

        try:
            gmaps = googlemaps.Client(key=app.config['GMAPS_KEY'])

            distance_response = distance_matrix(gmaps, shuttle_locations, [user_location])
            distance_result = distance_response['rows']

            # attach the shuttles' individual distance matrices
            for shuttle in serialized:
                # get the corresponding result in the distance results array. This is assuming that the responses are
                # in the order they are pushed
                index = serialized.index(shuttle)
                shuttle_result = distance_result[index]

                # The elements attribute is an array for some reason
                shuttle['distance_matrix'] = shuttle_result["elements"][0]

        except Exception as ex:
            message = 'Could not get distance matrix: {0}'.format(ex)
            app.logger.error(message)

    return jsonify({'status': 'success', 'data': serialized})


@locations.route(location_urls['create'], methods=['POST'])
@validate_schema(add_location_schema)
def add_location():

    name = request.json.get('name')
    location_type = request.json.get('type')
    description = request.json.get('description')
    latitude = request.json.get('latitude')
    longitude = request.json.get('longitude')
    directions = request.json.get('directions')

    # Ensure the location doesnt already exist.
    location = db.session.query(Location).filter_by(name=name).first()

    if location is not None:
        message = 'The location \'{0}\' already exists.'.format(name)
        app.logger.info(message)
        return jsonify({'status': 'error', 'message': message, 'code': 400})

    location = Location(name, location_type, description, latitude, longitude)

    try:
        db.session.add(location)
        db.session.commit()

        if directions is not None:
            directions_obj = Directions(location.id, directions["driving"], directions['walking'], directions['transit'])
            db.session.add(directions_obj)

        db.session.commit()

    except SQLAlchemyError as ex:
        unknown_error = "Could not add location {0}: {1}".format(name, ex)
        app.logger.error(unknown_error)
        return jsonify({'status': 'error', 'message': unknown_error, 'code': 500})

    return_obj = location.serialize
    return_obj['uri'] = url_for('locations.get_location',
                                location_id=location.id,
                                _external=True)

    return jsonify(return_obj)


@locations.route(location_urls['get'], methods=['GET'])
def get_location(location_id):

    location = db.session.query(Location).filter_by(id=int(location_id)).first()

    if location is None:
        message = 'Location {0} not found.'.format(location_id)
        app.logger.info(message)
        return jsonify({'status': 'error', 'message': message, 'code': 400})

    return jsonify(location.serialize)


@locations.route(location_urls['add_directions'], methods=['POST'])
@validate_schema(add_directions_schema)
def add_directions_to_location(location_id):

    payload = request.json

    location = db.session.query(Location).filter_by(id=int(location_id)).first()

    if location is None:
        message = 'Location {0} not found.'.format(location_id)
        app.logger.info(message)
        return jsonify({'status': 'error', 'message': message, 'code': 400})

    existing_directions = db.session.query(Directions).filter_by(location_id=int(location_id)).first()

    if existing_directions is not None:
        message = 'Sorry, directions already exist for this location: {0}.'.format(location.name)
        app.logger.info(message)
        return jsonify({'status': 'error', 'message': message, 'code': 400})

    directions_obj = Directions(location.id, payload['driving'], payload['walking'], payload['transit'])

    try:
        db.session.add(directions_obj)
        db.session.commit()

    except SQLAlchemyError as ex:
        unknown_error = "Could not add directions to {0}: {1}".format(location.name, ex)
        app.logger.error(unknown_error)
        return jsonify({'status': 'error', 'message': unknown_error, 'code': 500})

    return jsonify(location.serialize)


@locations.route(location_urls['get_all'], methods=['GET'])
def get_all_locations():

    status_query = request.args.get('status') or StatusEnum.enabled
    location_type = request.args.get('type')
    origin = request.args.get('origin')

    query_args = {
        'status': status_query
    }

    if location_type is not None:
        query_args['type'] = location_type

    locations_obj = db.session.query(Location).filter_by(**query_args).all()

    serialized = [location.serialize for location in locations_obj]

    if len(locations_obj) <= 0:
        return jsonify({'code': 500, 'status': 'error', 'message': 'No locations were found.'})

    # get the distances of all the shuttles and determine the closest one (if the user's location is provided
    if origin is not None:

        try:
            gmaps = googlemaps.Client(key=app.config['DIRECTIONS_KEY'])

            # TODO: Figure out how to avoid the multiple loops
            for location in serialized:
                location_str = "{0},{1}".format(location["latitude"], location["longitude"])
                location['directions'] = dict()

                for travel_mode in ['driving', 'walking', 'transit']:

                    location['directions'][travel_mode] = dict()
                    location['directions'][travel_mode]['routes'] = []

                    direction_response = directions(gmaps, origin, location_str, travel_mode)

                    for result in direction_response:

                        steps = result['legs'][0]['steps'][:2]

                        for step in steps:
                            direction_result = {
                                "html_instructions": step['html_instructions'],
                                "duration": step["duration"],
                                "distance": step["distance"],
                                "travel_mode": step['travel_mode']
                            }

                            location['directions'][travel_mode]['routes'].append(direction_result)

        except Exception as ex:
            message = 'Could not get directions: {0}'.format(ex)
            app.logger.error(message)

    return jsonify({'status': 'success', 'data': serialized})


@locations.route(location_urls['update'], methods=['PUT'])
@validate_schema(update_location_schema)
def update_location(location_id):

    payload = request.json

    location = db.session.query(Location).filter_by(id=location_id).first()

    if location is None:
        message = 'Location {0} not found.'.format(location_id)
        app.logger.info(message)
        return jsonify({'status': 'error', 'message': message, 'code': 400})

    try:
        update_entry(payload, location)

        if payload['directions']:
            print 'here'
            if int(payload['directions']['location_id']) != int(location_id):
                err_message = 'Tried to update directions for the wrong location: Location id - {0}, ' \
                              'Direction id - {1}.'.format(location_id, payload['directions']['location_id'])
                app.logger.info(err_message)

            else:
                location_directions = db.session.query(Directions).filter_by(location_id=location_id).first()
                if location_directions is None:
                    err_message = 'Location "{0}" has no directions to update.'.format(location.name)
                    app.logger.info(err_message)
                else:
                    update_entry(payload['directions'], location_directions)

    except SQLAlchemyError as ex:
        unknown_error = "Could not update location {0}: {1}".format(location.name, ex)
        app.logger.error(unknown_error)
        return jsonify({'status': 'error', 'message': unknown_error, 'code': 500})

    return jsonify({"status": 'success', 'data': location.serialize})


@shuttles.route(urls['switch_mode'], methods=['PUT'])
@validate_schema(switch_shuttle_mode_schema)
def switch_driver_mode(shuttle_id, driver_id):

    driver = User.get_user(driver_id)

    if driver is None:
        return jsonify({'code': 400, 'status': 'error', 'message': 'We could not find this driver.'})

    if driver.account_type is not AccountTypeEnum.driver:
        return jsonify({'code': 400, 'status': 'error', 'message': 'This user is not a driver.'})

    shuttle = Shuttle.get_shuttle_by_id(shuttle_id)

    if shuttle is None:
        return jsonify({'code': 400, 'status': 'error', 'message': 'We could not find this shuttle.'})

    if shuttle.user_id != driver.user_id:
        return jsonify({'code': 400, 'status': 'error', 'message': 'This shuttle is not driven by this driver.'})

    current_location = request.json.get('location')

    current_mode = shuttle.en_route

    shuttle.en_route = True if current_mode is False else False

    shuttle.latitude = current_location['latitude']
    shuttle.longitude = current_location['longitude']

    try:
        db.session.commit()
    except SQLAlchemyError as ex:
        unknown_error = "Could not switch shuttle\'s mode: {0}".format(ex)
        app.logger.error(unknown_error)
        return jsonify({'status': 'error', 'message': unknown_error, 'code': 500})

    return jsonify({"status": 'success', 'data': shuttle.serialize})


@shuttles.route(urls['update_location'], methods=['PUT'])
@validate_schema(update_shuttle_location_schema)
def update_shuttle_location(shuttle_id, driver_id):

    driver = User.get_user(driver_id)

    if driver is None:
        return jsonify({'code': 400, 'status': 'error', 'message': 'We could not find this driver.'})

    if driver.account_type is not AccountTypeEnum.driver:
        return jsonify({'code': 400, 'status': 'error', 'message': 'This user is not a driver.'})

    shuttle = Shuttle.get_shuttle_by_id(shuttle_id)

    if shuttle is None:
        return jsonify({'code': 400, 'status': 'error', 'message': 'We could not find this shuttle.'})

    if shuttle.user_id != driver.user_id:
        return jsonify({'code': 400, 'status': 'error', 'message': 'This shuttle is not driven by this driver.'})

    shuttle.longitude = request.json.get('lng')
    shuttle.latitude = request.json.get('lat')

    try:
        db.session.commit()
    except SQLAlchemyError as ex:
        unknown_error = "Could not switch shuttle\'s mode: {0}".format(ex)
        app.logger.error(unknown_error)
        return jsonify({'status': 'error', 'message': unknown_error, 'code': 500})

    return jsonify({"status": 'success', 'data': shuttle.serialize})


@shuttles.route(urls['get_distance_matrix'], methods=['GET'])
def get_distance_matrix():

    origin = request.args.get('origin')
    destination = request.args.get('destination')

    if (origin is None) or (destination is None):
        return jsonify({'status': 'error', 'message': 'Please enter both an origin and a destination in the query.'})

    if (origin == '') or (destination == ''):
        return jsonify({'status': 'error', 'message': 'The origin and destination queries cannot be empty.'})

    try:
        gmaps = googlemaps.Client(key=app.config['GMAPS_KEY'])

        result = distance_matrix(gmaps, [origin], [destination])

    except Exception as ex:
        return jsonify({'status': 'error', 'message': 'Could not get distance: \'{0}\''.format(ex)})

    return jsonify({'status': 'success', 'data': result})


@shuttles.route(urls['get_directions'], methods=['GET'])
def get_directions():

    mode = request.args.get('mode')
    origin = request.args.get('origin')
    destination = request.args.get('destination')

    if (origin is None) or (destination is None):
        return jsonify({'status': 'error', 'message': 'Please enter both an origin and a destination in the query.'})

    if (origin == '') or (destination == ''):
        return jsonify({'status': 'error', 'message': 'The origin and destination queries cannot be empty.'})

    try:
        gmaps = googlemaps.Client(key=app.config['GMAPS_KEY'])

        result = directions(gmaps, [origin], [destination], mode)

    except Exception as ex:
        return jsonify({'status': 'error', 'message': 'Could not get directions: \'{0}\''.format(ex)})

    return jsonify({'status': 'success', 'data': result})


def update_entry(payload, entry_object, skip_values=None):
    """
    :param payload:
    :param entry_object:
    :param skip_values:
    :type skip_values: list
    :return: boolean
    """

    skip_values = skip_values or []

    if 'created' not in skip_values:
        skip_values.append('created')

    if 'updated' not in skip_values:
        skip_values.append('updated')

    for obj in payload:

        converted_prop = convert_to_snake_case(obj)

        if converted_prop in skip_values:
            continue

        if not hasattr(entry_object, converted_prop):
            continue
        setattr(entry_object, converted_prop, payload[obj])

    db.session.commit()

    return True

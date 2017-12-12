from time import sleep

from flask import (abort,
                   Blueprint,
                   g,
                   jsonify,
                   request,
                   url_for,
                   current_app as app)
from requests import HTTPError
from sqlalchemy.exc import SQLAlchemyError

from app import auth, cache, db
from app.api.urls import URLS
from app.api.shuttles.shuttles import update_entry
from app.api.users.schemas import (
    confirm_registration_schema,
    register_user_schema,
    login_schema
)

from app.lib.email import send_email
from app.lib.validation import validate_schema
from app.models.users import User, AccountTypeEnum, StatusEnum as UserStatusEnum, verify_password


users = Blueprint('users', __name__, url_prefix='/users')
drivers = Blueprint('drivers', __name__, url_prefix='/drivers')
urls = URLS['users']
driver_urls = URLS['drivers']


@users.route(urls['token'], methods=['GET'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()

    return jsonify({'token': token.decode('ascii')})


@users.route(urls['get'], methods=['GET'])
@auth.login_required
def get_user(user_id):
    user = db.session.query(User).filter_by(user_id=int(user_id)).first()

    if user is None:
        message = 'User {0} not found.'.format(user_id)
        app.logger.info(message)
        return jsonify({'status': 'error', 'message': message, 'code': 400})

    return jsonify(user.serialize)


@users.route(urls['register'], methods=["POST"])
@validate_schema(register_user_schema)
def register_user():
    sleep(1)  # try to avoid email enumeration attacks
    first_name = request.json.get('firstName')
    last_name = request.json.get('lastName')
    password = request.json.get('password')
    email = request.json.get('email')
    account_type = request.json.get('accountType')

    if db.session.query(User).filter_by(email=email).first() is not None:
        email_exists = 'Email {0} already exists.'.format(email)
        app.logger.info(email_exists)
        return jsonify({'status': 'error', 'message': email_exists, 'code': 409})

    user = User(first_name, last_name, password, email, account_type)
    try:
        db.session.add(user)
        db.session.commit()
        app.logger.info("User {0} commited to DB.".format(first_name))
    except SQLAlchemyError as ex:
        unknown_error = "Could not add user {0}: {1}".format(first_name, ex)
        app.logger.error(unknown_error)
        return jsonify({'status': 'error', 'message': unknown_error, 'code': 500})

    # send confirmation email
    # try:
    #     resp = send_email(
    #         to=user.email,
    #         subject='Thank you for registering!',
    #         body='Registration code: {registration_code}'.format(
    #             registration_code=user.registration_code)
    #     )
    #     resp.raise_for_status()
    # except HTTPError as ex:
    #     message = 'Failed to email registration code to '
    #     '{email}: {ex}'.format(email=user.email, ex=ex)
    #     app.logger.error(message)
    #     error_resp = jsonify({
    #         'errorMsg': message.split(':')[0],
    #     })
    #     error_resp.status_code = 500
    #
    #     return error_resp

    return_obj = user.serialize
    return_obj['uri'] = url_for('users.get_user',
                                user_id=user.user_id,
                                _external=True)

    return jsonify(return_obj)


@users.route(urls['login'], methods=["POST"])
@validate_schema(login_schema)
def login():

    email = request.json.get('email')
    password = request.json.get('password')

    user = db.session.query(User).filter_by(email=email).first()

    if user is None:
        message = 'We could not find this user.'
        app.logger.info(message)
        return jsonify({'status': 'error', 'message': message, 'code': 400})

    password_valid = verify_password(user.user_id, password)

    if not password_valid:
        return jsonify({'status': 'error', 'message': 'The login details you provided seem to be incorrect. Please try again.', 'code': 400})

    token = g.user.generate_auth_token()

    return jsonify({'status': 'success', 'data': {'user': user.serialize, 'token': token.decode('ascii')}})


@drivers.route(driver_urls['get'], methods=['GET'])
def get_all_drivers():

    drivers = db.session.query(User).filter_by(account_type=AccountTypeEnum.driver).all()

    if len(drivers) <= 0:
        return jsonify({'code': 500, 'status': 'error', 'message': 'No drivers were found.'})

    return jsonify({'status': 'success', 'data': [driver.serialize for driver in drivers]})


@users.route(urls['get_all'], methods=['GET'])
def get_all_users():

    status_query = request.args.get('status')
    account_type_query = request.args.get('account_type')

    query_args = {}

    if status_query is not None:
        query_args['status'] = status_query

    if account_type_query is not None:
        query_args['account_type'] = account_type_query

    users = db.session.query(User).filter_by(**query_args).all()

    if len(users) <= 0:
        return jsonify({'code': 500, 'status': 'error', 'message': 'No users were found.'})

    return jsonify({'status': 'success', 'data': [user.serialize for user in users]})


@users.route(urls['update'], methods=['PUT'])
def update_user(user_id):

    payload = request.json

    user = db.session.query(User).filter_by(user_id=user_id).first()

    if user is None:
        message = 'We could not find this user.'
        app.logger.info(message)
        return jsonify({'status': 'error', 'message': message, 'code': 400})

    try:
        update_entry(payload, user)

    except SQLAlchemyError as ex:
        unknown_error = "Could not update user {0}: {1}".format(user.first_name, ex)
        app.logger.error(unknown_error)
        return jsonify({'status': 'error', 'message': unknown_error, 'code': 500})

    return jsonify({"status": 'success', 'data': user.serialize})


@users.route(urls['confirm'], methods=['POST'])
@auth.login_required
@validate_schema(confirm_registration_schema)
def confirm_registration(username):
    user = User.query.filter_by(username=username).first()
    secret_code = request.json.get('registrationCode')

    if user is None:
        abort(400)

    if int(secret_code) == int(user.registration_code):
        try:
            user.registration_confirmed = True
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError as ex:
            app.logger.info(
                'Could not commit user to database: {0}'.format(ex)
            )
            abort(500)

        return jsonify(user.serialize)
    else:
        app.logger.info(
            'User {0}: Secret code did not match.'.format(user.username)
        )
        abort(400)


@users.route('/this_is_cached', methods=['GET'])
@cache.cached(timeout=300)
def example_cached_handler():
    from datetime import datetime
    return jsonify({
        'time': datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    })

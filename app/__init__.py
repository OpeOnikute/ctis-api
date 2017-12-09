from flask import Flask
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from lib.cache import build_cache_from_config


db = SQLAlchemy()
auth = HTTPBasicAuth()


def init_app(testing=False):
    app = Flask(__name__)
    CORS(app)
    if testing:
        app.config.from_pyfile('../settings/test.cfg')
    else:
        app.config.from_pyfile('../settings/default.cfg')
        # $ export APP_CONFIG = ../settings/local.cfg
        app.config.from_envvar('APP_CONFIG', silent=True)

    app.debug = True

    if app.debug:
        from werkzeug.debug import DebuggedApplication
        app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

    global cache
    cache = build_cache_from_config(app)
    cache.init_app(app)

    db.init_app(app)

    # blueprints
    from app.api.users.users import users, drivers
    from app.api.shuttles.shuttles import shuttles, locations

    app.register_blueprint(users)
    app.register_blueprint(drivers)
    app.register_blueprint(shuttles)
    app.register_blueprint(locations)

    # with contextlib.closing(engine.connect()) as con:
    #     trans = con.begin()
    #     for table in reversed(meta.sorted_tables):
    #         con.execute(table.delete())
    #     trans.commit()

    return app

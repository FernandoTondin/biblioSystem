import os

from flask import Flask, render_template

from biblio.credentials import database_acces


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'biblio.sqlite'),
    )

    app.config['MYSQL_HOST'] = database_acces().get_host()
    app.config['MYSQL_USER'] = database_acces().get_user()
    app.config['MYSQL_PASSWORD'] = database_acces().get_password()
    app.config['MYSQL_DB'] = database_acces().get_database()

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def home():
        return render_template('index.html')

    from . import db
    db.init_app(app)

    from . import info
    app.register_blueprint(info.bp)

    from . import cadastro
    app.register_blueprint(cadastro.bp)

    from . import view
    app.register_blueprint(view.bp)

    return app


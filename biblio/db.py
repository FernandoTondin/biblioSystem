import sqlite3
import mysql.connector

import click
from flask import current_app, g, session
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:

        mydb = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD']
        )
        
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute("SHOW DATABASES")

        if 'admin' in session:
            if session.get('admin'):
                db = current_app.config['MYSQL_DB']
            else:
                db = current_app.config['MYSQL_DB']
        else:
            db = current_app.config['MYSQL_DB']


        for x in mycursor:
            if x == (db,):
                mycursor.close()
                g.db = mysql.connector.connect(
                    host=current_app.config['MYSQL_HOST'],
                    user=current_app.config['MYSQL_USER'],
                    password=current_app.config['MYSQL_PASSWORD'],
                    database=db
                )
                return g.db
        mycursor.execute("CREATE DATABASE "+db)
        mycursor.close()
        g.db = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=db
        )
        return g.db

        #g.db = sqlite3.connect(
        #    current_app.config['DATABASE'],
        #    detect_types=sqlite3.PARSE_DECLTYPES
        #)
        #g.db.row_factory = sqlite3.Row

    return g.db

def get_cursor():
    return get_db().cursor(dictionary=True)


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.cursor().execute(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


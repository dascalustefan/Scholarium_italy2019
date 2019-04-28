from app import app
import secrets
import MySQLdb
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

"""

This module contains the configurations of the flask application.

"""

# the secret key - used by the browser to keep track of the sessions
app.secret_key = secrets.token_bytes(32)
# the database configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/scholarium_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=80)

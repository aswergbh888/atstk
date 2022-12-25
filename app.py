from flask import *
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from flask.logging import default_handler

db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db.init_app(app)

gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)
app.logger.removeHandler(default_handler)
app.logger.info('Starting the Flask User Management App...')


@app.route('/')
def index():
    app.logger.info(f"DATABASE_URL environment variable: {os.getenv('DATABASE_URL')}")
    return 'atstk'


if __name__ == '__main__':
    app.run(debug=True)


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


@app.route('/api/c', methods=['POST'])
def create_order():
    content = request.get_json(silent=True)
    current_app.logger.info(f'content: {content}')
    message = content['m']
    current_app.logger.info(f'message: {message}')
    message_split = message.split('|')

    # Valid input
    if len(message_split) != 6:
        return f'Bad request!', 400
    # 2|2723|1|Sell|Fix|120.0
    order_id = int(message_split[0])
    stock_id = message_split[1]
    lot_num = 1  # int(message_split[2])
    order_type = message_split[3]
    price_type = message_split[4]
    price = float(message_split[5])
    current_app.logger.info(f'order_id: {order_id}, stock_id: {stock_id}, lot_num: {lot_num}, order_type: {order_type}, price_type: {price_type}, price: {price}')
    if len(stock_id) != 4 or order_type not in ['Buy', 'Sell'] or price_type not in ['Fix', 'Market']:
        return f'Bad request!', 400

    sql_cmd = '''
              INSERT INTO STOCK_ORDER
              VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
              '''
    result = db.engine.execute(sql_cmd, (order_id, stock_id, lot_num, order_type, price_type, price, 'New'))
    return 'OK'


if __name__ == '__main__':
    app.run(debug=True)


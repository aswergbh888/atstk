from flask import *
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from flask.logging import default_handler
import pytz
from datetime import datetime


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
    current_app.logger.info(f"DATABASE_URL environment variable: {os.getenv('DATABASE_URL')}")
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


@app.route('/api/g')
def get_order():
    sql_cmd = '''
              UPDATE HEALTH_CHECK
              SET last_check_time = CURRENT_TIMESTAMP
              WHERE name = %s;
              '''
    result = db.engine.execute(sql_cmd, 'Agent')

    sql_cmd = '''
              SELECT *
              FROM STOCK_ORDER
              WHERE status = 'New'
              ORDER BY create_time
              FETCH FIRST ROW ONLY
              '''

    row = db.engine.execute(sql_cmd).first()
    current_app.logger.info(f'row: {row}')
    if not row:
        return 'Not found!', 404

    order_id = row['id']
    stock_id = row['stock_id']
    lot_num = row['lot_num']
    order_type = row['type']
    price_type = row['price_type']
    price = row['price']
    current_app.logger.info(f'order_id: {order_id}')
    current_app.logger.info(f'stock_id: {stock_id}')
    current_app.logger.info(f'lot_num: {lot_num}')
    current_app.logger.info(f'order_type: {order_type}')
    current_app.logger.info(f'price_type: {price_type}')
    current_app.logger.info(f'price: {price}')

    sql_cmd = '''
              UPDATE STOCK_ORDER
              SET status = 'Accept', update_time = CURRENT_TIMESTAMP
              WHERE id = %s;
              '''
    result = db.engine.execute(sql_cmd, order_id)
    return f'{order_id}|{stock_id}|{lot_num}|{order_type}|{price_type}|{price}'


@app.route('/api/h')
def get_health_check():
    sql_cmd = '''
              SELECT last_check_time
              FROM HEALTH_CHECK
              WHERE name = %s;
              '''
    row = db.engine.execute(sql_cmd, 'Agent').first()
    last_check_time = row['last_check_time']
    tz = pytz.timezone('Asia/Taipei')
    last_check_time = last_check_time.replace(tzinfo=pytz.utc).astimezone(tz)
    return last_check_time.strftime('%Y-%m-%d %H:%M:%S %z')


@app.route('/api/cc', methods=['POST'])
def create_close_order():
    sql_cmd = '''
              UPDATE CLOSE_ORDER
              SET enable_flag = 1, update_time = CURRENT_TIMESTAMP
              WHERE name = %s;
              '''
    result = db.engine.execute(sql_cmd, 'Agent')
    return 'OK'


@app.route('/api/gc')
def get_close_order():
    # sql_cmd = '''
    #           UPDATE HEALTH_CHECK
    #           SET last_check_time = CURRENT_TIMESTAMP
    #           WHERE name = %s;
    #           '''
    # result = db.engine.execute(sql_cmd, 'Agent')

    sql_cmd = '''
              SELECT *
              FROM CLOSE_ORDER
              WHERE name = %s
              AND enable_flag = 1
              '''

    row = db.engine.execute(sql_cmd, 'Agent').first()
    current_app.logger.info(f'row: {row}')
    if not row:
        return 'Not found!', 404

    sql_cmd = '''
              UPDATE CLOSE_ORDER
              SET enable_flag = 0, update_time = CURRENT_TIMESTAMP
              WHERE name = %s;
              '''
    result = db.engine.execute(sql_cmd, 'Agent')
    return 'OK'


@app.route('/api/cf', methods=['POST'])
def create_order_fail_reason():
    content = request.get_json(silent=True)
    current_app.logger.info(f'content: {content}')
    message = content['m']
    current_app.logger.info(f'message: {message}')

    sql_cmd = '''
              INSERT INTO ORDER_FAIL_REASON
              VALUES (%s, CURRENT_TIMESTAMP)
              '''
    result = db.engine.execute(sql_cmd, message)
    return 'OK'


@app.route('/api/gf')
def get_order_fail_reason():
    result = 'Result:'

    sql_cmd = '''
              SELECT message, update_time
              FROM ORDER_FAIL_REASON
              ORDER BY update_time DESC
              '''

    rows = db.engine.execute(sql_cmd, 'Agent').fetchall()

    for row in rows:
        current_app.logger.info(f'row: {row}')
        message = row['message']
        update_time = row['update_time']

        if update_time.date() == datetime.today().date():
            tz = pytz.timezone('Asia/Taipei')
            update_time = update_time.replace(tzinfo=pytz.utc).astimezone(tz)
            update_time = update_time.strftime('%Y-%m-%d %H:%M:%S %z')
            result = result + '\n' + update_time + ' | ' + message

    return result


if __name__ == '__main__':
    app.run(debug=True)

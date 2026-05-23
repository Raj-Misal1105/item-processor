from flask import Flask, request, jsonify
import pika
import json
from app.database import get_connection, init_db
from app.config.settings import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USERNAME,
    RABBITMQ_PASSWORD,
    RABBITMQ_VHOST,
    QUEUE_NAME,
    EXCHANGE_NAME,
    ROUTING_KEY
)
import uuid

app = Flask(__name__)

def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    return connection

def publish_to_rabbitmq(message: dict, item_id: int, item_name: str):
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type='direct',
        durable=True
    )

    channel.queue_declare(
    queue=QUEUE_NAME,
    durable=True,
    arguments={'x-queue-type': 'quorum'} 
)


    channel.queue_bind(
        queue=QUEUE_NAME,
        exchange=EXCHANGE_NAME,
        routing_key=ROUTING_KEY
    )

    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=ROUTING_KEY,
        body=json.dumps([[item_id, item_name], {}, {}]),  
        properties=pika.BasicProperties(
            delivery_mode=2,
            content_type='application/json',
            headers={
                'id': str(uuid.uuid4()),
                'task': 'process_item',
                'argsrepr': f'({item_id}, "{item_name}")',
                'lang': 'py',
                'retries': 0,
            }
        )
    )

    connection.close()
    print(f"Message published to RabbitMQ: {message}")

@app.route('/items', methods=['POST'])
def create_item():

    data = request.get_json()

    if not data or 'item' not in data:
        return jsonify({'error': 'item field is required'}), 400

    item_name = data['item'].strip()

    if not item_name:
        return jsonify({'error': 'item cannot be empty'}), 400

    
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'INSERT INTO items (item, status) VALUES (?, ?)',
        (item_name, 'pending')
    )

    item_id = cursor.lastrowid
    conn.commit()
    conn.close()

    message = {
        'id': item_id,
        'item': item_name
    }
    publish_to_rabbitmq(message, item_id, item_name)

    return jsonify({'message': 'Item accepted', 'id': item_id}), 202
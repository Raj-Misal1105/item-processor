# RabbitMQ Configuration
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USERNAME = 'guest'
RABBITMQ_PASSWORD = 'guest'
RABBITMQ_VHOST = '/'

# Queue Configuration
QUEUE_NAME = 'item_processing_queue'
EXCHANGE_NAME = 'item_exchange'
ROUTING_KEY = 'item_routing_key'

# Celery Configuration
CELERY_BROKER_URL = f'amqp://{RABBITMQ_USERNAME}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{{}}'.format('')

# Database Configuration
DATABASE_NAME = 'items.db'
DATABASE_PATH = 'items.db'
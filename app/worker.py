from celery import Celery
from kombu import Queue, Exchange
import sqlite3
from app.config.settings import (
    CELERY_BROKER_URL,
    QUEUE_NAME,
    EXCHANGE_NAME,
    ROUTING_KEY,
    DATABASE_PATH
)

celery_app = Celery('worker', broker=CELERY_BROKER_URL)

item_exchange = Exchange(EXCHANGE_NAME, type='direct', durable=True)


celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    task_default_queue=QUEUE_NAME,
    task_default_exchange=EXCHANGE_NAME,
    task_default_routing_key=ROUTING_KEY,
    task_queues=[
        Queue(
            QUEUE_NAME,
            item_exchange,
            routing_key=ROUTING_KEY,
            durable=True,
            queue_arguments={'x-queue-type': 'quorum'}
        )
    ],
    task_always_eager=False,
    worker_direct=False,
    
    worker_hijack_root_logger=False,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    broker_transport_options={
        'confirm_publish': True
    }
)


celery_app.conf.worker_pool = 'solo'

def update_item_status(item_id: int, item_name: str):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute(
        '''UPDATE items 
           SET status = ? 
           WHERE id = ? AND item = ? AND status = ?''',
        ('completed', item_id, item_name, 'pending')
    )

    rows_updated = cursor.rowcount
    conn.commit()
    conn.close()

    if rows_updated > 0:
        print(f"Item id={item_id}, item={item_name} -> status: completed")
    else:
        print(f"Item id={item_id} not found or already completed")

@celery_app.task(name='process_item', queue=QUEUE_NAME)
def process_item(*args, **kwargs):
    # Celery format: args = (item_id, item_name)
    # Raw JSON format: kwargs = {'id': 1, 'item': 'book'}
    
    if args:
        item_id = args[0]
        item_name = args[1]
    else:
        item_id = kwargs.get('id')
        item_name = kwargs.get('item')
    
    print(f"Received: id={item_id}, item={item_name}")
    update_item_status(item_id, item_name)
    return {'status': 'completed', 'id': item_id, 'item': item_name}
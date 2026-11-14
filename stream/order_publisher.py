"""Bonus: publish FreshCart-style order messages to the durable queue `freshcart.orders`.

The five orders are fixed (same ids and same updated_at every time) so that publishing them again
simulates a re-delivered batch: the pipeline must not double the gold totals.
"""
import json
import os

import pika

QUEUE = 'freshcart.orders'

# same shape as the website API (flat JSON) used by the FreshCart notebook
STREAM_ORDERS = [
    {"order_id": "ORD-2001", "cust_email": "priya.r@gmail.com", "cust_name": "Priya R",
     "order_date": "2026-09-03", "amount": "500.00", "currency": "INR", "pincode": "600041",
     "updated_at": "2026-09-03 18:00:00"},
    {"order_id": "ORD-2002", "cust_email": "arjun.k@yahoo.in", "cust_name": "Arjun K",
     "order_date": "2026-09-02", "amount": "20.00", "currency": "USD", "pincode": "560034",
     "updated_at": "2026-09-02 19:10:00"},
    {"order_id": "ORD-2003", "cust_email": "meera@outlook.com", "cust_name": "Meera S",
     "order_date": "2026-09-03", "amount": "3,000.00", "currency": "INR", "pincode": "400050",
     "updated_at": "2026-09-03 20:30:00"},
    {"order_id": "ORD-2004", "cust_email": "priya.r@gmail.com", "cust_name": "Priya R",
     "order_date": "2026-09-02", "amount": "750.00", "currency": "INR", "pincode": "600041",
     "updated_at": "2026-09-02 21:00:00"},
    {"order_id": "ORD-2005", "cust_email": "meera@outlook.com", "cust_name": "Meera S",
     "order_date": "2026-09-01", "amount": "10.00", "currency": "USD", "pincode": "400050",
     "updated_at": "2026-09-01 22:15:00"},
]


def publish_orders(orders=STREAM_ORDERS, url=None):
    url = url or os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/%2F')
    conn = pika.BlockingConnection(pika.URLParameters(url))
    ch = conn.channel()
    ch.queue_declare(queue=QUEUE, durable=True)
    for o in orders:
        ch.basic_publish(exchange='', routing_key=QUEUE, body=json.dumps(o),
                         properties=pika.BasicProperties(delivery_mode=2))
        print('published', o['order_id'])
    conn.close()


if __name__ == '__main__':
    publish_orders()

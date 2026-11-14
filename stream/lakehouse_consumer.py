"""Bonus: collect order messages from RabbitMQ for N seconds and return them as a list.

The FreshCart notebook then calls write_landing() / load_file() / the transform SQL on that list.

    python stream/lakehouse_consumer.py --seconds 60      # just prints what it collected
"""
import argparse
import json
import os
import time

import pika

QUEUE = 'freshcart.orders'


def consume_orders(seconds=60, url=None):
    url = url or os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/%2F')
    conn = pika.BlockingConnection(pika.URLParameters(url))
    ch = conn.channel()
    ch.queue_declare(queue=QUEUE, durable=True)
    orders, last_tag = [], None
    deadline = time.time() + seconds
    while time.time() < deadline:
        method, props, body = ch.basic_get(queue=QUEUE, auto_ack=False)
        if method is None:
            time.sleep(0.5)
            continue
        orders.append(json.loads(body))
        last_tag = method.delivery_tag
    # ACK only after the whole batch is in memory; the caller writes the file next.
    # (If the process crashes before this line the broker re-delivers the messages: at-least-once.)
    if last_tag is not None:
        ch.basic_ack(delivery_tag=last_tag, multiple=True)
    conn.close()
    print(f'collected {len(orders)} order messages in {seconds}s')
    return orders


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=60)
    for o in consume_orders(ap.parse_args().seconds):
        print(o['order_id'], o['amount'], o['currency'])

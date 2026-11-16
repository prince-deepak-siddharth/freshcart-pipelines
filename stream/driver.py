"""Driver: declares a private queue, binds it with PATTERN, prints every request and ACKs it.

    python stream/driver.py NAME PATTERN
    python stream/driver.py Ravi "bangalore.koramangala.*"

* A message WITHOUT a "zone" field is rejected:  basic_nack(requeue=False)  (it is discarded, not retried).
* Every other message is processed and acknowledged:  basic_ack.
"""
import json
import os
import sys

import pika

try:  # optional: read RABBITMQ_URL from a local .env file (see .env.example)
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

EXCHANGE = 'rapido-dispatch'


def main():
    if len(sys.argv) != 3:
        sys.exit('usage: python stream/driver.py NAME PATTERN')
    name, pattern = sys.argv[1], sys.argv[2]

    url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/%2F')
    conn = pika.BlockingConnection(pika.URLParameters(url))
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type='topic', durable=False)

    # private queue: only this driver can use it, and it disappears when the driver disconnects
    queue = f'driver.{name}'
    ch.queue_declare(queue=queue, exclusive=True, auto_delete=True)
    ch.queue_bind(queue=queue, exchange=EXCHANGE, routing_key=pattern)
    ch.basic_qos(prefetch_count=1)          # one unacknowledged message at a time
    print(f'[{name}] queue={queue} bound with pattern "{pattern}". Waiting for requests...', flush=True)

    def on_message(channel, method, properties, body):
        key = method.routing_key
        try:
            msg = json.loads(body)
        except json.JSONDecodeError:
            msg = None
        if not isinstance(msg, dict) or 'zone' not in msg:
            print(f'[{name}] key={key:<30} REJECTED (no zone) -> NACK, requeue=False  body={body.decode(errors="replace")}',
                  flush=True)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return
        print(f'[{name}] key={key:<30} got #{msg["id"]} {msg["type"]} in {msg["zone"]}, {msg["city"]}  -> ACK', flush=True)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    ch.basic_consume(queue=queue, on_message_callback=on_message, auto_ack=False)
    try:
        ch.start_consuming()
    except KeyboardInterrupt:
        print(f'[{name}] stopped')
    finally:
        conn.close()


if __name__ == '__main__':
    main()

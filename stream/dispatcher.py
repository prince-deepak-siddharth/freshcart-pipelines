"""Dispatcher: publishes a request to the topic exchange `rapido-dispatch` every N seconds.

Routing key = city.zone.type   e.g.  bangalore.koramangala.ride

    python stream/dispatcher.py                      # random requests, every 2 s, forever
    python stream/dispatcher.py --duration 120       # stop after two minutes
    python stream/dispatcher.py --keys bangalore.koramangala.food chennai.tnagar.food
                                                     # publish exactly these routing keys (used for D1 proof)

Every 10th message is deliberately BAD (it has no "zone" field) so that drivers have something to NACK (D3).
The broker URL comes from the RABBITMQ_URL environment variable (never commit it).
"""
import argparse
import json
import os
import random
import time
from datetime import datetime, timezone

import pika

EXCHANGE = 'rapido-dispatch'
ZONES = {'bangalore': ['koramangala', 'indiranagar', 'whitefield'],
         'chennai': ['tnagar', 'whitefield']}
TYPES = ['ride', 'food']


def connect():
    url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/%2F')
    return pika.BlockingConnection(pika.URLParameters(url))


def make_message(n, city, zone, kind, bad=False):
    msg = {'id': n, 'city': city, 'zone': zone, 'type': kind,
           'ts': datetime.now(timezone.utc).isoformat(timespec='seconds')}
    if bad:
        del msg['zone']          # the bad message: zone is missing
    return msg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--interval', type=float, default=2.0, help='seconds between messages')
    ap.add_argument('--duration', type=float, default=None, help='stop after this many seconds')
    ap.add_argument('--bad-every', type=int, default=10, help='every Nth message has no zone (0 = never)')
    ap.add_argument('--keys', nargs='*', help='publish exactly these routing keys, once each')
    args = ap.parse_args()

    conn = connect()
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type='topic', durable=False)

    def publish(n, key, msg):
        ch.basic_publish(exchange=EXCHANGE, routing_key=key, body=json.dumps(msg))
        tag = '  <-- BAD (no zone)' if 'zone' not in msg else ''
        print(f'[dispatcher] #{n:<3} key={key:<34} {json.dumps(msg)}{tag}', flush=True)

    if args.keys:
        for n, key in enumerate(args.keys, 1):
            parts = key.split('.')
            msg = make_message(n, parts[0], parts[1] if len(parts) > 1 else None,
                               parts[2] if len(parts) > 2 else None)
            publish(n, key, msg)
            time.sleep(args.interval)
        conn.close()
        return

    start, n = time.time(), 0
    try:
        while args.duration is None or time.time() - start < args.duration:
            n += 1
            city = random.choice(list(ZONES))
            zone = random.choice(ZONES[city])
            kind = random.choice(TYPES)
            bad = args.bad_every > 0 and n % args.bad_every == 0
            publish(n, f'{city}.{zone}.{kind}', make_message(n, city, zone, kind, bad))
            time.sleep(args.interval)
    except KeyboardInterrupt:
        pass
    conn.close()
    print(f'[dispatcher] done, {n} messages published')


if __name__ == '__main__':
    main()

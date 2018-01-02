#!/usr/bin/env python3
import pika
import sys
import socket

'''
  Usage:
    Receives all messages routed via topic (set from cli) emitted from "e_emit_log_topic.py"
    1) start up a couple of e_receive_logs_topic.py sessions with different
       routes:
    > python3 e_receive_logs_topic.py "#"
    > python3 e_receive_logs_topic.py "kern.*"
    > python3 e_receive_logs_topic.py "*.critical"
    > python3 e_receive_logs_topic.py "kern.*" ".critical"

    2) send routed topic messages:

    > python3 e_emit_log_topic.py "kern.critical" "A critical kernel error"
    > python3 e_emit_log_topic.py "kern" "A kernel error"

    The first message should be see by all receivers
    The second message should only be seen by 1, 2, 3


  Demonstrates:
    * Publish Subscribe
    * Topic exchange

  Monitoring:
    * to view the results with the RabbitMQ manager:
    <hostname>:15672 in browser

    where <hostname> is the results of your hostname command

'''
def get_ip():
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  try:
    # doesn't have to be reachable
    s.connect(('10.255.255.255', 1))
    IP = s.getsockname()[0]
  except:
    IP = '127.0.0.1'
  finally:
    s.close()
  return IP

credentials = pika.PlainCredentials('bob', 'dobbs')
parameters = pika.ConnectionParameters(get_ip(), 5672, '/', credentials)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs',
  exchange_type='topic')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

binding_keys = sys.argv[1:]
if not binding_keys:
  sys.stderr.write("Usage: {} [binding_key]..\n".format(sys.argv[0]))
  sys.exit(1)

for binding_key in binding_keys:
  channel.queue_bind(exchange='topic_logs',
    queue=queue_name,
    routing_key=binding_key)

print(' [*] Waiting for logs. To exit press CTRL-C')

def callback(ch, method, properties, body):
  print(" [x] {!r}:{!r}".format(method.routing_key, body.decode('utf8')))

channel.basic_consume(callback,
  queue=queue_name,
  no_ack=True)

channel.start_consuming()



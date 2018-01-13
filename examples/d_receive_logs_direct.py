#!/usr/bin/env python3
import pika
import sys
import socket

'''
  Usage:
    Receives all messages routed (set from cli) emitted from  "d_emit_log_direct.py"
    1) start up a couple of d_receive_logs_direct.py sessions with different
       routes:
    > python3 d_receive_logs_direct.py info warning error
    > python3 d_receive_logs_direct.py error

    2) send routed messages:

    > python3 d_emit_log_direct.py error all_should_see_this
    > python3 d_emit_log_direct.py info first_should_see_this


  Demonstrates:
    * Publish Subscribe
    * Direct exchange

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

def hostname():
  return socket.gethostname()

# connection
def connection_using_basic_parameters():
  credentials = pika.PlainCredentials('bob', 'dobbs')
  parameters = pika.ConnectionParameters(hostname(), 5672, '/', credentials)
  connection = pika.BlockingConnection(parameters=parameters)
  return connection

def connection_using_url_parameters():
  credentials = {
      'protocol':'amqp',
      'user_name':'bob',
      'password':'dobbs',
      'hostname':hostname(),
      'port':'5672',
      'virtual_host':'/'}
  url = \
    "{protocol}://{user_name}:{password}@{hostname}:{port}/%2F".format(**credentials)
  parameters = pika.URLParameters(url)
  connection = pika.BlockingConnection(parameters=parameters)
  return connection

credentials = pika.PlainCredentials('bob', 'dobbs')
connection = connection_using_url_parameters()
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

severities = sys.argv[1:]
if not severities:
  sys.stderr.write("Usage: {} [info] [warning] [error]\n".format(sys.argv[0]))
  sys.exit(1)

for severity in severities:
  channel.queue_bind(exchange='direct_logs', queue=queue_name,
      routing_key=severity)

print(' [x] Waiting for logs. To exit press CTRL-C')
def callback(ch, method, properties, body):
  print(" [x] {}:{}".format(method.routing_key, body.decode('utf8')))

channel.basic_consume(callback,
  queue=queue_name,
  no_ack=True)

channel.start_consuming()

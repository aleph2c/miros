#!/usr/bin/env python3
import pika
import socket

'''
  Usage:
    Receives requests for remote procedure calls from "f_rpc_client.py"
    1) start up a couple of f_rpc_server.py sessions
    > python3 f_rpc_server.py
    > python3 f_rpc_server.py
    2) send rpc requests from:
    > python3 f_rpc_client.py
    > python3 f_rpc_client.py

    Observe that each of the f_rpc_server.py programs will take turns working on
    the rpc requests.  The load is distributed.

  Demonstrates:
    * Remote Procedure Calls

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
channel.queue_declare(queue='rpc_queue')

def fib(n):
  if n == 0:
    return 0
  elif n == 1:
    return 1
  else:
    return fib(n-1) + fib(n-2)

def on_request(ch, method, props, body):
  n = int(body)
  print(" [.] fib({})".format(n))
  response = fib(n)

  ch.basic_publish(exchange='',
      routing_key=props.reply_to,
      properties=pika.BasicProperties(correlation_id=\
          props.correlation_id),
      body=str(response)
  )
  ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue='rpc_queue')

print(" [x] Awaiting RPC requests")
channel.start_consuming()



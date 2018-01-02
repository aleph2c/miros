#!/usr/bin/env python3

import pika
import socket

'''
  Usage:
    Receives a message from "a_send.py"
    1) start "a_receive.py"
    2) send a message with "a_send.py"

  Demonstrates:
    * Hello world

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
  parameters = pika.ConnectionParameters(get_ip(), 5672, '/', credentials)
  connection = pika.BlockingConnection(parameters=parameters)
  return connection


def connection_using_url_parameters():
  credentials = {
      'protocol': 'amqp',
      'user_name': 'bob',
      'password': 'dobbs',
      'hostname': hostname(),
      'port': '5672',
      'virtual_host': '/'}
  url = \
    "{protocol}://{user_name}:{password}@{hostname}:{port}/%2F".format(**credentials)
  parameters = pika.URLParameters(url)
  connection = pika.BlockingConnection(parameters=parameters)
  return connection


connection = connection_using_url_parameters()
channel = connection.channel()

# if the queue already exists this call will do nothing
channel.queue_declare(queue='hello')


# create a callback function received messages in the queue
def callback(ch, method, properties, body):
  print(" [x]  Received {}".format(body.decode('utf8')))


# register the callback with a queue
channel.basic_consume(callback,
  queue='hello', no_ack=True)

# patiently wait forever
print(' [*] Waiting for message. To exit press CTRL+C')
channel.start_consuming()

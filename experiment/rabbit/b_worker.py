#!/usr/bin/env python3

'''
  Usage:
    Receives a new task request from "b_new_task.py"
    1) to start a worker:

    > python3 b_worker.py message....

  Demonstrates:
    * Work queues

  Monitoring:
    * to view the results with the RabbitMQ manager:
    <hostname>:15672 in browser

    where <hostname> is the results of your hostname command

'''
import pika
import time
import socket

# Taken from Jamieson Becker
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

# create a connection and a channel
credentials = pika.PlainCredentials('bob', 'dobbs')
parameters = pika.ConnectionParameters(get_ip(), 5672, '/', credentials)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()

# if the queue already exists this call will do nothing
channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for message. To exit press CTRL+C')

# create a callback function received messages in the queue
def callback(ch, method, properties, body):
  print(" [x]  Received {!s}".format(body.decode('utf8')))
  print("sleeping for {}".format(body.count(b'.')))
  time.sleep(body.count(b'.'))
  print(" [x] Done")
  ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)

# register the callback with a queue
channel.basic_consume(callback,
  queue='task_queue')

# patiently wait forever
channel.start_consuming()

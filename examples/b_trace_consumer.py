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
import socket
from miros.foreign import ForeignHsm
from miros.hsm import pp


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
parameters  = pika.ConnectionParameters(get_ip(), 5672, '/', credentials)
connection  = pika.BlockingConnection(parameters=parameters)
channel     = connection.channel()
count       = 0

# if the queue already exists this call will do nothing
channel.queue_declare(queue='spy_queue', durable=True)
channel.queue_declare(queue='trace_queue', durable=True)
print(' [*] Waiting for message. To exit press CTRL+C')


foreign_hsm = ForeignHsm()


# create a spy_callback function received messages in the queue
def spy_callback(ch, method, properties, body):
  global foreign_hsm
  foreign_spy_item = body.decode('utf8')
  foreign_hsm.append_to_spy(foreign_spy_item)
  print(" [x] {!s}".format(foreign_spy_item))
  ch.basic_ack(delivery_tag = method.delivery_tag)


# create a trace_callback function received messages in the queue
def trace_callback(ch, method, properties, body):
  global foreign_hsm
  pp(ch)
  foreign_trace_item = body.decode('utf8')
  foreign_hsm.append_to_trace(foreign_trace_item)
  print(" [x] Trace: {!s}".format(foreign_trace_item))
  ch.basic_ack(delivery_tag = method.delivery_tag)


def one_second_callback():
  global count
  global foreign_hsm
  global channel
  pp(foreign_hsm.spy())
  print(foreign_hsm.trace())
  # stop processing or reconnect this callback to a timer
  count += 1
  if count >= 3:
    channel.stop_consuming()
  else:
    connection.add_timeout(deadline=10, callback_method=one_second_callback)
    foreign_hsm.clear_spy()
    foreign_hsm.clear_trace()


connection.add_timeout(deadline=1, callback_method=one_second_callback)
channel.basic_qos(prefetch_count=10)

# register the spy_callback with a queue
channel.basic_consume(spy_callback,   queue='spy_queue')
channel.basic_consume(trace_callback, queue='trace_queue')

# patiently wait forever
channel.start_consuming()


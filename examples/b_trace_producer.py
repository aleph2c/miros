#!/usr/bin/env python3
'''
  Usage:
    Sends a new task request to "b_worker.py"
    1) start up a couple of worker.py sessions
    2) send delayed messages (where a dot is a second of delay):

    > python3 b_new_task.py message....

  Demonstrates:
    * Work queues

  Monitoring:
    * to view the results with the RabbitMQ manager:
    <hostname>:15672 in browser

    where <hostname> is the results of your hostname command

'''

import pika
import sys

# create credentials, connection and a channel
credentials = pika.PlainCredentials('bob', 'dobbs')
parameters = pika.ConnectionParameters('192.168.1.72', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()

# if this queue already exists this call will not do anything
channel.queue_declare(queue='task_queue', durable=True)

simple_trace = ['11:35:20.470871 [01352] WaitComplete: outer->inner',
                '11:35:20.469870 [01352] WaitComplete: inner->inner']

# Send our trace and print what we sent
for trace_item in simple_trace:
  channel.basic_publish(exchange='',
      routing_key='task_queue',
      body=trace_item,
      properties=pika.BasicProperties(
        delivery_mode=2,  # make message persistent
      ))
  print(" [x] Sent: {}".format(trace_item))

connection.close()

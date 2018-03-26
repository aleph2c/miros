#!/usr/bin/env python3
import pika
import sys

'''
  Usage:
    Sends a new task request to "c_receive_logs_fanout.py"
    1) start up a couple of c_receive_logs_fanout.py sessions
    2) send a message

    > python3 c_emit_log_fanout.py <some message>

    Both receivers should see the emitted messages

  Demonstrates:
    * Publish Subscribe
    * Fanout exchange

  Monitoring:
    * to view the results with the RabbitMQ manager:
    <hostname>:15672 in browser

    where <hostname> is the results of your hostname command

'''

credentials = pika.PlainCredentials('bob', 'dobbs')
parameters = pika.ConnectionParameters('192.168.1.69', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='fanout')

message = ' '.join(sys.argv[1:]) or "info: Hello World!"
channel.basic_publish(exchange='logs', routing_key='', body=message)

print(" [x] Sent {!s}".format(message))
connection.close()

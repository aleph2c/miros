#!/usr/bin/env python3
import pika
import sys

'''
  Usage:
    Sends a routed message (set from cli) to "d_receive_logs_direct.py"
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
credentials = pika.PlainCredentials('bob', 'dobbs')
parameters = pika.ConnectionParameters('192.168.1.69', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

severity = sys.argv[1] if len(sys.argv) > 2 else 'info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'
channel.basic_publish(exchange='direct_logs',
    routing_key=severity,
    body=message)

print(" [x] Sent {}:{}".format(severity, message))
connection.close()

#!/usr/bin/env python3
import pika
import sys

'''
  Usage:
    Sends a topic routed messages (set from cli) to "e_receive_logs_topic.py"
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
credentials = pika.PlainCredentials('bob', 'dobbs')
parameters = pika.ConnectionParameters('192.168.1.73', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs',
    exchange_type='topic')

routing_key = sys.argv[1] if len(sys.argv) > 2 else 'anonymous.info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'
channel.basic_publish(exchange='topic_logs',
  routing_key=routing_key,
  body=message)
print(" [x] Sent {}:{}".format(routing_key, message))
connection.close()

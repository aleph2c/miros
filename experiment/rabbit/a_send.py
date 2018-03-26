#!/usr/bin/env python3

import pika
import socket
'''
  Usage:
    Sends a message to "a_receive.py"
    1) start the "a_receive.py" program
    2) send a message

    > python3 a_send.py

  Demonstrates:
    * consumer (a_receive.py) 
    * producer (a_send.py) 
     

  Monitoring:
    * to view the results with the RabbitMQ manager:
    <hostname>:15672 in browser

    where <hostname> is the results of your hostname command

'''

# create credentials, connection and a channel
credentials = pika.PlainCredentials('bob', 'dobbs')
parameters = pika.ConnectionParameters('192.168.1.69', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters=parameters)
channel = connection.channel()

# if this queue already exists this call will not do anything
channel.queue_declare(queue='hello')

# publish a message to the queue
channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')

print(" [x] Sent 'Hello World!'")
connection.close()

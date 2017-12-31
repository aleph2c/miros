#!/usr/bin/env python3
import pika
import uuid

'''
  Usage:
    Sends a remote procedure call to "f_rpc_server.py"
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

class FibonacciRpcClient():
  def __init__(self):
    
    credentials = pika.PlainCredentials('bob', 'dobbs')
    parameters = pika.ConnectionParameters('192.168.1.73', 5672, '/', credentials)
    self.connection = pika.BlockingConnection(parameters=parameters)
    self.channel = self.connection.channel()

    result = self.channel.queue_declare(exclusive=True)
    self.callback_queue = result.method.queue

    self.channel.basic_consume(self.on_response,
        no_ack=True,
        queue=self.callback_queue)

  def on_response(self, ch, method, props, body):
    if self.corr_id == props.correlation_id:
      self.response = body

  def call(self, n):
    self.response = None
    self.corr_id = str(uuid.uuid4())
    self.channel.basic_publish(exchange='',
        routing_key='rpc_queue',
        properties=pika.BasicProperties(
          reply_to=self.callback_queue,
          correlation_id=self.corr_id,
          ),
        body=str(n)
    )
    while self.response is None:
      self.connection.process_data_events()
    return int(self.response)

fibonacci_rpc = FibonacciRpcClient()
print(" [x] Requesting fib(34)")
for i in range(34):
  response = fibonacci_rpc.call(i)
  print(" [.] Got {!r}".format(response))

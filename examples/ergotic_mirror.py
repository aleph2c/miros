
#!/usr/bin/env python3
import sys
import pika
import time
import socket
from types import SimpleNamespace
from threading import Thread, Event

class Connection():

  @staticmethod
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

  @staticmethod
  def get_blocking_connection(user, password, ip, port):
    credentials = pika.PlainCredentials(user, password)
    parameters = pika.ConnectionParameters(ip, port, '/', credentials)
    connection = pika.BlockingConnection(parameters=parameters)
    return connection

class ReceiveConnections():
  def __init__(self, user, password):
    self.connection = Connection.get_blocking_connection(user, password, Connection.get_ip(), 5672)
    self.channel = self.connection.channel()
    self.channel.exchange_declare(exchange='mirror', exchange_type='direct')
    # destroy queue when done
    result = self.channel.queue_declare(exclusive=True)
    self.queue_name = result.method.queue
    self.channel.queue_bind(exchange='mirror', queue=self.queue_name, routing_key=Connection.get_ip())

    self.task_run_event = Event()
    self.task_run_event.set()

    print(' [x] Waiting for messages. To exit press CTRL-C')
    def callback(ch, method, properties, body):
      self.callback(ch, method, properties, body)
    self.channel.basic_consume(callback, queue=self.queue_name, no_ack=True)

  def callback(self, ch, method, properties, body):
    print(" [x] {}:{}".format(method.routing_key, body.decode('utf8')))

  def start_consuming(self):
    def channel_consumer(self):
      self.task_run_event.set()
      def timeout_callback():
        if self.task_run_event.is_set():
          self.connection.add_timeout(deadline=10, callback_method=timeout_callback)
        else:
          self.channel.stop_consuming()
          return
      self.connection.add_timeout(deadline=10, callback_method=timeout_callback)
      self.channel.start_consuming()
    thread = Thread(target=channel_consumer, args=(self,), daemon=True)
    thread.start()

  def stop_consuming(self):
    self.task_run_event.clear()

class EmitConnections():

  def __init__(self, base, start, end, user, password):
    possible_ips  = [base + str(i) for i in [*range(start, end + 1)]]
    targets       = EmitConnections.scout_targets(possible_ips, user, password)
    self.channels = EmitConnections.get_channels(targets, user, password)

  def message_to_other_channels(self, message):
    for channel in self.channels:
      ip = channel.extension.ip_address
      channel.basic_publish(exchange='mirror',
          routing_key=ip, body=message)
      print(" [x] Sent \"{}\" to {}".format(message, ip))

  @staticmethod
  def scout_targets(targets, user, password):
    possible_targets = targets[:]
    possible_targets.remove(Connection.get_ip())
    message = 'discovery probe'

    for target in possible_targets[:]:
      try:
        connection = Connection.get_blocking_connection(user, password, target, 5672)
        channel = connection.channel()
        channel.exchange_declare(exchange='mirror', exchange_type='direct')
        channel.basic_publish(exchange='mirror', routing_key=target, body=message)
        print(" [x] Sent \"{}\" to {}".format(message, target))
        connection.close()
      except:
        possible_targets.remove(target)
    return possible_targets

  @staticmethod
  def get_channels(targets, user, password):
    channels = []
    for target in targets:
      try:
        connection = Connection.get_blocking_connection(user, password, target, 5672)
        channel = connection.channel()
        channel.exchange_declare(exchange='mirror', exchange_type='direct')
        channel.extension = SimpleNamespace()
        setattr(channel.extension, 'ip_address', target)
        channels.append(channel)
      except:
        pass
    return channels

class Receiver():
  def __init__(self, user, password):
    self.user     = user
    self.password = password
    self.rx = ReceiveConnections(user, password)

  def start_consuming(self):
    self.rx.start_consuming()

  def stop_consuming(self):
    self.rx.stop_consuming()
    del(self.rx)
    self.rx = ReceiveConnections(self.user, self.password)

class Transmitter():

  def __init__(self, user, password):
    self.tx = EmitConnections(base="192.168.1.",
                start=70,
                end=73,
                user=user,
                password=password)

  def message_to_other_channels(self, message):
    self.tx.message_to_other_channels(message)


tranceiver_type = sys.argv[1:]
if not tranceiver_type:
  sys.stderr.write("Usage: {} [rx]/[tx]\n".format(sys.argv[0]))

if tranceiver_type[0] == 'rx':
  rx = Receiver('bob', 'dobbs')
  rx.start_consuming()
  time.sleep(10)
  rx.stop_consuming()
  rx.start_consuming()
  time.sleep(10)
  rx.stop_consuming()

elif tranceiver_type[0] == 'tx':
  tx = Transmitter(user="bob", password="dobbs")
  tx.message_to_other_channels("an actual message")
else:
  sys.stderr.write("Usage: {} [rx]/[tx]\n".format(sys.argv[0]))



#!/usr/bin/env python3
import sys
import pika
import time
import uuid
import socket
import pickle
from functools import wraps
from types import SimpleNamespace
from threading import Thread
from threading import Event as ThreadingEvent
from cryptography.fernet import Fernet
from miros.event import Event, signals


class Connection():
  '''
  A grab bag of networking static methods used by different objects within this
  module
  '''
  @staticmethod
  def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
      s.connect(('10.255.255.255', 1))
      ip = s.getsockname()[0]
    except:
      ip = '127.0.0.1'
    finally:
      s.close()
    return ip

  @staticmethod
  def key():
    '''
    A better way to do this is to get the key from your flash key.
    '''
    return b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg='

  @staticmethod
  def get_blocking_connection(user, password, ip, port):
    credentials = pika.PlainCredentials(user, password)
    parameters = pika.ConnectionParameters(ip, port, '/', credentials)
    connection = pika.BlockingConnection(parameters=parameters)
    return connection

  @staticmethod
  def decrypt(fn):
    @wraps(fn)
    def _decrypt(ch, method, properties, cyphertext):
      '''LocalConsumer.decrypt()'''
      f = Fernet(Connection.key())
      plain_text = f.decrypt(cyphertext)
      fn(ch, method, properties, plain_text)
    return _decrypt

  @staticmethod
  def encrypt(fn):
    @wraps(fn)
    def _encrypt(*args):
      if len(args) == 1:
        plain_text = args[0]
      elif len(args) == 2:
        plain_text = args[1]
      else:
        assert(False)
      f = Fernet(Connection.key())
      cyphertext = f.encrypt(plain_text)
      if len(args) == 1:
        fn(cyphertext)
      else:
        fn(args[0], cyphertext)
    return _encrypt

  @staticmethod
  def serialize(fn):
    @wraps(fn)
    def _pickle_dumps(*args):
      if len(args) == 1:
        message = args[0]
      elif len(args) == 2:
        message = args[1]
      else:
        assert(False)

      # The event object is dynamically constructed and can't be serialized by
      # pickle, so we call it's custom serializer prior to pickling it
      if isinstance(message, Event):
        message = Event.dumps(message)

      pmessage = pickle.dumps(message)

      if len(args) == 1:
        fn(pmessage)
      else:
        fn(args[0], pmessage)
    return _pickle_dumps

  @staticmethod
  def deserialize(fn):
    @wraps(fn)
    def _pickle_loads(ch, method, properties, p_plain_text):
      plain_text = pickle.loads(p_plain_text)
      if isinstance(plain_text, Event):
        plain_text = Event.loads(plain_text)
      fn(ch, method, properties, plain_text)
    return _pickle_loads


class ReceiveConnections():
  '''
  Receives connections on this ip address from port 5672
  It creates a 'mirror' exchange using direct routing where the routing key is
  this ip address as a string.

  The interface to this class should be done through the Receiver

  '''
  def __init__(self, user, password):
    # create a connection and a direct exchange called 'mirror' on this ip
    self.connection = Connection.get_blocking_connection(user, password, Connection.get_ip(), 5672)
    self.channel    = self.connection.channel()
    self.channel.exchange_declare(exchange='mirror', exchange_type='direct')

    # destroy the rabbitmq queue when done
    result          = self.channel.queue_declare(exclusive=True)
    self.queue_name = result.method.queue
    # create a channel with a direct routing key, the key is our ip address
    self.channel.queue_bind(exchange='mirror', queue=self.queue_name, routing_key=Connection.get_ip())

    # The 'start_consuming' method of the pika library will block the program.
    # for this reason we will put it in it's own thread so that it does not harm
    # our program flow, to communicate to it we use an Event from the threading
    # class
    self.task_run_event = ThreadingEvent()
    self.task_run_event.set()

    # We provide a default message callback, but it is more than likely that the
    # client will register their own (why else use this class?)
    self.live_callback = self.default_callback
    print(' [x] Waiting for messages. To exit press CTRL-C')

    # We wrap the tunable callback with decryption and a serial decoder
    # this way the client doesn't have to know about this complexity
    @Connection.decrypt
    @Connection.deserialize
    def callback(ch, method, properties, body):
      self.live_callback(ch, method, properties, body)

    # Register the above callback with the queue
    self.channel.basic_consume(callback, queue=self.queue_name, no_ack=True)

  def default_callback(self, ch, method, properties, body):
    '''
    This default callback is provided out of the box, it will be ignored by the
    client since they will register their own callback
    '''
    print(" [x] {}:{}".format(method.routing_key, body))

  def register_live_callback(self, live_callback):
    '''
    Register a callback with this object.  It will be called once a message is
    received, decrypted and decoded.

    Example:

      def custom_rx_callback(ch, method, properties, body):
        if "signal_name" in body:
          # turn our event json object back into an event
          event = Event.loads(body)
          print(" [+] {}:{}".format(method.routing_key, event))
        else:
          print(" [+] {}:{}".format(method.routing_key, body))

      rx = Receiver('bob', 'dobbs')
      rx.register_live_callback(custom_rx_callback)

    '''
    self.live_callback = live_callback

  def start_consuming(self):
    # We make a thread so that the channel.start_consuming doesn't steal our
    # program control.

    # The thread has it's own timeout callback (pika) which wakes up every 10
    # seconds and checks the self.trask_run_event, which is controlled outside
    # of the thread.  If it is set, it continues to work, if it isn't set it
    # stop the pika consumer and the thread dies.
    def channel_consumer(self):
      '''
      This timeout_callback is the only way to communicate with a pika channel
      once it has started consuming.  This time out checks to see if this
      thread should die, if so, it calls stop_consuming, if not, it arms
      another timeout callback.  (Working with the library)
      '''
      self.task_run_event.set()

      def timeout_callback():
        if self.task_run_event.is_set():
          self.connection.add_timeout(deadline=10, callback_method=timeout_callback)
        else:
          self.channel.stop_consuming()
          return

      # We are within our own thread, we arm a timeout callback
      self.connection.add_timeout(deadline=10, callback_method=timeout_callback)
      # This process will block forever, with the exception of calling the
      # timeout_callback every 10 seconds.
      self.channel.start_consuming()

    # Create and start the thread.  The thread can be stopped by clearing the
    # task_run_event Event.
    thread = Thread(target=channel_consumer, args=(self,), daemon=True)
    thread.start()

  def stop_consuming(self):
    '''
    This will kill the channel_consumer within the next 10 seconds
    '''
    self.task_run_event.clear()


class EmitConnections():
  '''
  Scouts a range of ip addresses, creates a 'mirror' exchange which can dispatch
  messages to any rabbitmq server it has detected in the ip range.  It uses a
  direct routing strategy where the routing_key is the ip address of the node it
  wishes to communicate with.

  Once it has access to a number of network nodes, it provide a method to
  communicate with them, 'message_to_other_channels'.  Any object that is sent
  to this message is serialized into bytes then encrypted prior to being
  dispatched accross the network.

  This class should be accessed through the Transmitter object

  '''
  def __init__(self, base, start, end, user, password):
    possible_ips  = [base + str(i) for i in [*range(start, end + 1)]]
    targets       = EmitConnections.scout_targets(possible_ips, user, password)
    self.channels = EmitConnections.get_channels(targets, user, password)

  @Connection.serialize  # pickle.dumps
  @Connection.encrypt
  def message_to_other_channels(self, message):
    '''
    Send messages to all of confirmed channels
    '''
    for channel in self.channels:
      ip = channel.extension.ip_address
      channel.basic_publish(exchange='mirror',
          routing_key=ip, body=message)
      print(" [x] Sent \"{}\" to {}".format(message, ip))

  @staticmethod
  def scout_targets(targets, user, password):
    '''
    Returns a subset of ip address from the targets.  The common feature of
    these subsets is that they can you can connect to the via rabbitmq.  To do
    this:
    - They have have a mirror exchange
    - They need to be able to respond to a message with a routing_key that is
      the same as their ip address
    - They can descrypt the message we are sending to them
    '''
    possible_targets = targets[:]
    possible_targets.remove(Connection.get_ip())
    # some random message so that our encryption isn't easily broken
    message = uuid.uuid4().hex.upper()[0:12]

    for target in possible_targets[:]:
      try:
        connection = Connection.get_blocking_connection(user, password, target, 5672)
        channel = connection.channel()
        channel.exchange_declare(exchange='mirror', exchange_type='direct')

        @Connection.serialize
        @Connection.encrypt
        def send(message):
          channel.basic_publish(exchange='mirror', routing_key=target, body=message)

        send(message)
        print(" [x] Sent \"{}\" to {}".format(message, target))
        connection.close()
      except:
        possible_targets.remove(target)
    return possible_targets

  @staticmethod
  def get_channels(targets, user, password):
    '''
    Get a set of rabbitmq channels given a list of ip addresses and the user
    name and password of the local rabbitmq server.
    '''
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
  '''
  Creates a rabbitmq receiver.  You can register a live callback which will be
  called when a message is received, then start consuming.  You can stop
  consuming and start consuming at a later time.

  Example:
    import time

    def custom_rx_callback(ch, method, properties, body):
      if "signal_name" in body:
        # turn our event json object back into an event
        event = Event.loads(body)
        print(" [+] {}:{}".format(method.routing_key, event))
      else:
        print(" [+] {}:{}".format(method.routing_key, body))

    rx = Receiver(user='bob', password='dobbs')
    rx.register_live_callback(custom_rx_callback)
    rx.start_consuming() # launches a consuming task
    time.sleep(10)
    rx.stop_consuming()  # kills consuming task
    rx.start_consuming() # launches a consuming task with same custom_rx_callback
  '''
  def __init__(self, user, password):
    self.user     = user
    self.password = password
    self.rx = ReceiveConnections(user, password)

  def start_consuming(self):
    self.rx.start_consuming()

  def register_live_callback(self, live_callback):
    '''
    Register a callback with this object.  It will be called once a message is
    received, decrypted and decoded.

    Example:

      def custom_rx_callback(ch, method, properties, body):
        if "signal_name" in body:
          # turn our event json object back into an event
          event = Event.loads(body)
          print(" [+] {}:{}".format(method.routing_key, event))
        else:
          print(" [+] {}:{}".format(method.routing_key, body))

      rx = Receiver('bob', 'dobbs')
      rx.register_live_callback(custom_rx_callback)

    '''
    self.live_callback = live_callback
    self.rx.register_live_callback(live_callback)

  def stop_consuming(self):
    self.rx.stop_consuming()
    del(self.rx)
    self.rx = ReceiveConnections(self.user, self.password)
    # re-register our live callback with the next instantiation
    if hasattr(self, 'live_callback') is True:
      if self.live_callback is not None:
        self.rx.register_live_callback(self.live_callback)


class Transmitter():
  '''
  Scans addresses 192.168.1.70-192.168.1.73 looking for rabbitmq receivers.  If
  it finds them, they will be accessible through the message_to_other_channels
  method provided by the class.

  Example:
    tx = Transmitter(user="bob", password="dobbs")
    tx.message_to_other_channels("an actual message")

    # Note, to send a miros event across the network you will have to encode it
    # first:
    tx.message_to_other_channels(Event.dumps(Event(signal=signals.Mirror, payload=[1,2,3])))

    # To decode this event:
    event = Event.loads(event_as_json)
    print(event) #=> Mirror::<[1,2,3]>

  '''
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


def custom_rx_callback(ch, method, properties, body):
  print(" [+] {}:{}".format(method.routing_key, body))


if tranceiver_type[0] == 'rx':
  rx = Receiver('bob', 'dobbs')
  rx.register_live_callback(custom_rx_callback)
  rx.start_consuming()
  time.sleep(100)
  rx.stop_consuming()
  rx.start_consuming()
  time.sleep(10)
  rx.stop_consuming()
elif tranceiver_type[0] == 'tx':
  tx = Transmitter(user="bob", password="dobbs")
  tx.message_to_other_channels(Event(signal=signals.Mirror, payload=[1, 2, 3]))
  tx.message_to_other_channels([1, 2, 3, 4])
else:
  sys.stderr.write("Usage: {} [rx]/[tx]\n".format(sys.argv[0]))


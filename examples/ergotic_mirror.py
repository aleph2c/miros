#!/usr/bin/env python3
import sys
import pika
import time
import uuid
import socket
import pickle
import subprocess
from functools import wraps
from threading import Thread
from types import SimpleNamespace
from cryptography.fernet import Fernet
from threading import Event as ThreadingEvent
from miros.event import signals, Event


class Connection():
  '''
  A set of networking static methods used by different objects within this
  module.

  API:
    Connection.get_ip()                  -> get your own ip address
    Connection.ip_addresses_on_lan       -> get all IP addresses on LAN

    Connection.serialize                 -> serialization decorator
    Connection.deserialize               -> deserialization decorator

    Connection.key()                     -> get the encryption key
    Connection.ecrypt                    -> encryption decorator
    Connection.decrypt                   -> decryption decorator

    Connection.get_blocking_connection() -> get a blocking connection to a
                                            RabbitMq server
  '''
  @staticmethod
  def get_ip():
    '''
    Get the ip of this computer:

    Example:
      Connection.get_ip()
    '''
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
    Get the encryption key for this connection.  This key is used for encryption
    and decryption.

    Example:
      key = Connection.key()

    Note:
    To generate a new key: Fernet.generate_key()
    A better way to do this is to get the key from your connected flash-drive.
    '''
    return b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg='

  @staticmethod
  def get_blocking_connection(user, password, ip, port):
    '''
    Create and get a blocking connection to a rabbitMq server running on this,
    or another machine:

    Example:
      connection = Connection.get_blocking_connection(
        'bob', 'dobbs', '192.168.1.72', 5672)
    '''
    credentials = pika.PlainCredentials(user, password)
    parameters = pika.ConnectionParameters(ip, port, '/', credentials)
    connection = pika.BlockingConnection(parameters=parameters)
    return connection

  @staticmethod
  def serialize(fn):
    '''
    A decorator which will turn arguments into a byte stream prior to encryption:

    Example:
      @Connection.serialize  # <- HERE: 'message' turned into byte stream
      @Connection.encrypt
      def message_to_other_channels(self, message):
        for channel in self.channels:
          ip = channel.extension.ip_address
          channel.basic_publish(exchange='mirror',
              routing_key=ip, body=message)
          print(" [x] Sent \"{}\" to {}".format(message, ip))

    '''
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
  def encrypt(fn):
    '''
    A decorator which will encrypt a byte stream prior to transmission:

    Example:
      @Connection.serialize
      @Connection.encrypt   # <- HERE: 'message' bytestream encyrpted
      def message_to_other_channels(self, message):
        for channel in self.channels:
          ip = channel.extension.ip_address
          channel.basic_publish(exchange='mirror',
              routing_key=ip, body=message)
          print(" [x] Sent \"{}\" to {}".format(message, ip))

    '''
    @wraps(fn)
    def _encrypt(*args):
      '''
      encrypt a byte stream
      '''
      # To get around the self as the first argument issue
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
  def decrypt(fn):
    '''
    A decorator which will decrypt a received message into a byte stream.

    Example:
      @Connection.decrypt  # <- HERE: 'body' decrypted into a byte stream
      @Connection.deserialize
      def custom_rx_callback(ch, method, properties, body):
        print(" [+] {}:{}".format(method.routing_key, body))

    '''
    @wraps(fn)
    def _decrypt(ch, method, properties, cyphertext):
      '''LocalConsumer.decrypt()'''
      f = Fernet(Connection.key())
      plain_text = f.decrypt(cyphertext)
      fn(ch, method, properties, plain_text)
    return _decrypt

  @staticmethod
  def deserialize(fn):
    '''
    A decorator turn a serialized byte stream into a python object

    Example:
      @Connection.decrypt
      @Connection.deserialize  # <- HERE: 'body' bytestream turn into object
      def custom_rx_callback(ch, method, properties, body):
        print(" [+] {}:{}".format(method.routing_key, body))

    '''
    @wraps(fn)
    def _pickle_loads(ch, method, properties, p_plain_text):
      plain_text = pickle.loads(p_plain_text)
      if isinstance(plain_text, Event):
        plain_text = Event.loads(plain_text)
      fn(ch, method, properties, plain_text)
    return _pickle_loads

  @staticmethod
  def ip_addresses_on_lan():
    '''
    The Windows Linux Subsystem is currently broken, it does not support a lot
    of Linux networking commands - so, we can't use the nice tooling provided
    by the community.  Instead I call out to the cmd.exe file of DOS and send it
    the DOS version of arp to get a list of IP addresses on the LAN.

    The 'grep -Po 192\.\d+\.\d+\.\d+' applies the Perl regular expression
    with matching output only to our stream.  This will return all of the IP
    addresses in the class C family (192.xxx.xxx.xxx)

    Example:
      ip_addresses = Connection.ip_addresses_on_lan()
    '''
    wsl_cmd   = 'cmd.exe /C arp.exe -a'
    linux_cmd = 'arp -a'

    grep_cmd = 'grep -Po 192\.\d+\.\d+\.\d+'
    candidates = []

    for cmd in [wsl_cmd, linux_cmd]:
      cmd_as_list = cmd.split(" ")
      grep_as_list = grep_cmd.split(" ")
      output = ''
      try:
        ps = subprocess.Popen(cmd_as_list, stdout=subprocess.PIPE)
        output = subprocess.check_output(grep_as_list, stdin=ps.stdout)
        ps.wait()
        if output is not '':
          candidates = output.decode('utf-8').split('\n')
          if len(candidates) > 0:
            break
      except:
        # our windows command did not work on Linux
        pass
    return list(filter(None, candidates))

class ReceiveConnections():
  '''
  Receives connections on this ip address from port 5672

  It creates a 'mirror' exchange using direct routing where the routing key is
  this ip address as a string.

  The interface to this class should be done through the RabbitDirectReceiver

  Example:
    rx = ReceiveConnections(user="bob", password="dobbs")

  '''
  def __init__(self, user, password, port=5672):
    # create a connection and a direct exchange called 'mirror' on this ip
    self.connection = Connection.get_blocking_connection(user, password, Connection.get_ip(), port)
    self.channel = self.connection.channel()
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

    # Register the above callback with the queue, turn off message
    # acknowledgements
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
        print(" [+] {}:{}".format(method.routing_key, body))

      rx = RabbitDirectReceiver('bob', 'dobbs')
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
  Scouts a range of IP addresses, creates a 'mirror' exchange which can dispatch
  messages to any RabbitMq server it has detected in the IP range.  It uses a
  direct routing strategy where the routing_key is the IP address of the node it
  wishes to communicate with.

  Once it has access to a number of network nodes, it provide a method to
  communicate with them, 'message_to_other_channels'.  Any object that is sent
  to this message is serialized into bytes then encrypted prior to being
  dispatched across the network.

  This class should be accessed through the RabbitDirectTransmitter object

  Example:
    tx = EmitConnections(user, password)

  '''
  def __init__(self, user, password, port=5672):
    possible_ips  = Connection.ip_addresses_on_lan()
    targets       = EmitConnections.scout_targets(possible_ips, user, password)
    self.channels = EmitConnections.get_channels(targets, user, password, port)

  @Connection.serialize  # pickle.dumps
  @Connection.encrypt
  def message_to_other_channels(self, message):
    '''
    Send messages to all of confirmed channels, messages are not persistent
    '''
    for channel in self.channels:
      ip = channel.extension.ip_address
      channel.basic_publish(exchange='mirror',
          routing_key=ip, body=message)
      print(" [x] Sent \"{}\" to {}".format(message, ip))

  @staticmethod
  def scout_targets(targets, user, password, port=5672):
    '''
    Returns a subset of ip address from the targets.  The common feature of
    these subsets is that they can you can connect to the via rabbitmq.  To do
    this:
    * They have have a mirror exchange
    * They need to be able to respond to a message with a routing_key that is
      the same as their ip address
    * They can descrypt the message we are sending to them

    Example:
      # assumptions, user and password or correct
      #              possible_ips is a list of IP addresses to check
      targets = EmitConnections.scout_targets(possible_ips, user, password)

    '''
    possible_targets = targets[:]
    possible_targets.append(Connection.get_ip())

    # some random message so that our encryption isn't easily broken
    message = uuid.uuid4().hex.upper()[0:12]

    for target in possible_targets[:]:
      try:
        connection = Connection.get_blocking_connection(user, password, target, port)
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
  def get_channels(targets, user, password, port=5672):
    '''
    Get a set of rabbitmq channels given a list of ip addresses and the user
    name and password of the local rabbitmq server.
    '''
    channels = []
    for target in targets:
      try:
        connection = Connection.get_blocking_connection(user, password, target, port)
        channel = connection.channel()
        channel.exchange_declare(exchange='mirror', exchange_type='direct')
        channel.extension = SimpleNamespace()
        setattr(channel.extension, 'ip_address', target)
        channels.append(channel)
      except:
        pass
    return channels


class RabbitDirectReceiver():
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

    rx = RabbitDirectReceiver(user='bob', password='dobbs')
    rx.register_live_callback(custom_rx_callback)
    rx.start_consuming() # launches a consuming task
    time.sleep(10)
    rx.stop_consuming()  # kills consuming task
    rx.start_consuming() # launches a consuming task with same custom_rx_callback
  '''
  def __init__(self, user, password, port=5672):
    self.user     = user
    self.password = password
    self.port     = port
    self.rx = ReceiveConnections(user, password, port)

  def start_consuming(self):
    self.rx.start_consuming()

  def register_live_callback(self, live_callback):
    '''
    Register a callback with this object.  It will be called once a message is
    received, decrypted and decoded.

    Example:

      def custom_rx_callback(ch, method, properties, body):
        print(" [+] {}:{}".format(method.routing_key, body))

      rx = RabbitDirectReceiver(user='bob', password='dobbs')
      rx.register_live_callback(custom_rx_callback)

    '''
    self.live_callback = live_callback
    self.rx.register_live_callback(live_callback)

  def stop_consuming(self):
    self.rx.stop_consuming()
    del(self.rx)
    self.rx = ReceiveConnections(self.user, self.password, self.port)
    # re-register our live callback with the next instantiation
    if hasattr(self, 'live_callback') is True:
      if self.live_callback is not None:
        self.rx.register_live_callback(self.live_callback)


class RabbitDirectTransmitter(EmitConnections):
  def __init__(self, user, password, port):
    super().__init__(user, password, port)

tranceiver_type = sys.argv[1:]
if not tranceiver_type:
  sys.stderr.write("Usage: {} [rx]/[tx]\n".format(sys.argv[0]))

def custom_rx_callback(ch, method, properties, body):
  print(" [+] {}:{}".format(method.routing_key, body))


if __name__ == "__main__":
  if tranceiver_type[0] == 'rx':
    rx = RabbitDirectReceiver(user='bob', password='dobbs', port=5672)
    rx.register_live_callback(custom_rx_callback)
    rx.start_consuming()
    time.sleep(100)
    rx.stop_consuming()
    rx.start_consuming()
    time.sleep(10)
    rx.stop_consuming()
  elif tranceiver_type[0] == 'tx':
    tx = RabbitDirectTransmitter(user="bob", password="dobbs")
    tx.message_to_other_channels(Event(signal=signals.Mirror, payload=[1, 2, 3]))
    tx.message_to_other_channels([1, 2, 3, 4])
  elif tranceiver_type[0] == 'ergotic':
    tx = RabbitDirectTransmitter(user="bob", password="dobbs", port=5672)
    rx = RabbitDirectReceiver(user='bob', password='dobbs', port=5672)
    rx.register_live_callback(custom_rx_callback)
    rx.start_consuming()
    for i in range(0, 10):
      tx.message_to_other_channels(Event(signal=signals.Mirror, payload=[i]))
      time.sleep(2)
    rx.stop_consuming()
  else:
    sys.stderr.write("Usage: {} [rx]/[tx]\n".format(sys.argv[0]))


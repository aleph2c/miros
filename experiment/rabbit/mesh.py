import os
import re
import time
import pika
import uuid
import pickle
import pprint
import socket
import logging
import ipaddress
import netifaces  # pip3 install netifaces --user
import functools
import subprocess
from threading import Thread
from miros.event import Event
from queue import Queue as ThreadQueue
from cryptography.fernet import Fernet
from threading import Event as ThreadEvent
from miros.activeobject import ActiveObject
from miros.activeobject import Factory
from datetime import datetime as stdlib_datetime

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
        '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class SimplePikaTopicConsumer():
  """
  This is a pika (Python-RabbitMq) message consumer (topic routing), which is
  heavily based on the asynchronous example provided in the pike documentation.
  It should handle unexpected interactions with RabbitMQ such as channel and
  connection closures.

  If RabbitMQ closes the connection, it will reopen it. You should
  look at the output, as there are limited reasons why the connection may
  be closed, which usually are tied to permission related issues or
  socket timeouts.

  If the channel is closed, it will indicate a problem with one of the
  commands that were issued and that should surface in the output as well.

  Example:

    pc = PikaTopicConsumer(
      amqp_url='amqp://bob:dobbs@localhost:5672/%2F',
      routing_key='pub_thread.text',
      exchange_name='sex_change',
      queue_name='g_queue',
    )
    pc.start_thread()
  """
  EXCHANGE_TYPE = 'topic'
  KILL_THREAD_CALLBACK_TEMPO = 1.0  # how long it will take the thread to quit
  RPC_QUEUE_NAME = 'RPC_QUEUE'
  QUEUE_TTL_IN_MS = 500

  def __init__(self,
    amqp_url,
    routing_key,
    exchange_name,
    message_ttl_in_ms=None):
    """Create a new instance of the consumer class, passing in the AMQP
    URL used to connect to RabbitMQ.

    :param str amqp_url: The AMQP url to connect with

    """
    self._connection = None
    self._channel = None
    self._closing = False
    self._consumer_tag = None
    self._url = amqp_url
    self._task_run_event = ThreadEvent()
    self._exchange_name = exchange_name
    self._routing_key = routing_key
    self._queue_name = None

    if not message_ttl_in_ms:
      self._message_ttl_in_ms = self.QUEUE_TTL_IN_MS
    else:
      self._message_ttl_in_ms = message_ttl_in_ms

  def connect(self):
    """This method connects to RabbitMQ, returning the connection handle.
    When the connection is established, the on_connection_open method
    will be invoked by pika.

    :rtype: pika.SelectConnection

    """
    LOGGER.info('Connecting to %s', self._url)
    return pika.SelectConnection(pika.URLParameters(self._url),
                   self.on_connection_open,
                   stop_ioloop_on_close=False)

  def on_connection_open(self, unused_connection):
    """This method is called by pika once the connection to RabbitMQ has
    been established. It passes the handle to the connection object in
    case we need it, but in this case, we'll just mark it unused.

    :type unused_connection: pika.SelectConnection

    """
    LOGGER.info('Connection opened')
    self.add_on_connection_close_callback()
    self.open_channel()

  def add_on_connection_close_callback(self):
    """This method adds an on close callback that will be invoked by pika
    when RabbitMQ closes the connection to the publisher unexpectedly.

    """
    LOGGER.info('Adding connection close callback')
    self._connection.add_on_close_callback(self.on_connection_closed)

  def on_connection_closed(self, connection, reply_code, reply_text):
    """This method is invoked by pika when the connection to RabbitMQ is
    closed unexpectedly. Since it is unexpected, we will reconnect to
    RabbitMQ if it disconnects.

    :param pika.connection.Connection connection: The closed connection obj
    :param int reply_code: The server provided reply_code if given
    :param str reply_text: The server provided reply_text if given

    """
    self._channel = None
    if self._closing:
      self._connection.ioloop.stop()
    else:
      LOGGER.warning('Connection closed, reopening in 5 seconds: (%s) %s',
               reply_code, reply_text)
      self._connection.add_timeout(5, self.reconnect)

  def reconnect(self):
    """Will be invoked by the IOLoop timer if the connection is
    closed. See the on_connection_closed method.

    """
    # This is the old connection IOLoop instance, stop its ioloop
    self._connection.ioloop.stop()

    if not self._closing:

      # Create a new connection
      self._connection = self.connect()

      # There is now a new connection, needs a new ioloop to run
      self._connection.ioloop.start()

  def open_channel(self):
    """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
    command. When RabbitMQ responds that the channel is open, the
    on_channel_open callback will be invoked by pika.

    """
    LOGGER.info('Creating a new channel')
    self._connection.channel(on_open_callback=self.on_channel_open)

  def on_channel_open(self, channel):
    """This method is invoked by pika when the channel has been opened.
    The channel object is passed in so we can make use of it.

    Since the channel is now open, we'll declare the exchange to use.

    :param pika.channel.Channel channel: The channel object

    """
    LOGGER.info('Channel opened')
    self._channel = channel
    self.add_on_channel_close_callback()
    self.setup_exchange(self._exchange_name)

  def add_on_channel_close_callback(self):
    """This method tells pika to call the on_channel_closed method if
    RabbitMQ unexpectedly closes the channel.

    """
    LOGGER.info('Adding channel close callback')
    self._channel.add_on_close_callback(self.on_channel_closed)

  def on_channel_closed(self, channel, reply_code, reply_text):
    """Invoked by pika when RabbitMQ unexpectedly closes the channel.
    Channels are usually closed if you attempt to do something that
    violates the protocol, such as re-declare an exchange or queue with
    different parameters. In this case, we'll close the connection
    to shutdown the object.

    :param pika.channel.Channel: The closed channel
    :param int reply_code: The numeric reason the channel was closed
    :param str reply_text: The text reason the channel was closed

    """
    LOGGER.warning('Channel %i was closed: (%s) %s',
             channel, reply_code, reply_text)
    self._connection.close()

  def setup_exchange(self, exchange_name):
    """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
    command. When it is complete, the on_exchange_declareok method will
    be invoked by pika.

    :param str|unicode exchange_name: The name of the exchange to declare

    """
    LOGGER.info('Declaring exchange %s', exchange_name)
    self._channel.exchange_declare(
        callback=self.on_exchange_declareok,
        exchange=exchange_name,
        exchange_type=self.EXCHANGE_TYPE,
        durable=False)

  def on_exchange_declareok(self, unused_frame):
    """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
    command.

    :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame

    """
    LOGGER.info('Exchange declared')
    self.setup_queue()

  def setup_queue(self):
    """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
    command. When it is complete, the on_queue_declareok method will
    be invoked by pika.

    :param str|unicode queue_name: The name of the queue to declare.

    """
    LOGGER.info('Declaring queue')
    self._channel.queue_declare(
        callback=self.on_queue_declareok,
        arguments={'x-message-ttl': 50000},
        exclusive=True)

  def on_queue_declareok(self, method_frame):
    """Method invoked by pika when the Queue.Declare RPC call made in
    setup_queue has completed. In this method we will bind the queue
    and exchange together with the routing key by issuing the Queue.Bind
    RPC command. When this command is complete, the on_bindok method will
    be invoked by pika.

    :param pika.frame.Method method_frame: The Queue.DeclareOk frame

    """
    self._queue_name = method_frame.method.queue
    self._channel.queue_bind(self.on_bindok, self._queue_name,
                 self._exchange_name, self._routing_key)
    LOGGER.info('Binding %s to %s with %s',
          self._exchange_name, self._queue_name, self._routing_key)

  def on_bindok(self, unused_frame):
    """Invoked by pika when the Queue.Bind method has completed. At this
    point we will start consuming messages by calling start_consuming
    which will invoke the needed RPC commands to start the process.

    :param pika.frame.Method unused_frame: The Queue.BindOk response frame

    """
    LOGGER.info('Queue bound')
    self.start_consuming()

  def start_consuming(self):
    """This method sets up the consumer by first calling
    add_on_cancel_callback so that the object is notified if RabbitMQ
    cancels the consumer. It then issues the Basic.Consume RPC command
    which returns the consumer tag that is used to uniquely identify the
    consumer with RabbitMQ. We keep the value to use it when we want to
    cancel consuming. The on_message method is passed in as a callback pika
    will invoke when a message is fully received.

    """
    LOGGER.info('Issuing consumer related RPC commands')
    self.add_on_cancel_callback()
    self._consumer_tag = self._channel.basic_consume(self.on_message,
                             self._queue_name)

  def add_on_cancel_callback(self):
    """Add a callback that will be invoked if RabbitMQ cancels the consumer
    for some reason. If RabbitMQ does cancel the consumer,
    on_consumer_cancelled will be invoked by pika.

    """
    LOGGER.info('Adding consumer cancellation callback')
    self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

  def on_consumer_cancelled(self, method_frame):
    """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
    receiving messages.

    :param pika.frame.Method method_frame: The Basic.Cancel frame

    """
    LOGGER.info('Consumer was cancelled remotely, shutting down: %r',
          method_frame)
    if self._channel:
      self._channel.close()

  def on_message(self, unused_channel, basic_deliver, properties, body):
    """Invoked by pika when a message is delivered from RabbitMQ. The
    channel is passed for your convenience. The basic_deliver object that
    is passed in carries the exchange, routing key, delivery tag and
    a redelivered flag for the message. The properties passed in is an
    instance of BasicProperties with the message properties and the body
    is the message that was sent.

    :param pika.channel.Channel unused_channel: The channel object
    :param pika.Spec.Basic.Deliver: basic_deliver method
    :param pika.Spec.BasicProperties: properties
    :param str|unicode body: The message body

    """
    LOGGER.info('Received message # %s from %s: %s',
          basic_deliver.delivery_tag, properties.app_id, body)
    self.acknowledge_message(basic_deliver.delivery_tag)

  def acknowledge_message(self, delivery_tag):
    """Acknowledge the message delivery from RabbitMQ by sending a
    Basic.Ack RPC method for the delivery tag.

    :param int delivery_tag: The delivery tag from the Basic.Deliver frame

    """
    LOGGER.info('Acknowledging message %s', delivery_tag)
    try:
      self._channel.basic_ack(delivery_tag)
    except:
      LOGGER.info('Acknowledgment requires an open channel')

  def nak_message(self, delivery_tag):
    LOGGER.info('Not acknowledging message %s', delivery_tag)
    try:
      self._channel.basic_nack(delivery_tag)
    except:
      LOGGER.info('Acknowledgment requires an open channel')

  def stop_consuming(self):
    """Tell RabbitMQ that you would like to stop consuming by sending the
    Basic.Cancel RPC command.

    """
    if self._channel:
      LOGGER.info('Sending a Basic.Cancel RPC command to RabbitMQ')
      self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

  def on_cancelok(self, unused_frame):
    """This method is invoked by pika when RabbitMQ acknowledges the
    cancellation of a consumer. At this point we will close the channel.
    This will invoke the on_channel_closed method once the channel has been
    closed, which will in-turn close the connection.

    :param pika.frame.Method unused_frame: The Basic.CancelOk frame

    """
    LOGGER.info('RabbitMQ acknowledged the cancellation of the consumer')
    self.close_channel()

  def close_channel(self):
    """Call to close the channel with RabbitMQ cleanly by issuing the
    Channel.Close RPC command.

    """
    LOGGER.info('Closing the channel')
    self._channel.close()

  def run(self):
    """Run the example consumer by connecting to RabbitMQ and then
    starting the IOLoop to block and allow the SelectConnection to operate.

    """
    self._connection = self.connect()
    try:
      self._connection.ioloop.start()
    except Exception as e:
      # if we are turning off the task, ignore exceptions from callbacks
      if not self._task_run_event.is_set():
        pass
      else:
        raise(e)

  def stop(self):
    """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
    with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
    will be invoked by pika, which will then closing the channel and
    connection. The IOLoop is started again because this method is invoked
    when CTRL-C is pressed raising a KeyboardInterrupt exception. This
    exception stops the IOLoop which needs to be running for pika to
    communicate with RabbitMQ. All of the commands issued prior to starting
    the IOLoop will be buffered but not processed.

    """
    LOGGER.info('Stopping')
    self._closing = True
    self.stop_consuming()
    self._connection.ioloop.stop()
    LOGGER.info('Stopped')

  def close_connection(self):
    """This method closes the connection to RabbitMQ."""
    LOGGER.info('Closing connection')
    self._connection.close()

  def timeout_callback_method(self, provide_callback=False):
    # This syntax is a bit strange, so I'll explain what is going on.
    #
    # I am trying to build a partial function from a method, providing a default
    # value for 'self'.  I previously wrote this code as:
    #   timeout_callback = functools.partial(self.timeout_callback_method, self=self)
    # Which was wrong.
    #
    # The correct way to turn a method into a callback
    # function, with a frozen value of 'self', is like this:
    #   timeout_callback = functools.partial(self.timeout_callback_method)
    timeout_callback = functools.partial(self.timeout_callback_method, provide_callback)
    LOGGER.info('Timout callback being registered')

    if self._task_run_event.is_set():
      self._connection.add_timeout(deadline=self.KILL_THREAD_CALLBACK_TEMPO, callback_method=timeout_callback)
    else:
      if not self._closing:
        LOGGER.info('Consuming thread is being shutdown')
        self.stop()

    if provide_callback:
      return timeout_callback

  def start_thread(self):
    """Add a thread so that the run method doesn't steal our program control."""
    self._task_run_event.set()
    self._connection = self.connect()

    def thread_runner(self):
      LOGGER.info('The Thread is Running')
      if self._task_run_event.is_set():
        self._closing = False
        self.run()
      LOGGER.info('The Thread is Dead')

    thread = Thread(target=thread_runner, args=(self,), daemon=True)
    thread.start()

  def stop_thread(self):
    self._task_run_event.clear()
    timeout_callback = functools.partial(self.timeout_callback_method, provide_callback=True)
    self._connection.add_timeout(deadline=0.01, callback_method=timeout_callback)

class PikaTopicConsumer(SimplePikaTopicConsumer):
  """This is subclass of SimplePikaTopicConsumer which extends its capabilities.
  It can de-serialize and decrypt received messages and issues those messages to
  client callback methods.  While constructing it, you provide it with a
  symmetric encrytion key, and options functions for decrypting and
  deserializing.

  It has a start_thread and stop_thread method to control the thread in which
  the rabbit consumer is running.  Without this thread, you would loss program
  control after the 'run' call.  The encryption key can be changed while the
  service is running.

  Example:

    # make a callback that will get your messages
    def on_message_callback(unused_channel, basic_deliver, properties, body):
      LOGGER.info('Received message # %s from %s: %s',
            basic_deliver.delivery_tag, properties.app_id, body)

    consumer = PikaTopicConsumer(
      amqp_url='amqp://bob:dobbs@localhost:5672/%2F',
      routing_key='pub_thread.text',
      exchange_name='sex_change',
      queue_name='g_queue',
      message_callback=on_message_callback,
      encryption_key=b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg='
    )
    consumer.start_thread()
    consumer.stop_thread()

  """
  def __init__(self,
               amqp_url,
               routing_key,
               exchange_name,
               encryption_key,
               message_callback,
               decryption_function=None,
               deserialization_function=None):
    super().__init__(
               amqp_url,
               routing_key,
               exchange_name)

    self._encryption_key  = encryption_key
    self._rabbit_user     = self.get_rabbit_user(amqp_url)
    self._rabbit_password = self.get_rabbit_password(amqp_url)
    self._message_callback = message_callback

    # saved decryption function
    self._sdf = None

    def default_decryption_function(message, encryption_key):
      return Fernet(encryption_key).decrypt(message)

    def default_deserialization_function(obj):
      return pickle.loads(obj)

    if decryption_function is None:
      self._sdf = default_decryption_function
    else:
      self._sdf = decryption_function

    self._decryption_function = \
      functools.partial(self._sdf, encryption_key=encryption_key)

    if deserialization_function is None:
      self._deserialization_function = default_deserialization_function
    else:
      self._deserialization_function = deserialization_function

  def change_encyption_key(self, encryption_key):
    """Change the encryption_key:

    Example:
      # Fernet.generate_key() <= to make a new key
      consumer.change_encyption_key(
        b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg='
      )

    Note: the new key must match the key used by the producer
    """
    self.stop_thread()
    self._decryption_function = \
        functools.partial(self._sdf,
          encryption_key=encryption_key)
    self.start_thread()

  def get_rabbit_user(self, url):
    user = url.split(':')[1][2:]
    return user

  def get_rabbit_password(self, url):
    password = url.split(':')[2].split('@')[0]
    return password

  def deserialize(self, item):
    return self._deserialization_function(item)

  def decrypt(self, item):
    return self._decryption_function(item)

  def on_message(self, unused_channel, basic_deliver, properties, xsbody):
    ignore = False
    try:
      sbody = self.decrypt(xsbody)
    except:
      sbody = xsbody
      ignore = True

    try:
      body  = self.deserialize(sbody)
    except:
      body = sbody
      ignore = True
    #  body = self.deserialize(self.decrypt(xsbody))
    if not ignore:
      self._message_callback(unused_channel, basic_deliver, properties, body)
      self.acknowledge_message(basic_deliver.delivery_tag)
    else:
      self.nak_message(basic_deliver.delivery_tag)

def pp(item):
  pprint.pprint(item)

class PID():
  def __init__(self, kp, kd, ki, i_max, i_min, dt):
    self.err   = [0, 0]
    self.int   = [0, 0]
    self.der   = 0
    self.i_max = i_max
    self.i_min = i_min
    self.kp    = kp
    self.kd    = kd
    self.ki    = ki
    self.dt    = dt

  def next(self, x):
    '''A simple PID'''
    # err[0] = ref - x
    # err[1] = err[0] from the last sample
    # int[0] = int[1] + err[0]
    # int[1] = int[0] from the last sample
    # der = err[1] + err[0]
    # dt  = sample period in sec
    # output = kp*err[0] + (ki*int[0]*dt) + (kd*der/dt)
    output      = None
    ref         = 0
    self.err[0] = ref - x
    self.int[0] = self.int[1] + self.err[0]
    self.der    = self.err[1] + self.err[0]

    self.int[0] = self.i_max if self.int[0] > self.i_max else self.int[0]
    self.int[0] = self.i_min if self.int[0] < self.i_min else self.int[0]

    output  = self.kp * self.err[0]
    output += self.ki * self.int[0] * self.dt

    if self.dt != 0:
      output += self.kd * self.der / self.dt

    self.output = output
    self.err[1] = self.err[0]
    self.int[1] = self.int[0]
    return output

  def reset(self):
    self.err = [0, 0]
    self.int = [0, 0]
    self.der = 0


class QueueToSampleTimeControl(PID):
  def __init__(self, i_max, dt):
    super().__init__(kp=0.07, kd=0.05, ki=0.4, i_max=i_max, i_min=-1 * i_max, dt=dt)
    if i_max != 0:
      self.min_tempo = 1 / i_max
    else:
      self.min_tempo = 0.000001

  def next(self, x):
    '''Invert the output of our PID -> large amounts of control need to express
       short durations in time'''
    output = super().next(x)

    # if the controller is working accelerate the wind-down of the integrator
    # (the queue can't be negative, so help it out)
    if output <= 0:
      self.int[1] /= 1.1
      self.err[1] /= 1.1
      output =  1 / self.dt

    # start with the baseline tempo
    time_recommendation = self.dt

    if output != 0:
      time_recommendation = 1 / output

    # clamps
    time_recommendation = \
      self.min_tempo if time_recommendation < self.min_tempo else time_recommendation

    time_recommendation = \
      self.dt if time_recommendation > self.dt else time_recommendation

    return time_recommendation

class SimplePikaTopicPublisher():
  '''
  This is a pika (Python-RabbitMq) message publisher heavily based on the
  asychronous example provided in the pika documentation.  It should handle
  unexpected interactions with RabbitMQ such as channel and connection closures.

  If RabbitMQ closes the connection, an object of this class should reopen it.
  (You should look at the output, as there are limited reasons why the connection
  may be closed, which usually are tied to permission related issues or socket
  timeouts.)

  Example:
    # set a callback mechanism to sample the task's input queue every 1.5 seconds
    # name the exchange in the RabbitMq server at the url to 'g_pika_producer_exchange'
    # name the RabbitMq queue on the server at the url to 'g_queue'
    # set the topic routing key to 'pub_thread.text'

    publisher = \
      SimplePikaTopicPublisher(
        amqp_url='amqp://bob:dobbs@192.168.1.69:5672/%2F?connection_attempts=3&heartbeat_interval=3600',
        publish_tempo_sec=1.5,
        exchange_name='g_pika_producer_exchange',
        routing_key='pub_thread.text',
      )

    # to start the thread so pika won't block your code:
    publisher.start_thread()

    # to actually write messages (publish) to the amqp_url:
    publish.post_fifo("Some Message")

    # to stop the thread but keep the connection
    publisher.start_thread()

    # to start the thread again
    publisher.start_thread()

    # to stop the connection and the thread
    publisher.stop()

    # to reconnect and start the thread
    publisher.start_thread()

  Notes:
    It uses delivery confirmations and illustrates one way to keep track of
    messages that have been sent and if they've been confirmed by RabbitMQ.
    This confirmation mechanism will not work if message tempo exceeds the
    publish_tempo (the messages will get through but the confirmation mechanism
    will indicate there is a problem when there isn't one.)

    If the input queue has more than one item they will all be sent out to the
    network and the queue sampler callback's frequency will temporarily
    increase to deal with queue bursting.

  '''
  EXCHANGE_TYPE             = 'topic'
  PUBLISH_FAST_INTERVAL_SEC = 0.000001  # right now
  PRODUCER_VERSION          = u'1.0'

  def __init__(self,
               amqp_url,
               routing_key,
               publish_tempo_sec,
               exchange_name):
    '''Setup the example publisher object, passing in the URL we will use
    to connect to RabbitMQ.

    :param str amqp_url: The URL for connecting to RabbitMQ

    '''
    self._channel = None
    self._connection = None

    self._acked = 0
    self._nacked = 0
    self._deliveries = []
    self._message_number = 0

    self._closing = False
    self._stopping = False
    self.connect_error = False

    self._amqp_url = amqp_url
    self._task_run_event = ThreadEvent()
    self._publish_tempo_sec = publish_tempo_sec
    self._thread_queue = ThreadQueue(maxsize=500)

    self._tempo_controller = QueueToSampleTimeControl(
      i_max=1 / self.PUBLISH_FAST_INTERVAL_SEC,
      dt = publish_tempo_sec)

    # will set the exchange, queue and routing_keys names for the RabbitMq
    # server running on amqp_url
    self._rabbit_exchange_name = exchange_name
    self._rabbit_routing_key = routing_key

  def connect(self):
    '''This method connects to RabbitMQ, returning the connection handle.
    When the connection is established, the on_connection_open method
    will be invoked by pika. If you want the reconnection to work, make
    sure you set stop_ioloop_on_close to False, which is not the default
    behavior of this adapter.

    :rtype: pika.SelectConnection

    '''
    LOGGER.info('Connecting to %s', self._amqp_url)
    return pika.SelectConnection(pika.URLParameters(self._amqp_url),
                   self.on_connection_open,
                   stop_ioloop_on_close=False)

  def on_connection_open(self, unused_connection):
    '''This method is called by pika once the connection to RabbitMQ has
    been established. It passes the handle to the connection object in
    case we need it, but in this case, we'll just mark it unused.

    :type unused_connection: pika.SelectConnection

    '''
    LOGGER.info('Connection opened')
    self.add_on_connection_close_callback()
    self.open_channel()

  def add_on_connection_close_callback(self):
    '''This method adds an on close callback that will be invoked by pika
    when RabbitMQ closes the connection to the publisher unexpectedly.

    '''
    LOGGER.info('Adding connection close callback')
    self._connection.add_on_close_callback(self.on_connection_closed)

  def on_connection_closed(self, connection, reply_code, reply_text):
    '''This method is invoked by pika when the connection to RabbitMQ is
    closed unexpectedly. Since it is unexpected, we will reconnect to
    RabbitMQ if it disconnects.

    :param pika.connection.Connection connection: The closed connection obj
    :param int reply_code: The server provided reply_code if given
    :param str reply_text: The server provided reply_text if given

    '''
    self._channel = None
    if self._closing:
      self._connection.ioloop.stop()
    else:
      LOGGER.warning('Connection closed, reopening in 5 seconds: (%s) %s',
               reply_code, reply_text)
      self._connection.add_timeout(5, self.reconnect)

  def reconnect(self):
    '''Will be invoked by the IOLoop timer if the connection is
    closed. See the on_connection_closed method.

    '''
    self._deliveries = []
    self._acked = 0
    self._nacked = 0
    self._message_number = 0

    # This is the old connection IOLoop instance, stop its ioloop
    self._connection.ioloop.stop()

    # Create a new connection
    self._connection = self.connect()

    # There is now a new connection, needs a new ioloop to run
    self._connection.ioloop.start()

  def open_channel(self):
    '''This method will open a new channel with RabbitMQ by issuing the
    Channel.Open RPC command. When RabbitMQ confirms the channel is open
    by sending the Channel.OpenOK RPC reply, the on_channel_open method
    will be invoked.

    '''
    LOGGER.info('Creating a new channel')
    self._connection.channel(on_open_callback=self.on_channel_open)

  def on_channel_open(self, channel):
    '''This method is invoked by pika when the channel has been opened.
    The channel object is passed in so we can make use of it.

    Since the channel is now open, we'll declare the exchange to use.

    :param pika.channel.Channel channel: The channel object

    '''
    LOGGER.info('Channel opened')
    self._channel = channel
    self.add_on_channel_close_callback()
    self.setup_exchange(self._rabbit_exchange_name)

  def add_on_channel_close_callback(self):
    '''This method tells pika to call the on_channel_closed method if
    RabbitMQ unexpectedly closes the channel.

    '''
    LOGGER.info('Adding channel close callback')
    self._channel.add_on_close_callback(self.on_channel_closed)

  def on_channel_closed(self, channel, reply_code, reply_text):
    '''Invoked by pika when RabbitMQ unexpectedly closes the channel.
    Channels are usually closed if you attempt to do something that
    violates the protocol, such as re-declare an exchange or queue with
    different parameters. In this case, we'll close the connection
    to shutdown the object.

    :param pika.channel.Channel: The closed channel
    :param int reply_code: The numeric reason the channel was closed
    :param str reply_text: The text reason the channel was closed

    '''
    LOGGER.warning('Channel was closed: (%s) %s', reply_code, reply_text)
    if not self._closing:
      self._connection.close()

  def setup_exchange(self, exchange_name):
    '''Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
    command. When it is complete, the on_exchange_declareok method will
    be invoked by pika.

    :param str|unicode exchange_name: The name of the exchange to declare

    '''
    LOGGER.info('Declaring exchange %s', exchange_name)
    self._channel.exchange_declare(
                     callback=self.on_exchange_declareok,
                     exchange=exchange_name,
                     exchange_type=self.EXCHANGE_TYPE,
                     durable=False)

  def on_exchange_declareok(self, unused_frame):
    '''Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
    command.

    :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame

    '''
    LOGGER.info('Exchange declared')

    self.start_publishing()


  def start_publishing(self):
    '''This method will enable delivery confirmations and schedule the
    first message to be sent to RabbitMQ

    '''
    LOGGER.info('Issuing consumer related RPC commands')
    self.enable_delivery_confirmations()
    self.schedule_next_producer_heart_beat(self._publish_tempo_sec)

  def enable_delivery_confirmations(self):
    '''Send the Confirm.Select RPC method to RabbitMQ to enable delivery
    confirmations on the channel. The only way to turn this off is to close
    the channel and create a new one.

    When the message is confirmed from RabbitMQ, the
    on_delivery_confirmation method will be invoked passing in a Basic.Ack
    or Basic.Nack method from RabbitMQ that will indicate which messages it
    is confirming or rejecting.

    '''
    LOGGER.info('Issuing Confirm.Select RPC command')
    self._channel.confirm_delivery(self.on_delivery_confirmation)

  def on_delivery_confirmation(self, method_frame):
    '''Invoked by pika when RabbitMQ responds to a Basic.Publish RPC
    command, passing in either a Basic.Ack or Basic.Nack frame with
    the delivery tag of the message that was published. The delivery tag
    is an integer counter indicating the message number that was sent
    on the channel via Basic.Publish. Here we're just doing house keeping
    to keep track of stats and remove message numbers that we expect
    a delivery confirmation of from the list used to keep track of messages
    that are pending confirmation.

    :param pika.frame.Method method_frame: Basic.Ack or Basic.Nack frame

    '''
    confirmation_type = method_frame.method.NAME.split('.')[1].lower()
    LOGGER.info('Received %s for delivery tag: %i',
          confirmation_type,
          method_frame.method.delivery_tag)
    if confirmation_type == 'ack':
      self._acked += 1
    elif confirmation_type == 'nack':
      self._nacked += 1

    item = method_frame.method.delivery_tag
    # only remove items that exist in our list (if a previous thread was
    # canceled and this one was started we would receive delivery_tags which we
    # didn't send - this could cause the remove method to crash the producer
    if item in self._deliveries:
      self._deliveries.remove(method_frame.method.delivery_tag)
      LOGGER.info('Published %i messages, %i have yet to be confirmed, '
            '%i were acked and %i were nacked',
            self._message_number, len(self._deliveries),
            self._acked, self._nacked)
    else:
      LOGGER.info('Received delivery tag for something we did not send')

  def schedule_next_producer_heart_beat(self, timeout):
    '''If we are not closing our connection to RabbitMQ, schedule another
    message to be delivered in self._publish_tempo_sec seconds.

    '''
    if self._stopping:
      return

    # Scheduling next Task queue check
    LOGGER.info('Task queue check in %0.4f seconds', timeout)
    self._connection.add_timeout(timeout, self.producer_heart_beat)

  def publish_message(self, message):
    '''If the class is not stopping, publish a message to RabbitMQ,
    appending a list of deliveries with the message number that was sent.
    This list will be used to check for delivery confirmations in the
    on_delivery_confirmations method.

    Example:
      # get the message from somewhere
      message = self._thread_queue.get()

      # user partial of this method to make a custom callback with your message as an input
      cb = functools.partial(self.publish_message, message=message)

      # then load it into a timer
      self._connection.add_timeout(self.PUBLISH_FAST_INTERVAL_SEC, cb)
    '''
    if self._stopping:
      return
    properties = pika.BasicProperties(app_id='miros-rabbitmq-publisher',
                      content_type='application/json',
                      headers={u'version': self.PRODUCER_VERSION})

    self._channel.basic_publish(self._rabbit_exchange_name, self._rabbit_routing_key,
                  message,
                  properties)

    self._message_number += 1
    self._deliveries.append(self._message_number)
    LOGGER.info('Published message # %i', self._message_number)

  def close_channel(self):
    '''Invoke this command to close the channel with RabbitMQ by sending
    the Channel.Close RPC command.'''
    LOGGER.info('Closing the channel')
    if self._channel:
      self._channel.close()

  def run(self):
    '''Run the example code by connecting and then starting the IOLoop. '''
    self._connection = self.connect()
    self._connection.ioloop.start()

  def stop(self):
    '''Stop the example by closing the channel and connection and releasing the
    thread. We set a flag here so that we stop scheduling new messages to be
    published. The IOLoop is started because this method is
    invoked by the Try/Catch below when KeyboardInterrupt is caught.
    Starting the IOLoop again will allow the publisher to cleanly
    disconnect from RabbitMQ.
    '''
    LOGGER.info('Stopping')
    self._stopping = True
    self.close_channel()
    self.close_connection()
    self._task_run_event.clear()
    self._connection.ioloop.start()
    LOGGER.info('Stopped')

  def close_connection(self):
    '''This method closes the connection to RabbitMQ.'''
    LOGGER.info('Closing connection')
    self._closing = True
    self._connection.close()

  def producer_heart_beat(self):
    '''This is the callback that is called ever publish_tempo_sec to check to
    see if something is in the thread_queue.  If there are items in this queue
    it schedules other callbacks to send out the messages, and temporarily
    increases its frequecy to deal with queue bursting.
    '''
    if self._task_run_event.is_set():
      if self._stopping:
        return
      # messages tend to bunch up, they are bursty, so speed up our
      # producer_heart_beat if there were messages in our queue
      queue_length = self._thread_queue.qsize()
      new_tempo_period_sec = self._tempo_controller.next(queue_length)
      self.schedule_next_producer_heart_beat(new_tempo_period_sec)

      # send out all messages in the queue
      if queue_length >= 1:
        for i in range(queue_length):
          message = self._thread_queue.get()
          cb = functools.partial(self.publish_message, message=message)
          self._connection.add_timeout(self.PUBLISH_FAST_INTERVAL_SEC, cb)
          LOGGER.info('Scheduling next output message in %0.6f seconds', self.PUBLISH_FAST_INTERVAL_SEC)

  def post_fifo(self, message):
    '''use this to post messages to the network'''
    self._thread_queue.put(message)

  def start_thread(self):
    '''Add a thread so that the run method doesn't steal our program control.'''
    self._task_run_event.set()
    self._stopping = False

    def thread_runner(self):
      # The run method will turn on pika's callback hell.
      # To see how this is turned off look at the producer_heart_beat
      try:
        self.run()
      except:
        self.stop_thread()
        self.connect_error = True

    thread = Thread(target=thread_runner, args=(self,), daemon=True)
    thread.start()

  def stop_thread(self):
    '''stop the thread, but keep the connection open.  To close the connection
    and stop the thread, use the 'stop' api'''
    self._task_run_event.clear()

class PikaTopicPublisher(SimplePikaTopicPublisher):
  '''This is subclass of SimplePikaTopicPublisher which extends its capabilities.

  It can serialize and encrypt messages before it transmits them.
  While constructing it, you provide it with a
  symmetric encryption key, and optional functions for encrypting and
  serializing messages.

  Example:
    publisher = \
      PikaTopicPublisher(
        amqp_url='amqp://bob:dobbs@192.168.1.69:5672/%2F?connection_attempts=3&heartbeat_interval=3600',
        routing_key='pub_thread.text',
        publish_tempo_sec=1.5,
        exchange_name='sex_change',
        encryption_key=b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg='
      )

    publisher.start_thread()
    publisher.post_fifo("Publish a Message")
    publisher.stop_thread()
  '''
  def __init__(self,
               amqp_url,
               routing_key,
               publish_tempo_sec,
               exchange_name,
               encryption_key,
               encryption_function=None,
               serialization_function=None):

    super().__init__(
               amqp_url,
               routing_key,
               publish_tempo_sec,
               exchange_name)

    self._encryption_key  = encryption_key
    self._rabbit_user     = self.get_rabbit_user(amqp_url)
    self._rabbit_password = self.get_rabbit_password(amqp_url)

    # saved encryption function
    self._sef = None

    def default_encryption_function(message, encryption_key):
      return Fernet(encryption_key).encrypt(message)

    def default_serialization_function(obj):
      return pickle.dumps(obj)

    if encryption_function is None:
      self._sef = default_encryption_function
    else:
      self._sef = encryption_function

    self._encryption_function = functools.partial(self._sef,
        encryption_key=encryption_key)

    if serialization_function is None:
      self._serialization_function = default_serialization_function
    else:
      self._serialization_function = serialization_function

  def change_encryption_key(self, encryption_key):
    self.stop_thread()
    self._encryption_function = functools.partial(self._sef, encryption_key=encryption_key)
    self.start_thread()

  def get_rabbit_user(self, url):
    user = url.split(':')[1][2:]
    return user

  def get_rabbit_password(self, url):
    password = url.split(':')[2].split('@')[0]
    return password

  def encrypt(self, item):
    return self._encryption_function(item)

  def serialize(self, item):
    return self._serialization_function(item)

  def post_fifo(self, item):
    xsitem = self.encrypt(self.serialize(item))
    super().post_fifo(xsitem)

class Attribute():
  def __init__(self):
    pass

class LocalAreaNetwork():
  '''Provides the ip_addresses of the local area network (LAN)

  Example:
    lan = LocalAreaNetwork()

    print(lan.addresses)  # => \
      ['192.168.1.66', '192.168.1.69', '192.168.1.70', '192.168.1.71', '192.168.1.75', '192.168.1.254']

    print(lan.this.address)  # => '192.168.1.75'

    print(lan.other.addresses)  # => \
      ['192.168.1.66', '192.168.1.69', '192.168.1.70', '192.168.1.71', '192.168.1.254']

    print(LocalAreaNetwork.get_working_ip_address())  # => '192.168.1.75'

  '''
  def __init__(self):
    self.this  = Attribute()
    self.other = Attribute()
    self.this.address = LocalAreaNetwork.get_working_ip_address()
    self.addresses = self.candidate_ip_addresses()
    self.other.addresses = list(set(self.addresses) - set([self.this.address]))

  @staticmethod
  def get_working_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
      s.connect(('10.255.255.255', 1))
      ip = s.getsockname()[0]
    except:
      ip = '127.0.0.1'
    finally:
      s.close()
    return ip

  def get_ipv4_network(self):
    ip_address = LocalAreaNetwork.get_working_ip_address()
    netmask    = self.get_netmask_on_this_machine()
    inet4 = ipaddress.ip_network(ip_address + '/' + netmask, strict=False)
    return inet4

  def fill_arp_table(self):
    linux_cmd = 'ping -b {}'
    inet4 = self.get_ipv4_network()

    if inet4.num_addresses <= 256:
      broadcast_address = inet4[-1]
      fcmd = linux_cmd.format(broadcast_address)
      fcmd_as_list = fcmd.split(" ")
      try:
        ps = subprocess.Popen(fcmd_as_list, stdout=open(os.devnull, "wb"))
        ps.wait(2)
      except:
        ps.kill()
    return

  def ip_addresses_on_lan(self):
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
        output = subprocess.check_output(grep_as_list, stdin=ps.stdout, timeout=0.5)
        ps.wait()
        if output is not '':
          candidates = output.decode('utf-8').split('\n')
          if len(candidates) > 0:
            break
      except:
        # our windows command did not work on Linux
        pass
    return list(filter(None, candidates))

  def get_netmask_on_this_machine(self):
    interfaces = [interface for interface in netifaces.interfaces()]
    local_netmask = None
    working_address = LocalAreaNetwork.get_working_ip_address()
    for interface in interfaces:
      interface_network_types = netifaces.ifaddresses(interface)
      if netifaces.AF_INET in interface_network_types:
        if interface_network_types[netifaces.AF_INET][0]['addr'] == working_address:
          local_netmask = interface_network_types[netifaces.AF_INET][0]['netmask']
          break
    return local_netmask

  def ip_addresses_on_this_machine(self):
    interfaces = [interface for interface in netifaces.interfaces()]
    local_ip_addresses = []
    for interface in interfaces:
      interface_network_types = netifaces.ifaddresses(interface)
      if netifaces.AF_INET in interface_network_types:
        ip_address = interface_network_types[netifaces.AF_INET][0]['addr']
        local_ip_addresses.append(ip_address)
    return local_ip_addresses

  def candidate_ip_addresses(self):
    self.fill_arp_table()
    lan_ip_addresses = []
    a = set(self.ip_addresses_on_lan())
    b = set(self.ip_addresses_on_this_machine())
    c = set([LocalAreaNetwork.get_working_ip_address()])
    candidates = list(a - b ^ c)
    inet4 = self.get_ipv4_network()
    for host in inet4.hosts():
      shost = str(host)
      if shost in candidates:
        lan_ip_addresses.append(shost)
    return lan_ip_addresses

class RabbitHelper():
  CONNECTION_ATTEMPTS    = 3
  HEARTBEAT_INTERVAL_SEC = 3600
  PORT                   = 5672

  @staticmethod
  def make_amqp_url(ip_address,
               rabbit_user,
               rabbit_password,
               rabbit_port=None,
               connection_attempts=None,
               heartbeat_interval=None):
    '''Make a RabbitMq url.

      Example:
        amqp_url = \
          RabbitHelper.make_amqp_url(
              ip_address=192.168.1.1,
              rabbit_user='bob',
              rabbit_password='dobb',
              connection_attempts='3',
              heartbeat_interval='3600')

        print(amqp_url)  # => \
          'amqp://bob:dobbs@192.168.1.1:5672/%2F?connection_attempts=3&heartbeat_interval=3600'

    '''
    if rabbit_port is None:
      rabbit_port = RabbitHelper.PORT
    if connection_attempts is None:
      connection_attempts = RabbitHelper.CONNECTION_ATTEMPTS
    if heartbeat_interval is None:
      heartbeat_interval = RabbitHelper.HEARTBEAT_INTERVAL_SEC

    amqp_url = \
      "amqp://{}:{}@{}:{}/%2F?connection_attempts={}&heartbeat_interval={}".format(
          rabbit_user,
          rabbit_password,
          ip_address,
          rabbit_port,
          connection_attempts,
          heartbeat_interval)
    return amqp_url

class RabbitScout():
  '''Scouts a list of ip_addresses or your LAN ip_addresses for RabbitMq servers running clients
  with the correction encryption_key and routing_key.

  Example:
    rs = RabbitScout(
          rabbit_user='bob',
          rabbit_password='dobbs',
          routing_key='pub_thread.text',
          exchange_name='sex_change',
          encryption_key=b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg=')

    print(rs.addresses)      # => ['192.168.1.69', '192.168.1.75']
    print(rs.this.address)   # => '192.168.1.75'
    print(rs.other.addresss) # => ['192.168.1.69']

    print(rs.urls) # => \
      [amqp://bob:dobbs@192.168.1.69:5672/%2F?connection_attempts=3&heartbeat_interval=3600',
      'amqp://bob:dobbs@192.168.1.75:5672/%2F?connection_attempts=3&heartbeat_interval=3600']

    print(rs.this.url) # => \
      'amqp://bob:dobbs@192.168.1.75:5672/%2F?connection_attempts=3&heartbeat_interval=3600'

    print(rs.other.urls) # => \
      [amqp://bob:dobbs@192.168.1.69:5672/%2F?connection_attempts=3&heartbeat_interval=3600']

  Notes:
    The RabbitScout determines is an address has a rabbitmq server with a client
    using the correct encryption_key and routing_key by starting a
    PikaTopicPublisher thread using URL which will will not try to reconnect if
    an error is detected.  It tries to establish a connection, but only waits
    the scout_timeout_sec (default of 0.3 second/address).  If the connection is
    not made the PikaTopicPublisher indicates this with a 'connect_error' flag.
    If this flag is detected the address is disqualified.

    If you notice that some of your addresses are not being picked up by the
    RabbRabbitScout increase the scout_timeout_sec parameter.  The downside of
    doing this is it will take more time to get through your list of searched
    IP addresses to find the other RabbitMq clients in the address list or on
    the LAN.

  '''

  CONNECTION_ATTEMPTS    = 3
  HEARTBEAT_INTERVAL_SEC = 3600
  PORT                   = 5672

  SCOUT_TEMPO_SEC        = 0.01
  SCOUT_TIMEOUT_SEC      = 0.4

  def __init__(self,
               rabbit_user,
               rabbit_password,
               routing_key,
               exchange_name,
               encryption_key,
               addresses=None,
               rabbit_port=None,
               connection_attempts=None,
               heartbeat_interval=None,
               scout_timeout_sec=None):

    self.this  = Attribute()
    self.other = Attribute()

    self.routing_key = routing_key
    self.exchange_name = exchange_name
    self.encryption_key = encryption_key

    if addresses is None:
      lan = LocalAreaNetwork()
      self.candidates = lan.addresses
    else:
      self.candidates = addresses

    if rabbit_port is None:
      self.rabbit_port = self.PORT

    if connection_attempts is None:
      self.connection_attempts = self.CONNECTION_ATTEMPTS

    if heartbeat_interval is None:
      self.heartbeat_interval = self.HEARTBEAT_INTERVAL_SEC

    if scout_timeout_sec is None:
      self._scout_timeout_sec = self.SCOUT_TIMEOUT_SEC

    self.rabbit_user = rabbit_user
    self.rabbit_password = rabbit_password
    self.this.address = LocalAreaNetwork.get_working_ip_address()
    self.urls, self.addresses = self.scout_candidates()
    self.this.url = self.make_amqp_url(ip_address=self.this.address)
    self.other.urls = list(set(self.urls) - set([self.this.url]))

  def possible_amqp_urls(self, connection_attempts=None, addresses=None):
    if connection_attempts is None:
      connection_attempts = connection_attempts
    if addresses is None:
      addresses = self.candidates
    amqp_urls = []
    for ip_address in addresses:
      amqp_url = self.make_amqp_url(
        rabbit_user=self.rabbit_user,
        rabbit_password=self.rabbit_password,
        ip_address=ip_address,
        connection_attempts=connection_attempts,
      )
      amqp_urls.append(amqp_url)
    return amqp_urls

  def make_amqp_url(self,
                    ip_address,
                    rabbit_user=None,
                    rabbit_password=None,
                    rabbit_port=None,
                    connection_attempts=None,
                    heartbeat_interval=None):

    if rabbit_user is None:
      rabbit_user = self.rabbit_user
    if rabbit_password is None:
      rabbit_password = self.rabbit_password
    if rabbit_port is None:
      rabbit_port = self.rabbit_port
    if connection_attempts is None:
      connection_attempts = self.connection_attempts
    if heartbeat_interval is None:
      heartbeat_interval = self.heartbeat_interval

    amqp_url = \
      RabbitHelper.make_amqp_url(
          ip_address=ip_address,
          rabbit_user=rabbit_user,
          rabbit_password=rabbit_password,
          connection_attempts=connection_attempts,
          heartbeat_interval=heartbeat_interval)
    return amqp_url

  def scout_candidates(self):
    possible_amqp_urls = self.possible_amqp_urls(connection_attempts=1)
    scouting_amqp_urls = possible_amqp_urls[:]

    for amqp_url in possible_amqp_urls:
      thread = PikaTopicPublisher(
        amqp_url=amqp_url,
        routing_key=self.routing_key,
        publish_tempo_sec=self.SCOUT_TEMPO_SEC,
        exchange_name=self.exchange_name,
        encryption_key=self.encryption_key)

      thread.start_thread()
      # send a unexpected message to make it harder to decrypt
      thread.post_fifo(uuid.uuid4().hex.upper()[0:12])
      time.sleep(self._scout_timeout_sec)
      thread.stop_thread()
      if thread.connect_error:
        scouting_amqp_urls.remove(amqp_url)

    candidate_amqp_urls = [
     re.sub(r"connection_attempts=\d+", "connection_attempts={}".format(3), candidate)
      for candidate in scouting_amqp_urls
    ]
    candidate_ip_addresses = [
        re.sub(r'.+@(.+):.+', r'\1', candidate)
        for candidate in scouting_amqp_urls
    ]
    return candidate_amqp_urls, candidate_ip_addresses

class MirosApiException(BaseException):
  pass

class MirosNets:

  SPY_ROUTING_KEY   = 'snoop.spy'
  TRACE_ROUTING_KEY = 'snoop.trace'

  MESH_EXCHANGE     = 'miros.mesh.exchange'
  SPY_EXCHANGE      = 'miros.snoop.spy.exchange'
  TRACE_EXCHANGE    = 'miros.snoop.trace.exchange'

  def __init__(self,
                miros_object,
                rabbit_user,
                rabbit_password,
                mesh_encryption_key,
                tx_routing_key,
                rx_routing_key=None,
                on_mesh_rx=None,
                on_spy_rx=None,
                on_trace_rx=None,
                spy_snoop_encryption_key=None,
                trace_snoop_encryption_key=None):

    self.name = miros_object.name

    self.this = Attribute()
    self.mesh = Attribute()

    self.snoop = Attribute()
    self.snoop.spy = Attribute()
    self.snoop.trace = Attribute()

    self.mesh.encryption_key = mesh_encryption_key
    self._rabbit_user = rabbit_user
    self._rabbit_password = rabbit_password

    if spy_snoop_encryption_key is None:
      self.snoop.spy.encryption_key = mesh_encryption_key
    else:
      self.snoop.spy.encryption_key = spy_snoop_encryption_key

    if trace_snoop_encryption_key is None:
      self.snoop.trace.encryption_key = mesh_encryption_key
    else:
      self.snoop.trace.encryption_key = trace_snoop_encryption_key

    self.mesh.tx_routing_key = tx_routing_key

    if rx_routing_key is None:
      self.mesh.rx_routing_key = tx_routing_key
    else:
      self.mesh.rx_routing_key = rx_routing_key

    self.snoop.spy.routing_key   = tx_routing_key + '.' + MirosNets.SPY_ROUTING_KEY
    self.snoop.trace.routing_key = tx_routing_key + '.' + MirosNets.TRACE_ROUTING_KEY

    self.mesh.exchange_name        = MirosNets.MESH_EXCHANGE
    self.snoop.spy.exchange_name   = MirosNets.SPY_EXCHANGE
    self.snoop.trace.exchange_name = MirosNets.TRACE_EXCHANGE

    self.mesh.on_message_callback = \
      functools.partial(MirosNets.on_mesh_message_callback,
        custom_rx_callback=on_mesh_rx)

    self.snoop.spy.on_message_callback =  \
      functools.partial(MirosNets.on_snoop_spy_message_callback,
        custom_rx_callback=on_spy_rx)

    self.snoop.trace.on_message_callback = \
      functools.partial(MirosNets.on_snoop_trace_message_callback,
        custom_rx_callback=on_trace_rx)

    def custom_serializer(obj):
      if isinstance(obj, Event):
        obj = Event.dumps(obj)
      pobj = pickle.dumps(obj)
      return pobj

    def custom_deserializer(ppobj):
      pobj = pickle.loads(ppobj)
      try:
        obj = Event.loads(pobj)
      except:
        obj = pobj

      return obj

    self.mesh.serializer = custom_serializer
    self.mesh.deserializer = custom_deserializer

    api_ok = True
    api_ok &= hasattr(miros_object.__class__, 'post_fifo')
    api_ok &= hasattr(miros_object.__class__, 'post_lifo')
    api_ok &= hasattr(miros_object.__class__, 'start_at')
    api_ok &= hasattr(miros_object.__class__, 'register_live_spy_callback')
    api_ok &= hasattr(miros_object.__class__, 'register_live_trace_callback')

    if api_ok is False:
      raise MirosApiException("miros_object {} doesn't have the required attributes".format(miros_object))

    rabbit_scout = RabbitScout(
                    rabbit_user = self._rabbit_user,
                    rabbit_password=self._rabbit_password,
                    routing_key='scouting',
                    exchange_name=self.mesh.exchange_name,
                    encryption_key=b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg=')

    self._urls = rabbit_scout.urls
    self.this.url = rabbit_scout.this.url
    self.build_mesh_network()
    self.build_snoop_networks()

    self.snoop.spy.enabled = False
    self.snoop.trace.enabled = False
    self.mesh.started = False
    self.snoop.spy.started = False
    self.snoop.trace.started = False

  def enable_snoop_spy(self):
    self.snoop.spy.enabled = True
    self.start_threads()

  def enable_snoop_trace(self):
    self.snoop.trace.enabled = True
    self.start_threads()

  def start_threads(self):

    if self.mesh.started is False:
      for producer in self.mesh.producers:
        producer.start_thread()
      self.mesh.consumer.start_thread()
      self.mesh.started = True
    time.sleep(2.0)

    if self.snoop.spy.started is False and self.snoop.spy.enabled:
      for spy_producer in self.snoop.spy.producers:
        spy_producer.start_thread()
      self.snoop.spy.consumer.start_thread()
      self.snoop.spy.enabled = True

    if self.snoop.trace.started is False and self.snoop.trace.enabled:
      for trace_producer in self.snoop.trace.producers:
        trace_producer.start_thread()
      self.snoop.trace.consumer.start_thread()
      self.snoop.trace.enabled = True

  def stop_threads(self):
    if self.mesh.started is True:
      for producer in self.mesh.producers:
        producer.stop_thread()
      self.mesh.consumer.stop_thread()
      self.mesh.started = False

    if self.snoop.spy.started is True:
      for spy_producer in self.snoop.spy.producers:
        spy_producer.stop_thread()
      self.snoop.spy.consumer.stop_thread()
      self.snoop.spy.enabled = False

    if self.snoop.trace.started is True:
      for trace_producer in self.snoop.trace.producers:
        trace_producer.stop_thread()
      self.snoop.trace.consumer.stop_thread()
      self.snoop.trace.enabled = False

  def build_mesh_network(self):
    self.mesh.producers = [
      PikaTopicPublisher(
        amqp_url=amqp_url,
        routing_key=self.mesh.tx_routing_key,
        publish_tempo_sec=0.1,
        exchange_name=self.mesh.exchange_name,
        serialization_function=self.mesh.serializer,
        encryption_key=self.mesh.encryption_key)
      for amqp_url in self._urls
    ]

    self.mesh.consumer = \
      PikaTopicConsumer(
        amqp_url=self.this.url,
        routing_key=self.mesh.rx_routing_key,
        exchange_name=self.mesh.exchange_name,
        message_callback=self.mesh.on_message_callback,
        deserialization_function=self.mesh.deserializer,
        encryption_key=self.mesh.encryption_key)

  def build_snoop_networks(self):

    self.snoop.spy.producers = [
      PikaTopicPublisher(
        amqp_url=amqp_url,
        routing_key=self.snoop.spy.routing_key,
        publish_tempo_sec=0.1,
        exchange_name=self.snoop.spy.exchange_name,
        encryption_key=self.snoop.spy.encryption_key)
      for amqp_url in self._urls
    ]

    self.snoop.spy.consumer = \
      PikaTopicConsumer(
        amqp_url=self.this.url,
        routing_key=self.snoop.spy.routing_key,
        exchange_name=self.snoop.spy.exchange_name,
        message_callback=self.snoop.spy.on_message_callback,
        encryption_key=self.snoop.spy.encryption_key)

    self.snoop.trace.producers = [
      PikaTopicPublisher(
        amqp_url=amqp_url,
        routing_key=self.snoop.trace.routing_key,
        publish_tempo_sec=0.1,
        exchange_name=self.snoop.trace.exchange_name,
        encryption_key=self.snoop.trace.encryption_key)
      for amqp_url in self._urls
    ]

    self.snoop.trace.consumer = \
      PikaTopicConsumer(
        amqp_url=self.this.url,
        routing_key=self.snoop.trace.routing_key,
        exchange_name=self.snoop.trace.exchange_name,
        message_callback=self.snoop.trace.on_message_callback,
        encryption_key=self.snoop.trace.encryption_key)

  @staticmethod
  def on_mesh_message_callback(unused_channel, basic_deliver, properties, body, custom_rx_callback=None):
    if custom_rx_callback is None:
      print("Received mesh message # {} from {}: {}".format(
            basic_deliver.delivery_tag, properties.app_id, body))
    else:
      custom_rx_callback(unused_channel, basic_deliver, properties, body)

  @staticmethod
  def on_snoop_spy_message_callback(unused_channel, basic_deliver, properties, body, custom_rx_callback=None):
    if custom_rx_callback is None:
      print("Received snoop-spy message # {} from {}: {}".format(
            basic_deliver.delivery_tag, properties.app_id, body))
    else:
      custom_rx_callback(unused_channel, basic_deliver, properties, body)

  @staticmethod
  def on_snoop_trace_message_callback(unused_channel, basic_deliver, properties, body, custom_rx_callback=None):
    if custom_rx_callback is None:
      print("Received snoop-spy message # {} from {}: {}".format(
            basic_deliver.delivery_tag, properties.app_id, body))
    else:
      custom_rx_callback(unused_channel, basic_deliver, properties, body)

  def transmit(self, event):
    for producer in self.mesh.producers:
      producer.post_fifo(event)

  def broadcast_spy(self, message):
    for producer in self.snoop.spy.producers:
      producer.post_fifo(self.name + " " + message)

  def broadcast_trace(self, message):
    for producer in self.snoop.trace.producers:
      producer.post_fifo(message)

  def change_mesh_encyption_key(self, encryption_key):
    for producer in self.mesh.producers:
      producer.change_encyption_key(encryption_key)
    self.mesh.consumer.change_encyption_key(encryption_key)

  def change_spy_encyption_key(self, encryption_key):
    for producer in self.snoop.spy.producers:
      producer.change_encyption_key(encryption_key)
    self.snoop.spy.consumer.change_encyption_key(encryption_key)

  def change_trace_encyption_key(self, encryption_key):
    for producer in self.snoop.trace.producers:
      producer.change_encyption_key(encryption_key)
    self.snoop.trace.consumer.change_encyption_key(encryption_key)

class AnsiColors:
  White = '\u001b[37;1m'
  Reset = '\u001b[0m'

class MirosNetsInterface():

  def on_network_message(self, unused_channel, basic_deliver, properties, event):
    if isinstance(event, Event):
      # print("heard {} from {}".format(event.signal_name, event.payload))
      if event.payload != self.name:
        self.post_fifo(event)
    else:
      print("rx non-event {}".format(event))

  def on_network_trace_message(self, ch, method, properties, body):
    '''create a on_network_trace_message function received messages in the queue'''
    print(" [+t] {}".format(body.replace('\n', '')))

  def on_network_spy_message(self, ch, method, properties, body):
    '''create a on_network_spy_message function received messages in the queue'''
    print(" [+s] {}".format(body))

  def transmit(self, event):
    self.nets.transmit(event)

  def enable_snoop_trace(self):
    self.live_trace = True
    self.register_live_trace_callback(self.nets.broadcast_trace)
    self.nets.enable_snoop_trace()

  def enable_snoop_spy(self):
    self.live_spy = True
    self.register_live_spy_callback(self.nets.broadcast_spy)
    self.nets.enable_snoop_spy()

  def snoop_scribble(self, message, enable_color=None):
    enable_color = True
    if not enable_color:
      named_message = "[{}] [{}] # {}".format(
          stdlib_datetime.strftime(stdlib_datetime.now(), "%Y-%m-%d %H:%M:%S.%f"),
          self.name,
          message)
    else:
      named_message = "[{}] [{}] # {}{}{}".format(
          stdlib_datetime.strftime(stdlib_datetime.now(), "%Y-%m-%d %H:%M:%S.%f"),
          self.name,
          AnsiColors.White,
          message,
          AnsiColors.Reset)
    if self.nets.snoop.trace.enabled:
      self.nets.broadcast_trace(named_message)
    elif self.nets.snoop.spy.enabled:
      self.nets.broadcast_spy(named_message)
    else:
      self.scribble(named_message)

class NetworkedActiveObject(ActiveObject, MirosNetsInterface):
  def __init__(self,
                name,
                rabbit_user,
                rabbit_password,
                mesh_encryption_key,
                tx_routing_key=None,
                rx_routing_key=None,
                spy_snoop_encryption_key=None,
                trace_snoop_encryption_key=None):
    super().__init__(name)

    on_message_callback = functools.partial(self.on_network_message)
    on_trace_message_callback = functools.partial(self.on_network_trace_message)
    on_spy_message_callback = functools.partial(self.on_network_spy_message)

    if tx_routing_key is None:
      tx_routing_key = "empty"

    if rx_routing_key is None:
      rx_routing_key = tx_routing_key

    if trace_snoop_encryption_key is None:
      trace_snoop_encryption_key = mesh_encryption_key

    if spy_snoop_encryption_key is None:
      spy_snoop_encryption_key = mesh_encryption_key

    self.nets = MirosNets(miros_object = self,
                 rabbit_user=rabbit_user,
                 rabbit_password=rabbit_password,
                 mesh_encryption_key=mesh_encryption_key,
                 trace_snoop_encryption_key=trace_snoop_encryption_key,
                 spy_snoop_encryption_key=spy_snoop_encryption_key,
                 tx_routing_key=tx_routing_key,
                 rx_routing_key=rx_routing_key,
                 on_mesh_rx=on_message_callback,
                 on_trace_rx=on_trace_message_callback,
                 on_spy_rx=on_spy_message_callback)

  def start_at(self, initial_state):
    super().start_at(initial_state)
    time.sleep(0.1)
    self.nets.start_threads()

class NetworkedFactory(Factory, MirosNetsInterface):
  def __init__(self,
                name,
                rabbit_user,
                rabbit_password,
                mesh_encryption_key,
                tx_routing_key=None,
                rx_routing_key=None,
                spy_snoop_encryption_key=None,
                trace_snoop_encryption_key=None):
    super().__init__(name)

    on_message_callback = functools.partial(self.on_network_message)
    on_trace_message_callback = functools.partial(self.on_network_trace_message)
    on_spy_message_callback = functools.partial(self.on_network_spy_message)

    if tx_routing_key is None:
      tx_routing_key = "empty"

    if rx_routing_key is None:
      rx_routing_key = tx_routing_key

    if trace_snoop_encryption_key is None:
      trace_snoop_encryption_key = mesh_encryption_key

    if spy_snoop_encryption_key is None:
      spy_snoop_encryption_key = mesh_encryption_key

    self.nets = MirosNets(miros_object = self,
                 rabbit_user=rabbit_user,
                 rabbit_password=rabbit_password,
                 mesh_encryption_key=mesh_encryption_key,
                 trace_snoop_encryption_key=trace_snoop_encryption_key,
                 spy_snoop_encryption_key=spy_snoop_encryption_key,
                 tx_routing_key=tx_routing_key,
                 rx_routing_key=rx_routing_key,
                 on_mesh_rx=on_message_callback,
                 on_trace_rx=on_trace_message_callback,
                 on_spy_rx=on_spy_message_callback)

  def start_at(self, initial_state):
    super().start_at(initial_state)
    time.sleep(0.1)
    self.nets.start_threads()

if __name__ == '__main__':

  from miros.activeobject import ActiveObject
  lan = LocalAreaNetwork()
  print(lan.this.address)
  print(lan.addresses)
  print(lan.other.addresses)
  name = uuid.uuid4().hex[0:2]
  print("I am {}".format(name))
  rn = RabbitScout(
      'bob',
      'dobbs',
      routing_key='pub_thread.text',
      exchange_name='sex_change',
      encryption_key=b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg=',
      addresses=lan.addresses,
  )
  pp(rn.urls)
  pp(rn.addresses)
  pp(rn.this.url)
  pp(rn.other.urls)

  ao = ActiveObject(name='testing')

  def custom_on_message_callback(unused_channel, basic_deliver, properties, body):
      print("Custom rx, Received mesh message # {} from {}: {}".format(basic_deliver.delivery_tag, properties.app_id, body))

  mn = MirosNets(miros_object = ao,
                  rabbit_user='bob',
                  rabbit_password='dobbs',
                  mesh_encryption_key=b'u3Uc-qAi9iiCv3fkBfRUAKrM1gH8w51-nVU8M8A73Jg=',
                  tx_routing_key="testing",
                  on_mesh_rx=custom_on_message_callback)
  pp(mn._urls)

  print("transmitting something")
  mn.start_threads()
  crash_sample_number = 100
  for i in range(100):
    mn.transmit("{} bob {}".format(name, i))
    if i != 0 and i % crash_sample_number is 0:
      mn.stop_threads()
      time.sleep(2)
    if i != 0 and i % (crash_sample_number + 1) is 0:
      mn.start_threads()
      time.sleep(2)
    time.sleep(0.5)

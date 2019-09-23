import time
import random
import logging
from threading import Event 
from threading import Thread

logging.basicConfig(
  format='%(asctime)s %(levelname)s:%(message)s',
  filename='valgrind_simple_3.log',
  level=logging.DEBUG)

def make_test_thread1(name, thread_event):
  def thread_runner(name, e):
    while e.is_set():
      if random.choice(list(['get', 'set'])) == 'get':
        logging.debug(name + str(' get'))
      else:
        logging.debug(name + str(' set'))
      time.sleep(random.uniform(0, 0.5))
  return Thread(target=thread_runner, name=name, daemon=True, args=(name, thread_event))

# begin the multithreaded tests
# make an event that can turn off all threads
event = Event()
event.set()

number_of_threads = 10

# create and start the thread
for i in range(number_of_threads):
  thread = make_test_thread1("thrd_" + "{0:02}:".format(i), event)
  thread.start()

time.sleep(3)

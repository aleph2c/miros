import os
import re
import time
import pytest
import logging
from pathlib import Path
from functools import partial
from collections import namedtuple
from contextlib import contextmanager

from miros import pp
from miros import Event
from miros import spy_on
from miros import signals
from miros import ActiveObject
from miros import return_status


dir_path = os.path.dirname(os.path.realpath(__file__))
data_path = Path(dir_path)

@contextmanager
def stripped(log_items):
  def item_without_timestamp(item):
    m = re.match(r"[0-9-:., ]+ DEBUG:S: (.+)$", item)
    if(m is not None):
      without_time_stamp = m.group(1)
    else:
      without_time_stamp = item
    return without_time_stamp

  targets = log_items
  if len(targets) > 1:
    stripped_target = []
    for target_item in targets:
      target_item = target_item.strip()
      if len(target_item) != 0:
        stripped_target_item = item_without_timestamp(target_item)
        stripped_target.append(stripped_target_item)
    yield(stripped_target)

  else:
    target = log
    yield(item_without_timestamp(target))

def get_log_as_stripped_string(path):
  result = "\n"
  with open(str((path).resolve())) as fp:
    with stripped(fp.readlines()) as spy_lines:
      for s in spy_lines:
        result += s + '\n'
  return result

@spy_on
def Start(self, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    self.scribble('Hello from \"start\"')
    self.post_fifo(Event(signal=signals.SCXML_INIT_SIGNAL))
    self.subscribe(Event(signal=signals.Whatever1))
    self.publish(Event(signal=signals.Whatever2))
    status = return_status.HANDLED
  elif(e.signal == signals.SCXML_INIT_SIGNAL):
    status = self.trans(Work)
  elif(e.signal == signals.INIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    self.temp.fun = self.top
    status = return_status.SUPER
  return status

@spy_on
def Work(self, e):
  status = return_status.UNHANDLED
  if(e.signal == signals.ENTRY_SIGNAL):
    self.scribble('Hello from \'work\'')
    status = return_status.HANDLED
  elif(e.signal == signals.INIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.SCXML_INIT_SIGNAL):
    status = return_status.HANDLED
  elif(e.signal == signals.to_start):
    status = self.trans(Start)
  elif(e.signal == signals.EXIT_SIGNAL):
    status = return_status.HANDLED
  else:
    self.temp.fun = self.top
    status = return_status.SUPER
  return status


class InstrumentedActiveObject(ActiveObject):
  def __init__(self, name, log_file):
    super().__init__(name)

    self.log_file = log_file

    logging.basicConfig(
      format='%(asctime)s %(levelname)s:%(message)s',
      filemode='w',
      filename=self.log_file,
      level=logging.DEBUG)
    self.register_live_spy_callback(partial(self.spy_callback))
    self.register_live_trace_callback(partial(self.trace_callback))

  def trace_callback(self, trace):
    '''trace without datetimestamp'''
    trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
    logging.debug("T: " + trace_without_datetime)

  def spy_callback(self, spy):
    '''spy with machine name pre-pending'''
    print(spy)
    logging.debug("S: [%s] %s" % (self.name, spy))

  def clear_log(self):
    with open(self.log_file, "w") as fp:
      fp.write("I'm writing")

class ScxmlChart(InstrumentedActiveObject):
  def __init__(self, name, log_file):
    super().__init__(name, log_file)

  def start(self):
    self.start_at(Start)

#@pytest.mark.skip()
@pytest.mark.scxml_bugs
def test_build_a_small_chart():

  log_path = str((Path(data_path) / "scxml_test_1.log").resolve())
  ao = ScxmlChart("Scxml", log_path)
  ao.live_spy = True
  ao.live_trace = False
  ao.start()
  ao.post_fifo(Event(signal=signals.anything))
  ao.post_fifo(Event(signal=signals.to_start))
  time.sleep(0.2)
  result = get_log_as_stripped_string(data_path / 'scxml_test_1.log')
  # This confirms that a statechart's threading features can be asked for before
  # the thread is turned on.  A thread is turned on after the statechart has
  # been initialized in the start_at call.  A threading feature places a request
  # into the HSM's queue so that once the first RTC process is completed, each
  # request can be dealt with.  This example calls the post_fifo, subscribe and
  # publish threading features while the statechart is initializing for the
  # first time.  The post_fifo automatically places something into the queue,
  # while the subscribe and publish requests now create a meta signal, or a
  # signal that holds another signal.  This meta signal is placed into the
  # queue.  When the thread wakes up, each of these requests are dealt with in
  # their queing order.  The calls to publish and subscribe only publish these
  # meta signals when the thread isn't started yet.  Once it is started the
  # active object makes calls to the threadig features required to satify these
  # calls, since this is a lot faster than processing the meta signal events.

  # Since the publish and subscribe features are fundamental to how a statechart
  # is structured, the meta signals are posted using the post_lifo technique.
  # This means their requests will be dealt with before any other event.  A user
  # can craft a statechart to defeat this default by using a post lifo after the
  # subscribe and publish calls have been made in the start_at initialization
  # chain.
  target = """
[Scxml] START
[Scxml] SEARCH_FOR_SUPER_SIGNAL:Start
[Scxml] ENTRY_SIGNAL:Start
[Scxml] Hello from "start"
[Scxml] POST_FIFO:SCXML_INIT_SIGNAL
[Scxml] POST_LIFO:SUBSCRIBE_META_SIGNAL
[Scxml] POST_LIFO:PUBLISH_META_SIGNAL
[Scxml] INIT_SIGNAL:Start
[Scxml] <- Queued:(3) Deferred:(0)
[Scxml] PUBLISH_META_SIGNAL:Start
[Scxml] PUBLISH:(Whatever2, PRIORITY:1000)
[Scxml] <- Queued:(2) Deferred:(0)
[Scxml] SUBSCRIBE_META_SIGNAL:Start
[Scxml] SUBSCRIBING TO:(Whatever1, TYPE:fifo)
[Scxml] <- Queued:(3) Deferred:(0)
[Scxml] SCXML_INIT_SIGNAL:Start
[Scxml] SEARCH_FOR_SUPER_SIGNAL:Work
[Scxml] SEARCH_FOR_SUPER_SIGNAL:Start
[Scxml] EXIT_SIGNAL:Start
[Scxml] ENTRY_SIGNAL:Work
[Scxml] Hello from 'work'
[Scxml] INIT_SIGNAL:Work
[Scxml] <- Queued:(2) Deferred:(0)
[Scxml] anything:Work
[Scxml] <- Queued:(1) Deferred:(0)
[Scxml] to_start:Work
[Scxml] SEARCH_FOR_SUPER_SIGNAL:Start
[Scxml] SEARCH_FOR_SUPER_SIGNAL:Work
[Scxml] EXIT_SIGNAL:Work
[Scxml] ENTRY_SIGNAL:Start
[Scxml] Hello from "start"
[Scxml] POST_FIFO:SCXML_INIT_SIGNAL
[Scxml] PUBLISH:(Whatever2, PRIORITY:1000)
[Scxml] INIT_SIGNAL:Start
[Scxml] <- Queued:(1) Deferred:(0)
[Scxml] SCXML_INIT_SIGNAL:Start
[Scxml] SEARCH_FOR_SUPER_SIGNAL:Work
[Scxml] SEARCH_FOR_SUPER_SIGNAL:Start
[Scxml] EXIT_SIGNAL:Start
[Scxml] ENTRY_SIGNAL:Work
[Scxml] Hello from 'work'
[Scxml] INIT_SIGNAL:Work
[Scxml] <- Queued:(0) Deferred:(0)
"""
  assert(result == target)
#

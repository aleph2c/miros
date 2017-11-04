import pytest
from miros.activeobject import LockingDeque
from miros.hsm import HsmWithQueues
from threading import Thread, Event
import time


@pytest.fixture
def task_setup(request):
  ld              = LockingDeque()
  event           =  Event()
  event.clear()

  def task_function(lq, shared_event):
    lq.wait()
    event.set()

  def start_thread():
    thread = Thread(target=task_function, args=(ld, event))
    thread.daemon = True  # if something goes wrong the thread should stop when the
    thread.start()
    return thread

  yield(ld, event, start_thread)
  ld.append("anything_to_stop_the_thread")


@pytest.mark.locking_deque
def test_start_stop_task(task_setup):
  # locking_deque, shared_variable, fn to start a task
  ld, event, start_thread = task_setup
  assert(event.is_set() is False)
  thread = start_thread()
  assert(thread is not None)
  time.sleep(0.01)
  # The thread should be locked on the get/wait
  assert(event.is_set() is False)
  ld.append("something_important")
  time.sleep(0.01)
  assert(event.is_set() is True)


@pytest.mark.locking_deque
def test_that_queues_match_on_append(task_setup):
  total_deque_items = 10
  # locking_deque, shared_variable, fn to start a task
  ld, event, start_thread = task_setup
  assert(event.is_set() is False)
  # get the thread, start the thread
  thread = start_thread()
  assert(thread)
  # place a bunch of things into the deque
  for i in range(0, total_deque_items):
    ld.deque.append(i)
  # confirm the thread didn't unlock
  assert(event.is_set() is False)
  # append something to unlock the thread
  ld.append("something_important")
  total_deque_items += 1
  time.sleep(0.01)
  # confirm that the thread ran
  assert(event.is_set() is True)

  # the deque should be one larger than the locking thread, since we consumed on
  # of the locking threads items
  assert(len(ld.deque) == ld.locking_queue.qsize() + 1)

  # the thread is used up, so it can't consume items.  Append a new item and
  # confirm that the size of our two queues are the same
  ld.append("something_important")
  total_deque_items += 1
  assert((len(ld.deque)) == ld.locking_queue.qsize())
  assert(len(ld.deque) == total_deque_items)


@pytest.mark.locking_deque
def test_that_queues_match_on_appendleft(task_setup):
  total_deque_items = 10
  # locking_deque, shared_variable, fn to start a task
  ld, event, start_thread = task_setup
  assert(event.is_set() is False)
  # get the thread, start the thread
  thread = start_thread()
  assert(thread)
  # place a bunch of things into the deque
  for i in range(0, total_deque_items):
    ld.deque.appendleft(i)
  # confirm the thread didn't unlock
  assert(event.is_set() is False)
  # appendleft something to unlock the thread
  ld.appendleft("something_important")
  total_deque_items += 1
  time.sleep(0.01)
  # confirm that the thread ran
  assert(event.is_set() is True)

  # the deque should be one larger than the locking thread, since we consumed on
  # of the locking threads items
  assert(len(ld.deque) == ld.locking_queue.qsize() + 1)

  # the thread is used up, so it can't consume items.  Append a new item and
  # confirm that the size of our two queues are the same
  ld.appendleft("something_important")
  total_deque_items += 1
  assert((len(ld.deque)) == ld.locking_queue.qsize())
  assert(len(ld.deque) == total_deque_items)


@pytest.mark.locking_deque
def test_that_deque_overflows_properly(task_setup):
  total_deque_items = HsmWithQueues.QUEUE_SIZE
  top_item = HsmWithQueues.QUEUE_SIZE - 1
  # locking_deque, shared_variable, fn to start a task
  ld, event, start_thread = task_setup
  thread = start_thread()
  assert(thread)
  # place a bunch of things into the deque
  for i in range(0, total_deque_items):
    ld.append(i)
  assert(len(ld.deque) == HsmWithQueues.QUEUE_SIZE)
  assert(ld.deque.popleft() == 0)
  ld.deque.appendleft(0)
  ld.append(2000)
  assert(ld.deque.popleft() == 0)
  assert(ld.deque.pop() == 2000)
  assert(ld.deque.pop() == top_item - 1)


@pytest.mark.locking_deque
def test_that_deque_can_clear_without_task(task_setup):
  total_deque_items = HsmWithQueues.QUEUE_SIZE
  ld, event, start_thread = task_setup
  # don't start our thread
  for i in range(0, total_deque_items):
    ld.append(i)
  ld.clear()
  assert(len(ld.deque) == 0)
  assert(ld.locking_queue.qsize() == 0)

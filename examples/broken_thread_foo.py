import dis
import threading
n = 0

def foo():
  global n
  n += 1

def thread_test():
  global n
  n = 0
  threads = []
  for i in range(1000):
    t = threading.Thread(target=foo)
    threads.append(t)
  return threads


print(dis.dis(foo))

for i in range(1000):
  threads = thread_test()
  # start all of the threads
  for t in threads:
    t.start()

  # wait for all of the threads
  for t in threads:
    t.join()

  print(n)

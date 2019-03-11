# to make this script work
# > pip install watchdog
# > pip install pyyaml
import os
import time
import yaml
import shutil
import subprocess
import watchdog.events
import watchdog.observers
from functools import partial
from collections import deque
from threading import Thread

with open("automakeconfig.yaml") as f:
  config = yaml.load(f)

class Handler(watchdog.events.PatternMatchingEventHandler):

  def __init__(self):
    watchdog.events.PatternMatchingEventHandler.__init__(self,
    patterns=config['change_filters'],
      ignore_directories=True, case_sensitive=False)

  def on_modified(self, event):
    def popen_thread(cmd, queue):
      proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
      out, err = proc.communicate()
      if err:
        queue.append(err)
      queue.append(out)

    def _to_system(cmd, queue):
      thread = Thread(target=popen_thread, args=(cmd, queue,))
      thread.start()
      thread.join()
      if len(queue) == 2:
        result = queue.pop()
        error = queue.pop()
        print(error)
        print(result)
      elif len(queue) == 1:
        result = queue.pop()
        print(result)
      else:
        print("the command returned with no output")

    if event.src_path.lower().endswith('.rst'):

      print(event.src_path)

      # make a function which can make a blocking call to the OS
      to_system = partial(_to_system, queue=deque(maxlen=2))

      # remove the old artifacts from this directory
      # to_system('make clean')

      # generate the api docs
      to_system('sphinx-apidoc -f -o ./../miros .')

      # make the new html
      to_system('make html')

      #if os.path.isdir('./../docs'):
      #  to_system('rm -rf ./../docs')

      to_system('rsync -a ./_build/html/ ./../docs')
      to_system('touch ./../docs/.nojekyll')
      time.sleep(2)

  on_created = on_modified


if __name__ == "__main__":
  event_handler = Handler()
  observer = watchdog.observers.Observer()
  observer.schedule(event_handler, path='.', recursive=True)
  observer.start()
  try:
    while True:
      time.sleep(2)
  except KeyboardInterrupt:
    observer.stop()
  observer.join()

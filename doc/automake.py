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

with open("automakeconfig.yaml") as f:
  config = yaml.load(f)


class Handler(watchdog.events.PatternMatchingEventHandler):

  def __init__(self):
    watchdog.events.PatternMatchingEventHandler.__init__(self,
    patterns=config['change_filters'],
      ignore_directories=True, case_sensitive=False)

  def on_modified(self, event):
    if event.src_path.lower().endswith('.rst'):
      try:
        # remove the old artifacts from this directory
        cmd = 'make clean'
        p = subprocess.Popen(cmd,
                        stdout = subprocess.PIPE,
                        stdin  = subprocess.PIPE)
        output = p.communicate()
        p.wait()
        print("{}".format(cmd))
        print(output)
        
        # make the new html
        cmd = 'make html'
        p = subprocess.Popen(cmd,
                        stdout = subprocess.PIPE,
                        stdin  = subprocess.PIPE)
        output = p.communicate()
        p.wait()
        print("{}".format(cmd))
        print(output)
        try:
          shutil.rmtree('./../docs')
        except:
          print("could not remove old docs directory")

        try:
          shutil.copytree('./_build/html/','./../docs')
        except:
          print("could not copy build results into the docs directory")

      except:
        print("Screw you human! I'm not going to change anything")

  on_created = on_modified

if __name__ == "__main__":
  event_handler = Handler()
  observer = watchdog.observers.Observer()
  observer.schedule(event_handler, path='.', recursive=True)
  observer.start()
  try:
    while True:
      time.sleep(1)

  except KeyboardInterrupt:
    observer.stop()
  observer.join()

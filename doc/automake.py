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

from pathlib import Path
from pathlib import PurePosixPath
from pathlib import PurePath

Windows_Path_To_UMLet = r'C:\Users\lincoln\Desktop\Umlet\umlet.exe'

with open("automakeconfig.yaml") as f:
  config = yaml.load(f, yaml.FullLoader)

def convert_uxf_to_other_format(filename, convertion_type):
  '''
  Uses the umlet command line to convert an umlet drawing into another format.

  Example:
    # to write './_static/n_ergotic_mongol_1.pdf'
    convert_uxf_to_other_format(
      './_static/n_ergotic_mongol_1.uxf', 'pdf')

  '''
  # umlet throws X11 java errors from Linux (hours of wasted time)
  # so I use the windows version instead
  cmd_string = \
    r"cmd.exe /C '{} -action=convert -format={} -filename={}'". \
      format(Windows_Path_To_UMLet, convertion_type, filename)

  p = subprocess.Popen(cmd_string,
                        stdout=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        shell=True)
  p.communicate()
  p.wait()
  path = PurePath.joinpath(
      PurePosixPath(os.getcwd()),
      PurePosixPath(filename))

  basename = Path(filename).resolve().stem
  basepath = str(path.parents[0])
  try:
    # old version of umlet mislabel files, here we name them what they should be
    # named
    shutil.move(
      basepath + '/' + basename + ".uxf.{}".format(convertion_type),
      basepath + '/' + basename + '.{}'.format(convertion_type)
    )
  except:
    pass

class Handler(watchdog.events.PatternMatchingEventHandler):

  def __init__(self):
    watchdog.events.PatternMatchingEventHandler.__init__(self,
    patterns=config['change_filters'],
      ignore_directories=True, case_sensitive=False)
    self.old = None  # needed to work around bug 93 of watchdog
    self.new = None  # "

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
      filename = event.src_path
      statebuf = os.stat(filename)
      self.new = statebuf.st_mtime
      if self.old is None or (self.new - self.old) > 0.5:
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
    elif event.src_path.lower().endswith('.uxf'):
      print(event.src_path)
      if event.event_type == 'modified' or event.event_type == 'created':
        convert_uxf_to_other_format(event.src_path, 'pdf')
        convert_uxf_to_other_format(event.src_path, 'svg')
        print(event.src_path, event.event_type)  # print now only for debug
      self.old = self.new
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

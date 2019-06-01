#  cmd.exe /C "C:\Users\lincoln\Desktop\Umlet\umlet.exe -action=convert -format=pdf -filename=ergotic_mongol_3.uxf" > /dev/null 2>&1

import os
import sys
import time
import shutil
import subprocess
import watchdog.events
import watchdog.observers
from pathlib import Path
from pathlib import PurePosixPath
from pathlib import PurePath

Windows_Path_To_UMLet = r'C:\Users\lincoln\Desktop\Umlet\umlet.exe'

def shell_cmd(cmd, timeout=None, output_file=None):
  if timeout is None:
    timeout = 10
    try:
      cmd_as_list = shlex.split(cmd)
      if output_file:
        output = subprocess.run(
        cmd_as_list,
        stdout=open(output_file, "w"),
        timeout=timeout,
        check=True)
      else:
        output = subprocess.run(
          cmd_as_list,
          timeout=timeout,
          check=True)
    except TimeoutExpired:
      raise
    except CalledProcessError:
      raise
  return output

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
  '''
  A watch dog which converts 'modified' and 'created' events of of '*.uxf' file
  types in a specified directory to file convertions to '.pdf' and '.svg' of the
  touched files.
  '''

  def __init__(self):
    watchdog.events.PatternMatchingEventHandler.__init__(
      self, patterns=['*.uxf'], ignore_directories=True, case_sensitive=False)

  def process(self, event):
    """
    event.event_type
        'modified' | 'created' | 'moved' | 'deleted'
    event.is_directory
        True | False
    event.src_path
        path/to/observed/file
    """
    if event.event_type == 'modified' or event.event_type == 'created':
      convert_uxf_to_other_format(event.src_path, 'pdf')
      convert_uxf_to_other_format(event.src_path, 'svg')
      print(event.src_path, event.event_type)  # print now only for debug

  def on_modified(self, event):
    self.process(event)

  def on_created(self, event):
    self.process(event)

if __name__ == '__main__':
  # The user of this command can provide a path argument
  # By default it runs in the ./static subdirectory
  args = sys.argv[1:]
  observer = watchdog.observers.Observer()
  observer.schedule(Handler(), path=args[0] if args else './_static')
  observer.start()

  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    observer.stop()

  observer.join()

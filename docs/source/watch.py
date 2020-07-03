from datetime import datetime, timedelta
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# from watchdog.events import LoggingEventHandler
# from watchdog.events import PatternMatchingEventHandler
# from watchdog.events import RegexMatchingEventHandler


class MyHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = datetime.now()

    def on_modified(self, event):
        if datetime.now() - self.last_modified < timedelta(seconds=5):
            return
        else:
            self.last_modified = datetime.now()
        print(f'Event: {event.event_type} {event.src_path}')
        # subprocess.run(['ls', '-alh'])
        subprocess.run('cd ../ && make clean && make html', shell=True)
        # os.system('cd ../ && make clean && make html')


if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()

    try:
        while observer.is_alive():
            observer.join(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

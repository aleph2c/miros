import time
import random
from collections import deque
from collections import namedtuple

from miros import Event
from miros import Factory
from miros import signals
from miros import return_status

WeatherReport = namedtuple('WeatherReport', ['latest'])

class SimpleAcyncExample(Factory):

  Name = 'weather_reader'

  def __init__(self, name=None, live_trace=None, live_spy=None):

    super().__init__(name if name != None else SimpleAcyncExample.Name)
    self.weather = []
    self.thread_safe_queue = deque(maxlen=1)

    self.live_trace = False if live_trace == None else live_trace
    self.live_spy = False if live_spy == None else live_spy

    self.watch_external_weather_api = \
      self.create(state="watch_external_weather_api"). \
        catch(signal=signals.ENTRY_SIGNAL,
          handler=self.watch_external_weather_api_entry). \
        catch(signal=signals.weather_report,
          handler=self.watch_external_weather_api_weather_report). \
        to_method()

    self.nest(self.watch_external_weather_api, parent=None)
    self.start_at(self.watch_external_weather_api)
    time.sleep(0.01)

  @staticmethod
  def watch_external_weather_api_entry(weather, e):
    status = return_status.HANDLED
    # weather is like self in a typical method
    weather.choices = ['raining', 'sunny', 'snowing']
    index_and_time_delay = random.randint(0, len(weather.choices)-1)

    # post a fake weather report 0, 1, or 2 seconds from now
    weather.post_fifo(
      Event(signal=signals.weather_report, 
        payload=
          WeatherReport(latest=weather.choices[index_and_time_delay])),
      times=1,
      period=index_and_time_delay,
      deferred=True)

    return status

  @staticmethod
  def watch_external_weather_api_weather_report(weather, e):
    status = return_status.HANDLED
    weather.thread_safe_queue.append(e.payload.latest)
    return status

  def get_weather(self):
    result = None
    if len(self.thread_safe_queue) == 0:
      raise LookupError
    else:
      result = self.thread_safe_queue.popleft()
      return result


if __name__ == '__main__':
  # create the asynchronous part of our program starts a separate thread,
  # updates itself with the weather asychronously
  tracker = SimpleAcyncExample('weather_tracker', live_trace=True)
  time.sleep(3)
  print(tracker.get_weather())



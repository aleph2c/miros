import gzip
import json
import time
import random
from pathlib import Path
from collections import namedtuple

import requests
from miros import Event
from miros import signals
from miros import Factory
from miros import return_status

Coord = namedtuple(
  'Coord',
  [
    'lon',
    'lat'
  ]
)

# uses Coord
CityDetailsPayload = namedtuple(
  'CityDetailsPayload',
  [
    'id', 
    'country',  # ISO 3166
    'city',
    'coord'  # Coord
  ]
)

RequestDetailsForCityPayload = namedtuple(
  'RequestDetailsForCityPayload',
  [
    'city',
    'country'  # ISO 3166
  ]
)

Weather = namedtuple(
  'Weather',
  [
    'icon',
    'main',
    'id',
    'description'
  ]
)

Wind = namedtuple(
  'Wind',
  [
    'speed',
    'deg',
  ]
)

# uses Weather, Coord
WeatherOpenApiResult = namedtuple(
  'WeatherOpenApiResult', 
  [
    'city',
    'country',  # ISO 3166
    'coord',    # Coord
    'wind',     # Wind
    'weather',  # Weather
    'sunrise',
    'sunset',
    'temp_min',
    'temp_max',
    'temp',
    'humidity',
    'pressure',
    'dt',
    'visibility',
    'timezone',
  ]
)

class InstrumentedFactory(Factory):
  def __init__(self, name, live_trace=None, live_spy=None):
    super().__init__(name)
    self.live_trace = False if live_trace == None else live_trace
    self.live_spy = False if live_spy == None else live_spy

class OpenWeatherMapCityDetails(InstrumentedFactory):

  DEFAULT_LOOKUP_FILE_URL = 'http://bulk.openweathermap.org/sample/city.list.json.gz'
  LOOKUP_FILE_PATH = 'city_to_id_json.gz'

  def __init__(self, name, live_trace=None, live_spy=None, lookup_file_url=None):
    '''
    To see diagram of the OpenWeatherMapCityDetails statechart:
      https://aleph2c.github.io/miros/_static/open_weather_map_city_details.pdf
    '''
    super().__init__(name, live_trace, live_spy)

    self.city = None
    self.country = None
    self.city_id = None
    self.lookup_file_url = OpenWeatherMapCityDetails.DEFAULT_LOOKUP_FILE_URL
    self.lookup_file_name = OpenWeatherMapCityDetails.LOOKUP_FILE_PATH if lookup_file_url == None else lookup_file_url

    self.api_lookup_data = self.create(state="api_lookup_data"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.api_lookup_data_entry_signal). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.api_lookup_data_init_signal). \
      catch(signal=signals.REQUEST_CITY_DETAILS,
        handler=self.api_lookup_data_request_city_details). \
      catch(signal=signals.CITY_DETAILS,
        handler=self.api_lookup_data_city_details). \
      to_method()

    self.build_data_structure = self.create(state="build_data_structure"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.build_data_structure_entry_signal). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.build_data_structure_init_signal). \
      catch(signal=signals.read_file,
        handler=self.build_data_structure_read_file). \
      catch(signal=signals.ready,
        handler=self.get_id_file_from_network_ready). \
      catch(signal=signals.retry_after_network_error,
        handler=self.get_id_file_from_network_retry_after_network_error). \
      to_method()

    self.get_id_file_from_network = self.create(state="get_id_file_from_network"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.get_id_file_from_network_entry_signal). \
      to_method()

    self.read_file = self.create(state="read_file"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.read_file_entry_signal). \
      to_method()

    self.idle = self.create(state="idle"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.idle_entry_signal). \
      catch(signal=signals.REQUEST_CITY_DETAILS,
        handler=self.idle_request_city_details). \
      to_method()

    self.conduct_query = self.create(state="conduct_query"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.conduct_query_entry_signal). \
      catch(signal=signals.ready,
        handler=self.conduct_query_ready). \
      to_method()

    self.nest(self.api_lookup_data, parent=None). \
         nest(self.build_data_structure, parent=self.api_lookup_data). \
         nest(self.get_id_file_from_network, parent=self.build_data_structure). \
         nest(self.read_file, parent=self.build_data_structure). \
         nest(self.idle, parent=self.build_data_structure). \
         nest(self.conduct_query, parent=self.build_data_structure)

    self.start_at(self.api_lookup_data)

  def city_details_payload(self):
    '''Pull the city details out of the raw_weather_lookup_dict using the
       country and city attributes to identify the required item from the
       collection

    **Returns**:
       (CityDetailsPayload): namedtuple containing the city details needed for
       the open weather API call
    '''
    result = None
    for _id, _dict in self.raw_weather_lookup_dict.items():
      if self.city == _dict['name'] and self.country == _dict['country']:
        coord = Coord(lon=_dict['coord']['lon'], lat=_dict['coord']['lon'])
        result = CityDetailsPayload(
          id=_dict['id'],
          city=self.city,
          country=self.country,
          coord=coord)
        break
    return result

  @staticmethod
  def api_lookup_data_entry_signal(chart, e):
    status = return_status.HANDLED
    chart.subscribe(Event(signal=signals.REQUEST_CITY_DETAILS))
    chart.subscribe(Event(signal=signals.CITY_DETAILS))  # debugging
    return status

  @staticmethod
  def api_lookup_data_init_signal(chart, e):
    status = chart.trans(chart.build_data_structure)
    return status

  @staticmethod
  def api_lookup_data_request_city_details(chart, e):
    status = return_status.HANDLED
    chart.defer(e)
    return status

  @staticmethod
  def api_lookup_data_city_details(chart, e):
    status = return_status.HANDLED
    print("{}: {}".format(e.payload.city, e.payload.id))
    return status

  @staticmethod
  def build_data_structure_entry_signal(chart, e):
    status = return_status.HANDLED
    this_dir = Path('.').resolve()
    chart.lookup_file_path = this_dir / chart.lookup_file_name
    return status

  @staticmethod
  def build_data_structure_init_signal(chart, e):
    if not chart.lookup_file_path.exists():
      status = chart.trans(chart.get_id_file_from_network)
    else:
      status = chart.trans(chart.read_file)
    return status

  @staticmethod
  def build_data_structure_read_file(chart, e):
    status = chart.trans(chart.read_file)
    return status

  @staticmethod
  def get_id_file_from_network_ready(chart, e):
    status = chart.trans(chart.idle)
    return status

  @staticmethod
  def get_id_file_from_network_retry_after_network_error(chart, e):
    status = chart.trans(chart.build_data_structure)
    return status

  @staticmethod
  def get_id_file_from_network_entry_signal(chart, e):
    status = return_status.HANDLED
    try:
      r = requests.get(chart.lookup_file_url)
      with open(str(chart.lookup_file_path), 'wb') as f:
        f.write(r.content)
      chart.post_fifo(Event(signal=signals.read_file))
    except:
      chart.post_fifo(
        Event(signal=signals.retry_after_network_error),
        times=1,
        period=CityWeather.NETWORK_ERROR_RETRY_TIME_IN_SEC,
        deferred=True)
    return status

  @staticmethod
  def read_file_entry_signal(chart, e):
    status = return_status.HANDLED
    raw_weather_lookup_list = []
    with gzip.open(str(chart.lookup_file_path), 'rb') as f:
      raw_weather_lookup_list = \
        json.loads(f.read().decode('utf-8'))
    chart.raw_weather_lookup_dict = {}
    chart.raw_weather_lookup_dict = \
      {node["id"] : node for node in raw_weather_lookup_list}
    chart.post_fifo(Event(signal=signals.ready))
    return status

  @staticmethod
  def idle_entry_signal(chart, e):
    status = return_status.HANDLED
    chart.recall()
    return status

  @staticmethod
  def idle_request_city_details(chart, e):
    chart.city = e.payload.city
    chart.country = e.payload.country
    status = chart.trans(chart.conduct_query)
    return status

  @staticmethod
  def conduct_query_entry_signal(chart, e):
    status = return_status.HANDLED
    payload = chart.city_details_payload()
    chart.publish(Event(signal=signals.CITY_DETAILS,
                  payload=payload))
    chart.post_fifo(Event(signal=signals.ready))
    return status

  @staticmethod
  def conduct_query_ready(chart, e):
    status = chart.trans(chart.idle)
    return status

class CityWeather(InstrumentedFactory):

  API_HOLD_OFF_TIME_IN_SEC = 10.0
  NETWORK_ERROR_RETRY_TIME_IN_SEC = 5.0

  def __init__(self,
    name,
    city,
    country,
    api_key,
    live_trace=None,
    live_spy=None):
    '''
    To see diagram of the CityWeather statechart:
      https://aleph2c.github.io/miros/_static/city_weather.pdf
    '''
    super().__init__(name, live_trace, live_spy)

    self.city = city
    self.country = country  # ISO 3166
    self.city_id = None
    self.api_key = api_key
    self.cached_payload = None

    self.weather_worker = self.create(state="weather_worker"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.weather_worker_entry_signal). \
      catch(signal=signals.GET_WEATHER,
        handler=self.weather_worker_get_weather). \
      catch(signal=signals.CITY_DETAILS,
        handler=self.weather_worker_city_details). \
      catch(signal=signals.WEATHER,
        handler=self.weather_worker_weather). \
      to_method()

    self.query_weather = self.create(state="query_weather"). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.query_weather_init_signal). \
      to_method()

    self.idle = self.create(state="idle"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.idle_entry_signal). \
      catch(signal=signals.GET_WEATHER,
        handler=self.idle_get_weather). \
      to_method()

    self.api_live = self.create(state="api_live"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.api_live_entry_signal). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.api_live_init_signal). \
      catch(signal=signals.fresh_api_call,
        handler=self.api_live_fresh_api_call). \
      catch(signal=signals.network_error,
        handler=self.api_live_network_error). \
      to_method()

    self.api_paused = self.create(state="api_paused"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.api_paused_entry). \
      catch(signal=signals.GET_WEATHER,
        handler=self.api_paused_get_weather). \
      to_method()

    self.nest(self.weather_worker, parent=None). \
      nest(self.query_weather, parent=self.weather_worker). \
      nest(self.idle, parent=self.query_weather). \
      nest(self.api_live, parent=self.query_weather). \
      nest(self.api_paused, parent=self.api_live)

    self.start_at(self.weather_worker)

  def query_api(self):
    api_query_url=self.make_url()
    result = requests.get(api_query_url)
    return result.json()

  def make_url(self):
    '''Make an Open Weather URL to request weather data this object's city and
       country

    **Note**:
       The URL request should look something like this:

       http://api.openweathermap.org/data/2.5/
         weather?id=6173331&APPID=
         b35975e18dc93725acb092f7272cc6b8&units=metric

    **Returns**:
       (str): the url which you can use with the requests library
    
    '''
    query = 'id='+str(self.city_id)

    url = 'http://api.openweathermap.org/data/2.5/weather?'
    url += query
    url += '&APPID='
    url += self.api_key
    url += '&units=metric'

    return url

  def to_weather_payload(self, weather_dict):
    '''Convert the open web api (as a dict) to the WeatherOpenApiResult.

    **Args**:
       | ``weather_dict`` (dict): dictionary version of the json structure
       |                          returned from the Open Weather Api service

    **Returns**:
       (WeatherOpenApiResult): immutable namedtuple of the data
    '''
    api = weather_dict
    api_weather_dict = api['weather'][0]

    coord = Coord(lon=api['coord']['lon'], lat=api['coord']['lat'])

    weather = Weather(
      icon=api_weather_dict['icon'],
      main=api_weather_dict['main'],
      id=api_weather_dict['id'],
      description=api_weather_dict['description']
    )

    wind = Wind(
      speed=api['wind']['speed'],
      deg=api['wind']['deg']
    )

    payload = WeatherOpenApiResult(
      city=self.city,
      country=self.country,
      coord=coord,
      wind=wind,
      weather=weather,
      sunrise=api['sys']['sunrise'],
      sunset=api['sys']['sunset'],
      temp_min=api['main']['temp_min'],
      temp_max=api['main']['temp_max'],
      temp=api['main']['temp'],
      humidity=api['main']['humidity'],
      pressure=api['main']['pressure'],
      dt=api['dt'],
      visibility=api['visibility'],
      timezone=api['timezone'],
    ) 

    return payload

  @staticmethod
  def weather_worker_entry_signal(chart, e):
    status = return_status.HANDLED
    chart.subscribe(Event(signal=signals.GET_WEATHER))
    chart.subscribe(Event(signal=signals.CITY_DETAILS))
    chart.subscribe(Event(signal=signals.WEATHER))
    chart.publish(Event(signal=signals.REQUEST_CITY_DETAILS,
      payload=RequestDetailsForCityPayload(
        city=chart.city,
        country=chart.country)))
    return status

  @staticmethod
  def weather_worker_get_weather(chart, e):
    status = return_status.HANDLED 
    chart.defer(e)
    return status

  @staticmethod
  def weather_worker_city_details(chart, e):
    status = return_status.HANDLED 
    if e.payload.city == chart.city and \
       e.payload.country == e.payload.country:
      chart.city_id = e.payload.id
      status = chart.trans(chart.query_weather)
    return status

  @staticmethod
  def weather_worker_weather(chart, e):
    status = return_status.HANDLED 
    if e.payload.city == chart.city and \
       e.payload.country == chart.country:
      pass
      #print(e.payload)
    return status

  @staticmethod
  def query_weather_init_signal(chart, e):
    status = chart.trans(chart.idle)
    return status

  @staticmethod
  def idle_entry_signal(chart, e):
    status = return_status.HANDLED
    chart.recall()
    return status

  @staticmethod
  def idle_get_weather(chart, e):
    chart.cancel_events(
      Event(signal=signals.network_error)
    )
    status = chart.trans(chart.api_live)
    return status

  @staticmethod
  def api_live_entry_signal(chart, e):
    status = return_status.HANDLED
    try:
      weather_results_dict = chart.query_api()
      chart.cached_payload = \
        chart.to_weather_payload(weather_results_dict)
      chart.publish(
        Event(
          signal=signals.WEATHER,
          payload=chart.cached_payload
        )
      )
    except:
      chart.post_lifo(Event(signal=signals.network_error))
      chart.post_fifo(
        Event(signal=signals.GET_WEATHER),
        times=1,
        period=CityWeather.NETWORK_ERROR_RETRY_TIME_IN_SEC,
        deferred=True)
    return status

  @staticmethod
  def api_live_init_signal(chart, e):
    status = chart.trans(chart.api_paused)
    return status

  @staticmethod
  def api_live_fresh_api_call(chart, e):
    status = chart.trans(chart.idle)
    return status

  @staticmethod
  def api_live_network_error(chart, e):
    status = chart.trans(chart.idle)
    return status

  @staticmethod
  def api_paused_entry(chart, e):
    status = return_status.HANDLED
    chart.post_fifo(
      Event(signal=signals.fresh_api_call),
      times=1,
      period=CityWeather.API_HOLD_OFF_TIME_IN_SEC,
      deferred=True
    )
    return status

  @staticmethod
  def api_paused_get_weather(chart, e):
    status = return_status.HANDLED
    chart.publish(
      Event(signal=signals.WEATHER, 
        payload=chart.cached_payload
      )
    )
    return status

class Sprinkler(InstrumentedFactory):

  SPRINKLER_HEART_BEAT_SEC = 5.0

  def __init__(self,
    name,
    city,
    country,
    api_key,
    water_time_sec,
    live_trace=None,
    live_spy=None):

    super().__init__(name, live_trace, live_spy)
    self.city_details = OpenWeatherMapCityDetails('city_details')
    self.city_weather = CityWeather('city_weather', city, country, api_key)

    self.city = city
    self.country = country
    self.not_raining = None
    self.water_time_sec = water_time_sec

    self.common_behaviors = self.create(state="common_behaviors"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.common_behaviors_entry_signal). \
      catch(signal=signals.heart_beat,
        handler=self.common_behaviors_heart_beat). \
      catch(signal=signals.WEATHER,
        handler=self.common_behaviors_weather). \
      catch(signal=signals.to_summer,
        handler=self.common_behaviors_to_summer). \
      to_method()

    self.summer = self.create(state="summer"). \
      catch(signal=signals.to_winter,
        handler=self.summer_to_winter). \
      catch(signal=signals.to_summer,
        handler=self.summer_to_summer). \
      catch(signal=signals.to_day,
        handler=self.summer_to_day). \
      catch(signal=signals.to_night,
        handler=self.summer_to_night). \
      to_method()

    self.night = self.create(state="night"). \
      catch(signal=signals.to_night,
        handler=self.night_to_night). \
      catch(signal=signals.to_day,
        handler=self.night_to_day). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.sprinkler_off_init_signal). \
      to_method()

    self.not_raining_state = self.create(state="not_raining_state"). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.not_raining_init_signal). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.not_raining_exit_signal). \
      to_method()

    self.sprinkler_on = self.create(state="sprinkler_on"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.sprinkler_on_entry_signal). \
      catch(signal=signals.done_watering,
        handler=self.sprinkler_on_done_watering). \
      catch(signal=signals.EXIT_SIGNAL,
        handler=self.sprinkler_on_exit_signal). \
      to_method()

    self.sprinkler_off = self.create(state="sprinkler_off"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.sprinkler_off_entry_signal). \
      to_method()

    self.nest(self.common_behaviors, parent=None). \
         nest(self.summer, parent=self.common_behaviors). \
         nest(self.night, parent=self.summer). \
         nest(self.not_raining_state, parent=self.night). \
         nest(self.sprinkler_on, parent=self.not_raining_state). \
         nest(self.sprinkler_off, parent=self.not_raining_state)

    self.start_at(self.common_behaviors)

  @staticmethod
  def common_behaviors_entry_signal(chart, e):
    status = return_status.HANDLED
    chart.subscribe(Event(signal=signals.WEATHER))
    chart.turn_off_sprinkler()
    chart.post_fifo(
      Event(signal=signals.heart_beat),
      times=0,
      period=Sprinkler.SPRINKLER_HEART_BEAT_SEC,
      deferred=True)
    return status

  @staticmethod
  def common_behaviors_heart_beat(chart, e):
    status = return_status.HANDLED
    chart.publish(Event(signal=signals.GET_WEATHER))
    return status

  @staticmethod
  def common_behaviors_weather(chart, e):
    status = return_status.HANDLED

    # https://openweathermap.org/weather-conditions
    if 500 <= e.payload.weather.id <= 531:
      chart.not_raining = False
    else:
      chart.not_raining = True

    is_winter = False
    is_winter |= 600 <= e.payload.weather.id <= 622
    is_winter |= e.payload.weather.id == 511
    is_winter |= e.payload.temp_min < 0.0
    if is_winter:
      chart.post_fifo(Event(signal=signals.to_winter))
    else:
      chart.post_fifo(Event(signal=signals.to_summer))

    if e.payload.dt > e.payload.sunset:
      chart.post_fifo(Event(signal=signals.to_night))
    else:
      chart.post_fifo(Event(signal=signals.to_day))

    return status

  @staticmethod
  def common_behaviors_to_summer(chart, e):
    status = chart.trans(chart.summer)
    return status

  @staticmethod
  def summer_to_winter(chart, e):
    status = chart.trans(chart.common_behaviors)
    return status

  @staticmethod
  def summer_to_summer(chart, e):
    status = return_status.HANDLED
    return status

  @staticmethod
  def summer_to_day(chart, e):
    status = return_status.HANDLED
    return status

  @staticmethod
  def summer_to_night(chart, e):
    status = chart.trans(chart.night)
    return status

  @staticmethod
  def night_to_night(chart, e):
    status = return_status.HANDLED
    return status

  @staticmethod
  def night_to_day(chart, e):
    status = chart.trans(chart.summer)
    return status

  @staticmethod
  def sprinkler_off_init_signal(chart, e):
    status = return_status.HANDLED
    if chart.not_raining:
      status = chart.trans(chart.not_raining_state)
    return status

  @staticmethod
  def not_raining_init_signal(chart, e):
    status = chart.trans(chart.sprinkler_on)
    return status

  def not_raining_exit_signal(chart, e):
    status = return_status.HANDLED
    chart.cancel_events(Event(signal=signals.done_watering))
    return status

  @staticmethod
  def sprinkler_on_entry_signal(chart, e):
    status = return_status.HANDLED
    chart.turn_on_sprinkler()
    chart.post_fifo(
      Event(signal=signals.done_watering),
      times=1,
      period=chart.water_time_sec,
      deferred=True)
    return status

  @staticmethod
  def sprinkler_on_done_watering(chart, e):
    status = chart.trans(chart.sprinkler_off)
    return status

  @staticmethod
  def sprinkler_on_exit_signal(chart, e):
    status = return_status.HANDLED
    chart.turn_off_sprinkler()
    return status

  @staticmethod
  def sprinkler_off_entry_signal(chart, e):
    status = return_status.HANDLED
    chart.turn_off_sprinkler()
    return status

  def turn_on_sprinkler(self):
    '''turn our sprinkler on'''
    print('turn the sprinkler on')

  def turn_off_sprinkler(self):
    '''turn our sprinkler off'''
    print('turn the sprinkler off')


if __name__ == "__main__":
  sprinkler  = Sprinkler(
    name='sprinkler',
    city='Vancouver',
    country='CA',
    api_key='b35975e18dc93725acb092f7272cc6b8',
    water_time_sec = 10,
    live_trace=True)

  time.sleep(300)


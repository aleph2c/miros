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

# uses Weather, Coord
WeatherOpenApiResult = namedtuple(
  'WeatherOpenApiResult', 
  [
    'city',
    'country',  # ISO 3166
    'coord',    # Coord
    'wind',
    'weather',  # Weather
    'sunrise',
    'sunset',
    'temp_min',
    'temp_max',
    'temp',
    'humidity',
    'dt'
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
    super().__init__(name, live_trace, live_spy)

    self.city = None
    self.country = None
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
        period=10.0,
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
    chart.publish(Event(signal=signals.CITY_DETAILS,
      payload=chart.city_details_payload()))
    chart.post_fifo(Event(signal=signals.ready))
    return status

  @staticmethod
  def conduct_query_ready(chart, e):
    status = chart.trans(chart.idle)
    return status

if __name__ == "__main__":
  owm = OpenWeatherMapCityDetails('city_details', live_trace=True)
  owm.publish(Event(signal=signals.REQUEST_CITY_DETAILS,
    payload=RequestDetailsForCityPayload(city="Vancouver", country="CA")))
  owm.publish(Event(signal=signals.REQUEST_CITY_DETAILS,
    payload=RequestDetailsForCityPayload(city="Burnaby", country="CA")))
  owm.publish(Event(signal=signals.REQUEST_CITY_DETAILS,
    payload=RequestDetailsForCityPayload(city="Toronto", country="CA")))
  owm.publish(Event(signal=signals.REQUEST_CITY_DETAILS,
    payload=RequestDetailsForCityPayload(city="Saskatoon", country="CA")))
  time.sleep(5)





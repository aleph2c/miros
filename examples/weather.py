import json
import gzip
import requests
from pathlib import Path
from collections import namedtuple

this_dir = Path('.').resolve()
weather_lookup_file = this_dir / 'city_to_id_json.gz'

if not weather_lookup_file.exists():
  id_lookup_file_url = 'http://bulk.openweathermap.org/sample/city.list.json.gz'
  r = requests.get(id_lookup_file_url)
  with open(str(weather_lookup_file), 'wb') as f:
    f.write(r.content)

raw_weather_lookup_list = None
weather_lookup_json = None
with gzip.open(str(weather_lookup_file), 'rb') as f:
  weather_lookup_json = f.read().decode('utf-8')
  raw_weather_lookup_list = json.loads(weather_lookup_json)

raw_weather_lookup_dict = {}
raw_weather_lookup_dict = {node['id'] : node for  node in raw_weather_lookup_list}

Coord = namedtuple('Coord', ['lon', 'lat'])
CityDetails = namedtuple('CityDetails', ['id', 'name', 'country', 'coord'])
'''
  {
    "id": 6173331,
    "name": "Vancouver",
    "country": "CA",
    "coord": {
      "lon": -123.119339,
      "lat": 49.24966
    }
  },
'''
def get_meta_data_for_city_and_country_code(city, country):
  result = None
  for _id, _dict in raw_weather_lookup_dict.items():
    if city == _dict['name'] and country == _dict['country']:
      coord = Coord(lon=_dict['coord']['lon'], lat=_dict['coord']['lon'])
      result = CityDetails(
        id=_dict['id'],
        name=_dict['name'],
        country=_dict['country'],
        coord=coord)
      break
  return result
      
print(get_meta_data_for_city_and_country_code('Vancouver', 'CA'))

def weather_data(query):
  res=requests.get('http://api.openweathermap.org/data/2.5/weather?'+query+'&APPID=b35975e18dc93725acb092f7272cc6b8&units=metric');
  return res.json();

def print_weather(result,city):
  print("{}'s temperature: {}°C ".format(city,result['main']['temp']))
  print("Wind speed: {} m/s".format(result['wind']['speed']))
  print("Description: {}".format(result['weather'][0]['description']))
  print("Weather: {}".format(result['weather'][0]['main']))

def main():
  city="Vancouver"
  city_to_id_dict = {}
  city_to_id_dict['Vancouver'] = 6173331
  print()
  try:
    query='id='+str(city_to_id_dict[city])
    w_data=weather_data(query);
    print_weather(w_data, city)
    print()
  except:
    print('City name not found...')
if __name__=='__main__':
  main()

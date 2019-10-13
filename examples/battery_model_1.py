import re
import time
import logging
from datetime import datetime
from functools import partial
from collections import namedtuple

import numpy as np
from miros import Event
from miros import signals
from miros import Factory
from miros import return_status
import matplotlib.pyplot as plt
from miros import ThreadSafeAttributes
from scipy.interpolate import interp1d
import numpy.polynomial.polynomial as poly

Amps = namedtuple('Amps', ['amps'])
Volts = namedtuple('Volts', ['volts'])
AmpsHours = namedtuple('AmpHours', ['amp_hours'])
AmpsAndTime = namedtuple('AmpsAndTime', ['amps', 'time'])
VoltsAndTime = namedtuple('VoltsAndTime', ['volts', 'time'])

class InstrumentedFactory(Factory):
  def __init__(self, name, log_file=None, live_trace=None, live_spy=None):
    super().__init__(name)

    self.live_trace = False if live_trace == None else live_trace
    self.live_spy = False if live_spy == None else live_spy
    self.log_file = 'battery_model.log' if log_file == None else log_file

    with open(self.log_file, "w") as fp:
      fp.write("")

    logging.basicConfig(
      format='%(asctime)s %(levelname)s:%(message)s',
      filename=self.log_file,
      level=logging.DEBUG)

    self.register_live_spy_callback(partial(self.spy_callback))
    self.register_live_trace_callback(partial(self.trace_callback))

  def trace_callback(self, trace):
    '''trace without datetimestamp'''
    trace_without_datetime = re.search(r'(\[.+\]) (\[.+\].+)', trace).group(2)
    print(trace_without_datetime)
    logging.debug("T: " + trace_without_datetime)

  def spy_callback(self, spy):
    '''spy with machine name pre-pending'''
    logging.debug("S: [{}] {}".format(self.name, spy))


class BatteryAttributes(ThreadSafeAttributes):
  _attributes = [
    'soc_per',
    'amp_hours', 
    'last_sample_time',
    'last_current_amps',
    'open_circuit_volts',
    'last_terminal_volts'
  ]

class Battery(InstrumentedFactory, BatteryAttributes):

  def __init__(self,
    name,
    initial_soc_per,
    rated_amp_hours,
    start_time=None,
    ocv_vrs_r_profile_csv=None,
    soc_vrs_ocv_profile_csv=None,
    live_trace=None,
    live_spy=None):

    '''Battery simulator

    **Note**:
       This model requires ocv_vrs_r_profile_csv and oc_vrs_ocv_profile_csv
       files.

    **Args**:
       | ``name`` (str): 
       | ``initial_soc_per`` (float): initial battery charge %
       | ``rated_amp_hours`` (float): battery's rated amps hours
       | ``start_time=None`` (datetime): starting time of simulation
       | ``ocv_vrs_r_profile_csv=None`` (str): open circuit volts vrs internal
       |                                       battery resistance
       | ``soc_vrs_ocv_profile_csv=None`` (str): state of charge % vrs
       |                                         open circuit voltage
       | ``live_trace=None``: enable live_trace feature?
       | ``live_spy=None``: enable live_spy feature?


    **Returns**:
       (Battery): 
         A battery simulator which can be fed Amps, AmpsAndTime, Volts,
         VoltsAndTime or AmpHours via the amps, amp_and_time, volts,
         volts_and_time and amp_hour signals respectively

    **Example(s)**:
      
    .. code-block:: python
       
      battery = Battery(
       rated_amp_hours=100,
       initial_soc_per=10.0,
       name="battery_example",
       soc_vrs_ocv_profile_csv='soc_ocv.csv',
       ocv_vrs_r_profile_csv='ocv_internal_resistance.csv',
       live_trace=True)

      while battery.soc_per < 80.0:
        battery.post_fifo(Event(signal=signals.amps, payload=Amps(80.0)))
        print(str(battery), end='')
        time.sleep(1)

    '''
    super().__init__(name, live_trace=live_trace, live_spy=live_spy)

    self.last_terminal_voltage = 0.0
    self.last_current_amps = 0.0
    self.soc_per = float(initial_soc_per)
    self.rated_amp_hours = float(rated_amp_hours)

    self.start_time = datetime.now() if start_time is None else start_time
    self.last_sample_time = datetime.now()

    self.ocv_vrs_r_profile_csv = 'ocv_internal_resistance.csv' if \
      ocv_vrs_r_profile_csv is None else ocv_vrs_r_profile_csv

    self.soc_vrs_ocv_profile_csv = "ocv_soc.csv" if \
      soc_vrs_ocv_profile_csv is None else soc_vrs_ocv_profile_csv

    self.build_ocv_soc_profile = self.create(state="build_ocv_soc_profile"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.build_ocv_soc_profile_entry_signal). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.build_ocv_soc_profile_init_signal). \
      to_method()

    self.volts_to_amps = self.create(state="volts_to_amps"). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.volts_to_amps_init_signal). \
      catch(signal=signals.volts,
        handler=self.volts_to_amps_volts). \
      catch(signal=signals.volts_and_time,
        handler=self.volts_to_amps_volts_and_time). \
      to_method()

    self.amps_to_amp_hours = self.create(state="amps_to_amp_hours"). \
      catch(signal=signals.INIT_SIGNAL,
        handler=self.amps_to_amp_hours_init_signal). \
      catch(signal=signals.amps,
        handler=self.amps_to_amp_hours_amps). \
      catch(signal=signals.amps_and_time,
        handler=self.amps_to_amp_hours_amps_and_time). \
      to_method()

    self.update_charge_state = self.create(state="update_charge_state"). \
      catch(signal=signals.amp_hours,
        handler=self.update_charge_state_amp_hours). \
      to_method()

    self.nest(self.build_ocv_soc_profile, parent=None). \
         nest(self.volts_to_amps, parent=self.build_ocv_soc_profile). \
         nest(self.amps_to_amp_hours, parent=self.volts_to_amps). \
         nest(self.update_charge_state, parent=self.amps_to_amp_hours)

    self.start_at(self.build_ocv_soc_profile)

  def __str__(self):
    '''Turn the battery simulator into a str to describe its characteristics.

    **Returns**:
       (str): The state of the battery simulator

    **Example(s)**:

    .. code-block:: python

       # After making a battery obj, you can see its
       # state by casting it as a str then printing that str:

       print(str(battery)) # =>
         ---
         time_s:        7.10
         term_v:     13.8614
         batt_o:      0.0140
         losses_w:   89.6000
         amps_a:     80.0000
         ocv_v:      12.7416
         soc_%:      75.1577

    '''
    return """
---
time_s:   {0:9.2f}
term_v:   {1:9.4f}
batt_o:   {2:9.4f}
losses_w: {3:9.4f}
amps_a:   {4:9.4f}
ocv_v:    {5:9.4f}
soc_%:    {6:9.4f}""".format(
      (self.last_sample_time-self.start_time).total_seconds(),
      self.last_terminal_voltage,
      self.batt_r_ohms,
      self.last_current_amps**2*self.batt_r_ohms,
      self.last_current_amps,
      self.fn_soc_to_ocv(self.soc_per),
      self.soc_per)

  def build_ocv_soc_profile_entry_signal(self, e):
    self.last_sample_time = datetime.now()
    self.fn_soc_to_ocv = self._create_soc_to_ocv_model(
      self.soc_vrs_ocv_profile_csv
    )
    self.fn_ocv_to_batt_r = self._create_ocv_to_batt_r_model(
      self.ocv_vrs_r_profile_csv
    )
    self.batt_r_ohms = self._ohms_given_soc(self.soc_per)

    return return_status.HANDLED

  def build_ocv_soc_profile_init_signal(self, e):
    status = self.trans(self.volts_to_amps)
    return status

  def volts_to_amps_init_signal(self, e):
    status = self.trans(self.amps_to_amp_hours)
    return status

  def volts_to_amps_volts(self, e):
    self.post_lifo(
      Event(
        signal=signals.volts_and_time,
        payload=VoltsAndTime(
          volts=e.payload.volts,
          time=datetime.now()
        )
      )
    )
    return return_status.HANDLED

  def volts_to_amps_volts_and_time(self, e):
    status = return_status.HANDLED
    amps = self._amps_given_terminal_volts(
      terminal_volts=e.payload.volts
    )
    self.last_terminal_voltage = e.payload.volts
    self.post_lifo(
      Event(
        signal=signals.amps_and_time,
        payload=AmpsAndTime(
          amps=amps,
          time=e.payload.time
        )
      )
    )
    return status

  def amps_to_amp_hours_init_signal(self, e):
    status = self.trans(self.update_charge_state)
    return status

  def amps_to_amp_hours_amps(self, e):
    status = return_status.HANDLED
    self.post_lifo(
      Event(
        signal=signals.amps_and_time,
        payload=AmpsAndTime(
          amps=e.payload.amps,
          time=datetime.now()
        )
      )
    )
    return status

  def amps_to_amp_hours_amps_and_time(self, e):
    status = return_status.HANDLED

    amps = e.payload.amps
    terminal_volts = amps * self.batt_r_ohms + self.open_circuit_volts

    self.last_terminal_voltage = terminal_volts
    self.last_current_amps = amps

    amp_hours = self._amp_hours_given_amps(
      amps=amps,
      time=e.payload.time
    )
    
    self.post_lifo(
      Event(
        signal=signals.amp_hours,
        payload=AmpsHours(amp_hours=amp_hours)
      )
    )
    self.last_sample_time = e.payload.time
    return status

  def update_charge_state_amp_hours(self, e):
    status = return_status.HANDLED
    self.amp_hours = \
      self.soc_per / 100.0 * self.rated_amp_hours + e.payload.amp_hours
    self.soc_per = self.amp_hours / self.rated_amp_hours * 100.0
    self.batt_r_ohms = self._ohms_given_soc(self.soc_per)
    return status

  def _amps_given_terminal_volts(self, terminal_volts):
    soc_per = self.soc_per
    voc = self.fn_soc_to_ocv(soc_per)
    v_r_volts = terminal_volts - voc
    amps = v_r_volts / self.batt_r_ohms
    return amps

  def _amp_hours_given_amps(self, amps, time):
    delta_t_sec = (time - self.last_sample_time).total_seconds()
    amp_hours = amps * delta_t_sec / 3600.0
    return amp_hours

  def _ohms_given_soc(self, soc):
    ocv = self.fn_soc_to_ocv(self.soc_per)
    batt_r_ohms = self.fn_ocv_to_batt_r(ocv)
    return batt_r_ohms

  def _create_soc_to_ocv_model(self, soc_vrs_ocv_profile_csv):
    data_ocv_soc = np.genfromtxt(
      soc_vrs_ocv_profile_csv,
      delimiter=',',
      skip_header=1,
      names=['state_of_charge', 'open_circuit_voltage'],
      dtype="float, float",
    )
    fn_soc_to_ocv = interp1d(
      data_ocv_soc['state_of_charge'],
      data_ocv_soc['open_circuit_voltage']
    )
    return fn_soc_to_ocv

  def _create_ocv_to_batt_r_model(self, soc_vrs_ocv_profile_csv):
    data_ocv_internal_resistance = np.genfromtxt(
      self.ocv_vrs_r_profile_csv,
      delimiter=',',
      skip_header=1,
      names=['open_circuit_volts', 'resistance_ohms'],
      dtype="float, float",
    )

    coefs = poly.polyfit(
      data_ocv_internal_resistance['open_circuit_volts'],
      data_ocv_internal_resistance['resistance_ohms'],
      5,
    )
    fn_ocv_to_batt_r = poly.Polynomial(coefs)
    return fn_ocv_to_batt_r


if __name__ == '__main__':

  # time 3149, 52 minutes (80 amps at 10 percent capacity)

  battery = Battery(
   rated_amp_hours=100,
   initial_soc_per=10.0,
   name="battery_example",
   soc_vrs_ocv_profile_csv='soc_ocv.csv',
   ocv_vrs_r_profile_csv='ocv_internal_resistance.csv',
   live_trace=True)

  while battery.soc_per < 80.0:
    battery.post_fifo(Event(signal=signals.amps, payload=Amps(30.0)))
    print(str(battery), end='')
    time.sleep(1)
    abs_volts = battery.last_terminal_voltage

  for i in range(3):
    battery.post_fifo(Event(signal=signals.volts, payload=Volts(abs_volts)))
    print(str(battery), end='')
    time.sleep(1)

  print("")



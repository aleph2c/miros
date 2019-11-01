import sys
import csv 
import time
import shutil
from functools import partial
from datetime import datetime
from datetime import timedelta
from collections import namedtuple

from miros import Event
from miros import signals
from miros import return_status

import numpy as np
import matplotlib.pyplot as plt

from battery_model_1 import Battery
from single_unit_three_stage_charger_3 import Charger
from single_unit_three_stage_charger_3 import Sampler
from single_unit_three_stage_charger_3 import ChargerParameters
from single_unit_three_stage_charger_3 import ElectricalInterface
from single_unit_three_stage_charger_3 import CurrentControlSystem
from single_unit_three_stage_charger_3 import VoltageControlSystem
from single_unit_three_stage_charger_3 import BatterySpecificationSettings

Seconds = namedtuple('Seconds', ['sec'])

class ChargerMock(Charger):
  def __init__(self, *args, time_compression_scalar, **kwargs):
    self.time_compression_scalar = time_compression_scalar
    super().__init__(*args, **kwargs)
    #self.stop()  # stop the parent statechart if it has been started

  def charging_entry_signal(self, e):
    status = return_status.HANDLED
    self.cancel_events(Event(signal=signals.Pulse))
    self.post_fifo(
      Event(signal=signals.Pulse),
      period=self.pulse_sec / self.time_compression_scalar,
      deferred=True,
      times=0)
    return status

# Just re-write this, we aren't trying to test it we are trying to use it to
# express our battery with the charger
class ElectricalInterfaceMock(ElectricalInterface):

  def __init__(self, time_compression_scalar, battery, name=None, live_trace=None, live_spy=None):

    self.pulse_sec = 1.0
    self.battery = battery
    self.charger_state = None

    self._last_current_amps = None
    self._last_terminal_voltage = None

    self.time_compression_scalar = time_compression_scalar

    self.test_csv_output_file = "charger_test_results.csv"
    self.fieldnames = ['time', 'current', 'voltage', 'soc', 'state']
    
    # we just want to test our graph
    if time_compression_scalar == -1:
      return

    with open(self.test_csv_output_file, mode="w") as csv_file:
      writer = csv.DictWriter(csv_file, fieldnames=self.fieldnames)
      writer.writeheader()

    super().__init__(
      name=name, 
      live_trace=live_trace,
      live_spy=live_spy,
    )

    self.respond_to_control_changes = self.create(state="respond_to_control_changes"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.respond_to_control_changes_entry_signal). \
      catch(signal=signals.Pulse2,
        handler=self.respond_to_control_changes_pulse). \
      catch(signal=signals.DRIVE_CURRENT,
        handler=self.respond_to_control_changes_drive_current). \
      catch(signal=signals.DRIVE_VOLTAGE,
        handler=self.respond_to_control_changes_drive_voltage). \
      catch(signal=signals.REQUEST_FOR_SAMPLERS,
        handler=self.respond_to_control_changes_request_for_samplers). \
      catch(signal=signals.stop,
        handler=self.respond_to_control_changes_stop). \
      to_method()

    self.drive_current_state = self.create(state="drive_current_state"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.drive_current_state_entry_signal). \
      catch(signal=signals.Tick,
        handler=self.drive_current_state_tick). \
      to_method()

    self.drive_voltage_state = self.create(state="drive_voltage_state"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.drive_voltage_state_entry_signal). \
      catch(signal=signals.Tick,
        handler=self.drive_voltage_state_tick). \
      to_method()

    self.nest(self.respond_to_control_changes, parent=None). \
      nest(self.drive_current_state, parent=self.respond_to_control_changes). \
      nest(self.drive_voltage_state, parent=self.respond_to_control_changes)

    self.start_at(self.respond_to_control_changes)

  def sample_current(self):
    self._last_current_amps = self.battery.last_current_amps
    return self._last_current_amps

  def sample_voltage(self):
    self._last_terminal_voltage = self.battery.last_terminal_voltage
    return self._last_terminal_voltage

  def respond_to_control_changes_entry_signal(self, e):
    status = return_status.HANDLED
    self.publish(
      Event(
        signal=signals.SET_CURRENT_SAMPLER,
        payload=Sampler(fn=partial(self.sample_current))
      )
    )
    self.publish(
      Event(
        signal=signals.SET_VOLTAGE_SAMPLER,
        payload=Sampler(fn=partial(self.sample_voltage))
      )
    )
    self.subscribe(Event(signal=signals.REQUEST_FOR_SAMPLERS))
    self.subscribe(Event(signal=signals.DRIVE_CURRENT))
    self.subscribe(Event(signal=signals.DRIVE_VOLTAGE))

    self.post_fifo(
      Event(signal=signals.Pulse2),
      period=self.pulse_sec / self.time_compression_scalar,
      deferred=True,
      times=0
    )
    self.real_seconds = 0
    self.fake_seconds = 0
    self.start_datetime=datetime.now()
    self.csv_file = open(self.test_csv_output_file, mode="a")
    self.writer = csv.DictWriter(self.csv_file, self.fieldnames)
    return status

  def respond_to_control_changes_pulse(self, e):
    status = return_status.HANDLED
    self.real_seconds += (self.pulse_sec / self.time_compression_scalar)
    self.fake_seconds += self.pulse_sec / 2.0
    self.post_fifo(
      Event(
        signal=signals.Tick,
        payload=Seconds(sec=self.fake_seconds)
      )
    )
    return status

  def respond_to_control_changes_drive_current(self, e):
    self._driving_terminal_volts = None
    self._driving_terminal_amps = e.payload.amps
    self.charger_state = e.payload.cause
    status = self.trans(self.drive_current_state)
    return status

  def respond_to_control_changes_drive_voltage(self, e):
    self._driving_terminal_volts = e.payload.volts
    self._driving_terminal_amps = None
    self.charger_state = e.payload.cause
    status = self.trans(self.drive_voltage_state)
    return status

  def respond_to_control_changes_request_for_samplers(self, e):
    status = return_status.HANDLED
    self.trans(self.respond_to_control_changes)
    return status

  def respond_to_control_changes_stop(self, e):
    status = return_status.HANDLED
    self.csv_file.close()
    self.stop()
    return status

  def drive_current_state_entry_signal(self, e):
    status = return_status.HANDLED
    fake_seconds_since_start = self.fake_seconds + 0.5
    new_datetime = self.start_datetime + timedelta(seconds=fake_seconds_since_start)

    self.battery.amps_through_terminals(
      self._driving_terminal_amps,
      sample_time=new_datetime
    )
    return status

  def drive_current_state_tick(self, e):
    status = return_status.HANDLED
    new_datetime = self.start_datetime + timedelta(seconds=e.payload.sec)

    self.battery.amps_through_terminals(
      self._driving_terminal_amps,
      sample_time=new_datetime
    )
    print(self.charger_state)
    if self._last_current_amps and self._last_terminal_voltage:
      print('a ', self._last_current_amps)
      print('v ', self._last_terminal_voltage)

      self.writer.writerow(
        {'time':new_datetime,
         'current':self._last_current_amps,
         'voltage':self._last_terminal_voltage,
         'soc':self.battery.soc_per,
         'state':self.charger_state}
      )
    return status

  def drive_voltage_state_entry_signal(self, e):
    status = return_status.HANDLED
    fake_seconds_since_start = self.fake_seconds + 0.5
    new_datetime = self.start_datetime + timedelta(seconds=fake_seconds_since_start)
    self.battery.volts_across_terminals(
      self._driving_terminal_volts,
      sample_time=new_datetime
    )
    print(self.charger_state)
    print('a ', self.battery.last_current_amps)
    print('v ', self.battery.last_terminal_voltage)
    return status

  def drive_voltage_state_tick(self, e):
    status = return_status.HANDLED
    new_datetime = self.start_datetime + timedelta(seconds=e.payload.sec)

    self.battery.volts_across_terminals(
      self._driving_terminal_volts,
      sample_time=new_datetime
    )
    print(self.charger_state)
    print('a ', self._last_current_amps)
    print('v ', self._last_terminal_voltage)
    self.writer.writerow(
      {'time':new_datetime,
       'current':self._last_current_amps,
       'voltage':self._last_terminal_voltage,
       'soc':self.battery.soc_per,
       'state':self.charger_state}
    )
    return status

class ChargerTester:

  def __init__(self, 
    charger_bulk_timeout_sec,
    charger_abs_timeout_sec,
    charger_equ_timeout_sec,
    charger_bulk_entry_volts,
    charger_bulk_exit_volts,
    charger_abs_exit_amps,
    charger_bulk_ref_amps,
    charger_float_ref_volts,
    charger_abs_ref_volts,
    charger_equ_ref_volts,
    battery_rated_amp_hours,
    battery_initial_soc_per,
    battery_soc_vrs_ocv_profile_csv,
    battery_ocv_vrs_r_profile_csv,
    time_compression_scalar):

    self.time_compression_scalar = time_compression_scalar

    # current control system
    ccs = CurrentControlSystem(
      reference=50.0,  # 50 amps
      kp=0.5,
      ki=0.03,
      kd=0.04
    )

    # voltage control system
    vcs = VoltageControlSystem(
      reference=12.0, # 12 volts
      kp=0.4,
      ki=0.02,
      kd=0.005
    )

    # build up the charger's battery specification
    self.charger_battery_spec =  BatterySpecificationSettings(
      bulk_timeout_sec=charger_bulk_timeout_sec,
      abs_timeout_sec=charger_abs_timeout_sec,
      equ_timeout_sec=charger_equ_timeout_sec,
      bulk_entry_volts=charger_bulk_entry_volts,
      bulk_exit_volts=charger_bulk_exit_volts,
      abs_exit_amps=charger_abs_exit_amps,
      bulk_ref_amps=charger_bulk_ref_amps,
      float_ref_volts=charger_float_ref_volts,
      abs_ref_volts=charger_abs_ref_volts,
      equ_ref_volts=charger_equ_ref_volts
    )

    # merge the control systems and the battery specification
    charger_params = ChargerParameters(
      c_control=ccs,
      v_control=vcs,
      battery_spec=self.charger_battery_spec
    )

    # hack the pulse of the charger and start it up
    self.charger = ChargerMock(
      name="charger_under_test",
      charger_params=charger_params,
      time_compression_scalar=time_compression_scalar,
      live_spy=True,
      live_trace=True
    )

    # make a battery simulator and start it up
    self.battery = Battery(
      rated_amp_hours=battery_rated_amp_hours,
      initial_soc_per=battery_initial_soc_per,
      name="lead_acid_battery_{}Ah".format(battery_rated_amp_hours),
      soc_vrs_ocv_profile_csv=battery_soc_vrs_ocv_profile_csv,
      ocv_vrs_r_profile_csv=battery_ocv_vrs_r_profile_csv,
      live_trace=True,
      live_spy=True
    )
    
    # create an electrical interface mock that will be tied
    # to the battery simulator
    self.electrical_interface = ElectricalInterfaceMock(
      name="interface_mock",
      battery=self.battery,
      time_compression_scalar=time_compression_scalar,
      live_trace=True,
      live_spy=True
    )
    self.charger.post_fifo(Event(signal=signals.Force_Bulk))

  def plot_profile(self, csv_file_to_graph=None):

    colors = {
      'voltage_color' : 'tab:blue',
      'current_color' : 'tab:red',
      'state_color':    'tab:orange',
      'text':           'tab:orange',
      'time_bar':       'tab:cyan',
    }

    if csv_file_to_graph is None:
      csv_file_to_graph = self.electrical_interface.test_csv_output_file

    to_datetime = lambda x: \
      datetime.strptime(x.decode('utf-8'), "%Y-%m-%d %H:%M:%S.%f")

    # genfromtxt is garbage, find a better api for future projects
    data = np.genfromtxt(
      self.electrical_interface.test_csv_output_file,
      delimiter=',',
      skip_header=1,
      names=self.electrical_interface.fieldnames,
      dtype="|S27, float, float, float, |S10"
    )

    time_list_datetime = [to_datetime(string) for string in data['time'].tolist()]
    time_list = [(d - time_list_datetime[0]).total_seconds() for i, d in enumerate(time_list_datetime)]
    max_current_height = max(data['current'])*1.10
    max_voltage_height = max(data['voltage'])
    min_voltage_height = min(data['voltage'])
    max_time_sec = time_list[-1]

    fig, ax1 = plt.subplots()
    ax1.set_ylim([0, max_current_height])
    ax1.set_xlabel("time (sec)")
    ax1.set_ylabel("Current (amps)")
    alh = ax1.plot(time_list, data['current'], color=colors['current_color'], label="current")
    ax2 = ax1.twinx()
    blh = ax2.plot(time_list, data['voltage'], color=colors['voltage_color'], label="voltage")
    ax2.set_ylabel("Voltage (volts)")
    ax2.tick_params(axis='y', labelcolor=colors['voltage_color'])
    state_transition_times = [
      (d[0],data[i+1][4].decode('utf-8')) for i, d in enumerate(data) if \
       i+1 < len(data) and data[i][4] != data[i+1][4]
    ]

    state_transition_times = [(data[0][0], data[0][-1].decode('utf-8'))] + state_transition_times
    state_text_height = min_voltage_height + (max_voltage_height - min_voltage_height)/ 2.0
    for transition_time, state_name in state_transition_times:
      transition_time_in_sec = (to_datetime(transition_time) -
          time_list_datetime[0]).total_seconds()
      clh = ax2.plot(
        [transition_time_in_sec, transition_time_in_sec],
        [min_voltage_height, max_voltage_height],
        color=colors['state_color'],
        label="transition"
      )
      ax2.text(
        transition_time_in_sec+30.0,
        state_text_height,
        state_name,
        color=colors['text'])
      if state_name == 'bulk':
        bulk_transition_time = transition_time_in_sec
        bulk_time_bar = self.charger_battery_spec.bulk_timeout_sec
      elif state_name == 'absorption':
        abs_transition_time = transition_time_in_sec
        abs_time_bar = abs_transition_time + self.charger_battery_spec.abs_timeout_sec
      elif state_name == 'float':
        float_transition_time = transition_time_in_sec

    def draw_timeout_bar(vertical_time_bar):
      vertical_time_bar_height = min_voltage_height + (max_voltage_height-min_voltage_height)/5
      if vertical_time_bar <= max_time_sec:
        dlh = ax2.plot(
          [vertical_time_bar, vertical_time_bar],
          [min_voltage_height, vertical_time_bar_height],
          color=colors['time_bar'],
          linewidth=4.0,
          label="timeout"
        )
      return dlh

    dlh = draw_timeout_bar(bulk_time_bar)
    dlh = draw_timeout_bar(abs_time_bar)

    lhs = alh + blh + clh + dlh
    labs = [l.get_label() for l in lhs]
    ax2.legend(lhs, labs, loc=1)
    plt.show()
    plt.savefig('./../doc/_static/charger_test_results.svg')
    plt.savefig('./../doc/_static/charger_test_results.pdf')


if __name__ == '__main__':

  copy_csv_to_bak = True
  test_with_simulator = False

  if test_with_simulator:
    time_compression_scalar = 30
    simulated_duration_in_hours = 1.0
    fake_sec = simulated_duration_in_hours * 3600.0
    real_delay_needed_sec = fake_sec / time_compression_scalar
  else:
    time_compression_scalar = -1 
    real_delay_needed_sec = 1

  ct = ChargerTester(
    charger_bulk_timeout_sec=1600,
    charger_abs_timeout_sec=1300,
    charger_equ_timeout_sec=86400,
    charger_bulk_entry_volts=12.0,
    charger_bulk_exit_volts=13.04,
    charger_abs_exit_amps=20.0,
    charger_bulk_ref_amps=30,
    charger_float_ref_volts=12.9,
    charger_abs_ref_volts=13.04,
    charger_equ_ref_volts=16.0,
    battery_rated_amp_hours=100,
    battery_initial_soc_per=65.0,
    battery_soc_vrs_ocv_profile_csv='soc_ocv.csv',
    battery_ocv_vrs_r_profile_csv='ocv_internal_resistance.csv',
    time_compression_scalar=time_compression_scalar
  )

  time.sleep(real_delay_needed_sec)

  if test_with_simulator:
    ct.electrical_interface.post_lifo(Event(signal=signals.stop))
    if copy_csv_to_bak:
      shutil.copy(
        ct.electrical_interface.test_csv_output_file,
        ct.electrical_interface.test_csv_output_file + '.bak'
      )
    ct.plot_profile()

  else:
    ct.plot_profile(
      csv_file_to_graph=ct.electrical_interface.test_csv_output_file + '.bak'
    )
  time.sleep(1)


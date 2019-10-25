import re
import time
import logging
from functools import partial
from datetime import datetime
from datetime import timedelta
from collections import namedtuple

from miros import Event
from miros import signals
from miros import Factory
from miros import return_status

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

    self.battery = battery
    self.time_compression_scalar = time_compression_scalar
    self.pulse_sec = 1.0
    self.charger_state = None

    super().__init__(
      name=name, 
      live_trace=live_trace,
      live_spy=live_spy,
    )
    #self.stop()  # stop the parent statechart if it has been started

    self.respond_to_control_changes = self.create(state="respond_to_control_changes"). \
      catch(signal=signals.ENTRY_SIGNAL,
        handler=self.respond_to_control_changes_entry_signal). \
      catch(signal=signals.Pulse,
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
    return self.battery.last_current_amps

  def sample_voltage(self):
    return self.battery.last_terminal_voltage

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
      Event(signal=signals.Pulse),
      period=self.pulse_sec / self.time_compression_scalar,
      deferred=True,
      times=0
    )

    self.real_seconds = 0
    self.fake_seconds = 0
    self.start_datetime=datetime.now()
    return status

  def respond_to_control_changes_pulse(self, e):
    status = return_status.HANDLED
    self.real_seconds += self.pulse_sec / self.time_compression_scalar
    self.fake_seconds += self.pulse_sec
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
    self.charger_state = e.payload.state
    status = self.trans(self.drive_current_state)
    return status

  def respond_to_control_changes_drive_voltage(self, e):
    self._driving_terminal_volts = e.payload.volts
    self._driving_terminal_amps = None
    self.self.charger_state = e.payload.state
    status = self.trans(self.drive_voltage_state)
    return status

  def respond_to_control_changes_request_for_samplers(self, e):
    status = return_status.HANDLED
    self.trans(self.respond_to_control_changes)
    return status

  def respond_to_control_changes_stop(self, e):
    status = return_status.HANDLED
    self.stop()
    return status

  def drive_current_state_entry_signal(self, e):
    status = return_status.HANDLED
    _datetime = datetime.now()
    real_seconds_since_start = (_datetime - self.start_datetime).total_seconds()
    fake_seconds_since_start = real_seconds_since_start * self.time_compression_scalar
    new_datetime = self.start_datetime + timedelta(seconds=fake_seconds_since_start)

    self.battery.amps_through_terminals(
      self._driving_terminal_amps,
      sample_time=new_datetime
    )
    # TODO: write data
    print(self.charger_state)
    print('a ', self.battery.last_current_amps)
    print('v ', self.battery.last_terminal_voltage)
    return status

  def drive_current_state_tick(self, e):
    status = return_status.HANDLED
    new_datetime = self.start_datetime + timedelta(seconds=e.payload.sec)

    self.battery.amps_through_terminals(
      self._driving_terminal_amps,
      sample_time=new_datetime
    )
    # TODO: write data
    print(self.charger_state)
    print('a ', self.battery.last_current_amps)
    print('v ', self.battery.last_terminal_voltage)
    return status

  def drive_voltage_state_entry_signal(self, e):
    status = return_status.HANDLED
    _datetime = datetime.now()
    real_seconds_since_start = (_datetime - self.start_datetime).total_seconds()
    fake_seconds_since_start = real_seconds_since_start * self.time_compression_scalar
    new_datetime = self.start_datetime + timedelta(seconds=fake_seconds_since_start)
    self.battery.volts_across_terminals(
      self._driving_terminal_volts,
      sample_time=new_datetime
    )
    # TODO: write data
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
    # TODO: write data
    print(self.charger_state)
    print('a ', self.battery.last_current_amps)
    print('v ', self.battery.last_terminal_voltage)
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
    battery_spec = BatterySpecificationSettings(
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
      battery_spec=battery_spec
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


if __name__ == '__main__':

  ct = ChargerTester(
    charger_bulk_timeout_sec=700,
    charger_abs_timeout_sec=900,
    charger_equ_timeout_sec=86400,
    charger_bulk_entry_volts=18.0,
    charger_bulk_exit_volts=28.0,
    charger_abs_exit_amps=12,
    charger_bulk_ref_amps=240,
    charger_float_ref_volts=24.0,
    charger_abs_ref_volts=28.0,
    charger_equ_ref_volts=30.0,
    battery_rated_amp_hours=100,
    battery_initial_soc_per=10.0,
    battery_soc_vrs_ocv_profile_csv='soc_ocv.csv',
    battery_ocv_vrs_r_profile_csv='ocv_internal_resistance.csv',
    time_compression_scalar=1
  )

  time.sleep(10)


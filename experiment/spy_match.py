import re

def spy_line_of_match(spy, string):
  result = None
  spy_list = spy.split("\n") if type(spy) is str else spy
  pattern = re.compile(string)
  for line in spy_list:
    if pattern.match(line):
      result = line
      break
  return result

spy = """
START
SEARCH_FOR_SUPER_SIGNAL:door_closed
SEARCH_FOR_SUPER_SIGNAL:common_features
ENTRY_SIGNAL:common_features
ENTRY_SIGNAL:door_closed
[2019-02-09 10:39:04:921569] light_off
INIT_SIGNAL:door_closed
SEARCH_FOR_SUPER_SIGNAL:off
ENTRY_SIGNAL:off
INIT_SIGNAL:off
<- Queued:(0) Deferred:(0)
Toasting:off
Toasting:door_closed
EXIT_SIGNAL:off
SEARCH_FOR_SUPER_SIGNAL:toasting
SEARCH_FOR_SUPER_SIGNAL:door_closed
SEARCH_FOR_SUPER_SIGNAL:heating
ENTRY_SIGNAL:heating
[2019-02-09 10:39:04:934164] heater_on
ENTRY_SIGNAL:toasting
INIT_SIGNAL:toasting
<- Queued:(0) Deferred:(0)
buzz
Buzz:toasting
Buzz:heating
Buzz:door_closed
Buzz:common_features
[2019-02-09 10:39:05:135511] buzz
Buzz:common_features:HOOK
<- Queued:(0) Deferred:(0)"""

print(spy_line_of_match(spy, "] buzz"))

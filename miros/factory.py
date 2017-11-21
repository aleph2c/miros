from miros.hsm import spy_on
from miros.activeobject import ActiveObject, ActiveFabric
from miros.event import signals, Event, return_status

# factory
# I want this to be a very small factory
'''
chart = HsmFactory(name='toaster_oven'))
'''
# create
'''
chart.create(state='door_closed')
'''

# create a function with a given name
#def make_method(name):
#  def func1(*args):
#    for arg in args:
#      print arg
#    return 42
#  func1.__name__ = name
#  return func1

# module name __name__
# dir(__name__) will return this module's names

# need to put code inside of the function
# thinking that a context manager can do this

# the function will need to:
# 1) be wrapped with spy_on
# 2) has an if else structure that checks the signal names, then
# 3) returns the correct return status
# 4) manage a trans 
# 5) manage a handled
# 6) easy to adjust hierarchy
# just return an active object

# I want a to_s which will output the function as a string.  This could be
# copies and placed directly in the code

# I want normal functions to work with the factory, through an injection api

# def fn
#   pass
# factory.inject(fn, named="bobby")

# problems
# 1) it's going to get too complicated to debug
# 2) a factory of what? hsm/active object?/instrumented?/not-instrumented?


#chart.temp.fun.__name__



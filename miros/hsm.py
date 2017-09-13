import sys
import traceback
# this_function_name = sys._getframe().f_code.co_name

def reflect(hsm=None,e=None):
  '''
    This will return the callers function name as a string:
    Example:

      def example_function():
        return reflect()

      print(example_function) #=> "example_function"
    
  '''
  fnt  = traceback.extract_stack(None,2)
  fnt1 = fnt[0]
  fnt2 = fnt1[2]
  return fnt2

def top(hsm, e):
  status = ReturnCodes.UNHANDLED

def init(hsm,e):
  pass

def ctor(hsm,e):
  pass

def dispatch(hsm,e):
  pass

def trans(hsm,e):
  pass

def is_in(hsm,e):
  pass

def child_state(hsm,e):
  pass


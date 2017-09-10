# events should just be int so that they can be fast
#enum {
#    /* unhandled and need to "bubble up" */
#    Q_RET_SUPER,     /*!< event passed to superstate to handle */
#    Q_RET_SUPER_SUB, /*!< event passed to submachine superstate */ NEW!
#    Q_RET_UNHANDLED, /*!< event unhandled due to a guard */ NEW! -> ultimate hook
#
#    /* handled and do not need to "bubble up" */
#    Q_RET_HANDLED,   /*!< event handled (internal transition) */
#    Q_RET_IGNORED,   /*!< event silently ignored (bubbled up to top) */
#
#    /* entry/exit */
#    Q_RET_ENTRY,     /*!< state entry action executed */
#    Q_RET_EXIT,      /*!< state exit  action executed */
#
#    /* no side effects */
#    Q_RET_NULL,      /*!< return value without any effect */
#
#    /* transitions need to execute transition-action table in ::QMsm */
#    Q_RET_TRAN,      /*!< event handled (regular transition) */
#    Q_RET_TRAN_INIT, /*!< initial transition in a state or submachine */
#    Q_RET_TRAN_HIST, /*!< event handled (transition to history) */
#    Q_RET_TRAN_EP,   /*!< entry-point transition into a submachine */
#    Q_RET_TRAN_XP    /*!< exit-point transition out of a submachine */
#};

from enum import Enum, unique
@unique
class Events(Enum)
  Q_RET_SUPER = 1
  Q_RET_SUPER_SUB,=  2
  Q_RET_UNHANDLED,=   3
  # handled and do not need to bubble up
  Q_RET_ENTRY = 4
  Q_RET_EXIT, = 5   
                   
  # no side effects 
  Q_RET_NULL,= 6
                   
  #transitions need to execute
  Q_RET_TRAN,= 7
  Q_RET_TRAN_INIT, = 8
  Q_RET_TRAN_HIST, = 9
  Q_RET_TRAN_EP,  = 10
  Q_RET_TRAN_XP   = 11

if '__main__' == __file__:
  enum = Events
  import pdb; pdb.set_trace()

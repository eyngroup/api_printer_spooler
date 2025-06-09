from . import Util

class AcumuladosX(object):
  #Global variables
  _freeTax = 0
  _generalRate1 = 0
  _generalRate1Tax = 0
  _reducedRate2 = 0
  _reducedRate2Tax = 0
  _additionalRate3 = 0
  _additionalRate3Tax = 0

  def __init__(self, trama):
    if trama is not None:
      if (len(trama) > 0):
        try:
          _arrayParameter = trama.split(chr(0X0A)) 
          if (len(_arrayParameter) >= 7):
            self._freeTax = Util().do_value_double(_arrayParameter[0])
            self._generalRate1 = Util().do_value_double(_arrayParameter[1])
            self._reducedRate2 = Util().do_value_double(_arrayParameter[2])
            self._additionalRate3 = Util().do_value_double(_arrayParameter[3])
            self._generalRate1Tax = Util().do_value_double(_arrayParameter[4])
            self._reducedRate2Tax = Util().do_value_double(_arrayParameter[5])
            self._additionalRate3Tax = Util().do_value_double(_arrayParameter[6])
        except():
            return
  
  def FreeTax(self):
    return self._freeTax
  
  def GeneralRate1(self):
    return self._generalRate1
  
  def GeneralRate1Tax(self):
    return self._generalRate1Tax
  
  def ReducedRate2(self):
    return self._reducedRate2

  def ReducedRate2Tax(self):
    return self._reducedRate2Tax
  
  def AdditionalRate3(self):
    return self._additionalRate3
    
  def AdditionalRate3Tax(self):
    return self._additionalRate3Tax



OFF = 0

class _logging():
# 
  def __init__(self, mask):
    self.logmask = mask
    self.mask_dic = {1: "INFO", 2: "ERROR", 4: "WARNING", 8: "DEBAG", 10: "FATAL"}

    self.INFO = 1
    self.ERROR = 2
    self.WARNING = 4
    self.DEBAG = 8
    self.FATAL = 10

  def _print(self, mask, *args):
    if ((self.logmask | mask == self.logmask) or (mask == 10)):
      string = ''
      for data in args:
        string = string + data
      print(f"[{self.mask_dic.get(mask)}] {string}")
# 
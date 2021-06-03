import tkinter as Tk        # Бибиотека для оконного приложения
import tkinter.ttk as ttk   # Библиотека виджетов для окна
from datetime import datetime as dt   # Работа с unix временем

# ==============================[Внешний класс]=================================

class MacTableFrame(Tk.Frame):
# 
  def __init__(self, parent):
    Tk.Frame.__init__(self, parent)

    self.configure(height = 0.5 * parent.winfo_screenheight())

    self.table = UniqueMacTable(self)
    self.table.pack(fill = Tk.BOTH, expand = True)

# ---------------------[Методы для внешнего использования]----------------------

  def update_table(self, data):
  # 
    self.table.update_table(data)
  # 

# ------------------------------------------------------------------------------
# 

# ==============================================================================

def _parser_to_mac_table(data):
# 
  rows = list()

  # Создаем заголовки
  headings = ('Data', 'MAC address',
              'Messages', 'Status', 'Vendor')

  # Собираем данные в нужную форму
  for mac, info in data.items():
  # 
      mask = info['type_bitmask']
      status = info['status']
      org = info['vendor']

      time = info['first_time']
      time = dt.fromtimestamp(int(time)).strftime('%d/%m/%Y, %H:%M:%S')

      msg = None
      if (mask & 2 == 2):
      # 
          msg = "probe"
      # 
      if (mask & 1 == 1):
      # 
          msg = (msg + "/assoc" if msg is not None else "assoc")
      # 
      if (mask & 4 == 4):
      # 
          msg = (msg + "/data" if msg is not None else "data")
      # 

      rows.append([time, mac, msg, status, org])
  # 

  rows = tuple(rows)

  return headings, rows
# 

class UniqueMacTable(ttk.Treeview):
# 
  def _get_mac_table_data(self):
  # 
    data = request("MACDB REQV")
    headings, rows = _parser_to_mac_table(data)
    return headings, rows
  # 

  def __init__(self, parent):
    super().__init__(parent)

    # Тег для определение цвета закраски вставляемой строки
    self.tag_configure('bg_87CEEB', background = '#87CEEB')
    self.tag_configure('bg_FA8072', background = '#FA8072')

    headings, rows = _parser_to_mac_table({})

    self.configure(columns = headings, show = 'headings')

    for column in headings:
    # 
      if (column != 'Vendor'):
        self.heading(column,text = column, anchor = Tk.CENTER)
        self.column(column, anchor = Tk.CENTER)
    # 

    self.heading(column,text = column, anchor = Tk.CENTER, command=lambda: \
                       self._treeview_sort_column(self, column, False))
    self.column(column, anchor = Tk.CENTER)

    for row in rows:
      self._insert('', Tk.END, values = tuple(row))

    # Установим прокрутку таблицы по двум осям
    yscroll = Tk.Scrollbar(self, command = self.yview)
    self.configure(yscrollcommand = yscroll.set)
    yscroll.pack(side = Tk.RIGHT, fill = Tk.Y)
    self.pack(expand = Tk.YES, fill = Tk.BOTH)

    xscroll = Tk.Scrollbar(self, orient = Tk.HORIZONTAL)
    xscroll.config(command = self.xview)
    self.configure(xscrollcommand = xscroll.set)
    xscroll.pack(side = Tk.BOTTOM, fill=Tk.X)
    self.pack()
  # 

  # Переопределение метода insert() для раскраски строк таблицы
  def _insert(self, parent_node, index, **kwargs):
  # 
    item = super().insert(parent_node, index, **kwargs)

    values = kwargs.get('values', None)

    if values:
    # 
      if (values[3] == 'unconfirmed'):
        super().item(item, tag = 'bg_87CEEB')
      elif (values[4] == 'unknown'):
        super().item(item, tag = 'bg_FA8072')
    # 

    return item
  # 

  def _treeview_sort_column(self, tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col, command=lambda: \
               self._treeview_sort_column(tv, col, not reverse))

  def _delete_table(self):
  # 
    for i in self.get_children():
      self.delete(i)
  # 

# ---------------------[Методы для внешнего использования]----------------------

  def update_table(self, data):
  # 
    mac_base = data.get('mac_base')
    if mac_base is None:
      mac_base = dict()

    headings, rows = _parser_to_mac_table(mac_base)
    self._delete_table()

    for row in rows:
      self._insert('', Tk.END, values = tuple(row))

    self.update()
  # 

# ------------------------------------------------------------------------------
# 

def _parser_to_bssid_table(data):
# 
  headings = ('BSSID', 'Status', 'Last connect', \
    'Collected dev (start session)', 'Collected dev (per session)')
  rows = list()

  for bssid, info in data.items():
  # 
    if info['last_time'] is not None:
    # 
      now = dt.timestamp(dt.now())
      # Предполагается, что ТД связывается с сервером 1 раз в минуту
      # Но даем фору в 2 минуты
      if ((now - info['last_time']) > 120):
        status = 'inactive'
      else:
        status = 'activ'

      time = dt.fromtimestamp(int(info['last_time'])).\
                  strftime('%d/%m/%Y, %H:%M:%S')
    # 
    else:
      time = '-'
      status = 'unknown'

    dev_count = len(info.get('mac_base')) - info['start_count']

    rows.append([bssid, status, time, info.get('start_count'), dev_count])
  # 

  rows = tuple(rows)
  return headings, rows
# 

# ==============================[Внешний класс]=================================

class BssIdTableFrame(Tk.Frame):
# 
  def __init__(self, parent):
    Tk.Frame.__init__(self, parent)

    headings, rows = _parser_to_bssid_table({})
    self.table = ttk.Treeview(self, columns = headings, show = 'headings')

    for column in headings:
    # 
      self.table.heading(column,text = column, anchor = Tk.CENTER)
      self.table.column(column, anchor = Tk.CENTER)
    # 

    for row in rows:
      self.table.insert('', Tk.END, values = tuple(row))

    self.table.pack(fill = Tk.BOTH, expand = True)

    # Установим прокрутку таблицы по двум осям
    yscroll = Tk.Scrollbar(self.table, command = self.table.yview)
    self.table.configure(yscrollcommand = yscroll.set)
    yscroll.pack(side = Tk.RIGHT, fill = Tk.Y)
    self.table.pack(expand = Tk.YES, fill = Tk.BOTH)

  def _delete_table(self):
  # 
    for i in self.table.get_children():
      self.table.delete(i)
  # 

# ---------------------[Методы для внешнего использования]----------------------

  def update_table(self, data):
  # 
    headings, rows = _parser_to_bssid_table(data)
    self._delete_table()

    for row in rows:
      self.table.insert('', Tk.END, values = tuple(row))

    self.table.update()
  # 

# ------------------------------------------------------------------------------

# 
# ==============================================================================

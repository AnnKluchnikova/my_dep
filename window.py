import tkinter as Tk
import tkinter.ttk as ttk
from tables import MacTableFrame, BssIdTableFrame
from startpage_plot import StartPagePlote
from onepage_plot import OnePagePlote
import tkinter.messagebox as mbox
from math import floor
import datetime as dt
from PIL import Image, ImageTk

class MainWindow(Tk.Tk):

  def __init__(self, win_analyz_conn, log, update_rate):
    Tk.Tk.__init__(self)

    self.configure(background = 'white')

    self.update_rate = update_rate
    self.conn = win_analyz_conn
    self.log = log

    Tk.Tk.wm_title(self, 'RADMAC')

    style = ttk.Style(self)
    style.configure('lefttab.TNotebook', tabposition='wn')
    style.map("TNotebook.Tab", background=[("selected", 'white')])
    style.configure('TNotebook.Tab', padding=(20, 8, 20, 0),
                                        font = ("Helvetica", 10, 'bold'))

    self.notebook = ttk.Notebook(self, style='lefttab.TNotebook')
    self.startpage = StartPage(self.notebook)
    self.pageone = PageOne(self.notebook, self)

    self.notebook.pack(side = Tk.TOP, fill = Tk.BOTH, expand = True)
    self.notebook.bind("<<NotebookTabChanged>>", None)

  def _data_request(self):
    while True:
      self.conn.send(["ALL DATA", ])
      if (self.conn.poll(timeout = 1) == True):
        msg = self.conn.recv()

        if (msg[0] == "ALL"):
          data = msg[1]
          break
    return data

  def _update(self):
    data = self._data_request()
    self.startpage._update(data)
    self.pageone._update(data)
    self.after(self.update_rate, self._update)

  def run(self):
    wwidth = self.winfo_screenwidth()
    wheight = self.winfo_screenheight()
    self.geometry('{}x{}'.format(wwidth, wheight))

    def _on_close():
      response = mbox.askyesno('RADMAC (Exit)',\
                               'Are you sure you want to exit?')

      if response:
        self.destroy()

    startpage_icon = Tk.PhotoImage(file = 'home.png')
    pageone_icon = Tk.PhotoImage(file = 'analiz.png')
    self.notebook.add(self.startpage, image = startpage_icon)
    self.notebook.add(self.pageone, image = pageone_icon)

    self.protocol('WM_DELETE_WINDOW',_on_close)
    self.tk.eval('::msgcat::mclocale en')

    self.after(0, self._update)
    self.mainloop()

class StartPage(Tk.Frame):

  def __init__(self, parent):
    Tk.Frame.__init__(self, parent)

    headofpage = Tk.Frame(self)
    headofpage.pack(side = Tk.TOP)

    def _get_start_time():
      self.start_data = floor(dt.datetime.now().timestamp())
      time = dt.datetime.fromtimestamp(self.start_data).\
                            strftime('%d/%m/%Y, %H:%M')
      return time

    width = self.winfo_screenwidth() * 0.5
    starttime = Tk.LabelFrame(headofpage, text = "Session start time",\
                         width = width, height = 100, font = ("Helvetica", 15))
    starttime.pack(side = Tk.LEFT, anchor = Tk.CENTER)
    starttime.pack_propagate(0)
    slable = Tk.Label(starttime, text = _get_start_time(), relief = Tk.SUNKEN,
                                        bg = 'white', font = ("Helvetica", 25))
    slable.pack(fill = Tk.BOTH, expand = True)

    worktime = Tk.LabelFrame(headofpage, text = "Session work time",\
                         width = width, height = 100, font = ("Helvetica", 15))
    worktime.pack(side = Tk.LEFT, anchor = Tk.CENTER)
    worktime.pack_propagate(0)
    self.wlable = Tk.Label(worktime, text = '00:00:00', relief = Tk.SUNKEN,
                                        bg = 'white', font = ("Helvetica", 25))
    self.wlable.pack(fill = Tk.BOTH, expand = True)

    self.table = BssIdTableFrame(self)
    self.table.pack(fill = Tk.BOTH, expand = True)

    # self.plot = WapsTrafficPlot(self)
    self.plot = StartPagePlote(self)
    self.plot.pack(fill = Tk.BOTH, expand = True)

  def _update(self, data):
    def __get_session_time():
      now = floor(dt.datetime.now().timestamp())
      sec = now - self.start_data
      time = dt.timedelta(seconds = sec)
      return time

    self.table.update_table(data)
    self.plot.update_plot(data)
    self.wlable['text'] = __get_session_time()

class PageOne(Tk.Frame):
  def _init_combo_list(self, data, main):
    loc_list = list(data.keys())
    # if (len(loc_list) > 0):
    #   self.default_loc = loc_list[0]
    return loc_list

  def _update_combobox(self, data):
    values = list(data.keys())
    if (len(values) == 0):
      self.default_loc = ""
    self.combobox['values'] = values

  def _change_location(self, event):
    select = event.widget.get()
    if (select != self.default_loc):
      # local_data = (self.full_data.get(select)).get('mac_base')
      # self.plot.update_plot(local_data)
      # self.table.update_table(local_data)
      self.default_loc = select
      self.main._update()

  def _get_local_data(self, data):
    self.full_data = data
    local_data = data.get(self.default_loc)

    if local_data is None:
      local_data = dict()
    return local_data

  def __init__(self, parent, main):
    Tk.Frame.__init__(self, parent)

    headofpage = Tk.Frame(self)
    headofpage.pack(side = Tk.TOP)

    self.main = main

    self.default_loc = ""
    self.full_data = dict()

    self.lable = Tk.Label(headofpage, text = "Selected BSSID:",
                                             font=("Helvetica", 20))
    self.lable.pack(side = Tk.LEFT)
    self.lable.pack_propagate(0)

    self.combobox = ttk.Combobox(headofpage, values = "")
    self.combobox.pack(side = Tk.LEFT)
    self.combobox.bind('<<ComboboxSelected>>', self._change_location)

    self.table = MacTableFrame(self)
    self.table.pack(side = Tk.BOTTOM, fill = Tk.BOTH, expand = True)
    self.table.pack_propagate(0)

    self.plot = OnePagePlote(self)
    self.plot.pack(side = Tk.BOTTOM, fill = Tk.BOTH, expand = True)
    self.plot.pack_propagate(0)

  def _update(self, data):
    self._update_combobox(data)
    local_data = self._get_local_data(data)

    self.table.update_table(local_data)
    self.plot.update_plot(local_data)
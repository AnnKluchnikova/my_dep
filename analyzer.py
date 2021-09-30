from datetime import datetime as dt
import analyzer_func as func
from itertools import groupby
from math import floor
import gc

class DataAnalyzer():
  def __init__(self, analyz_serv_conn, analyz_win_conn, log):
    self.serv_conn = analyz_serv_conn
    self.win_conn = analyz_win_conn
    self.log = log
    self.oui_base = None
    self.loc_base = None

  def _filter(self, element):
    ret = False
    status = "unconfirmed"
    org = "unknown"

    oktet = int(element['mac'][0:2], 16)
    mask = int(element['type_bitmask'])

    if (oktet & 2 == 2):
      if (mask & 4 != 4):
        # print("#1",ret, status, org)
        return ret, status, org
      else:
        ret == True
        status = "random"
        # print("#2",ret, status, org) # #2 False random unknown
        return True, status, org

    mac_id = element['mac'][0:8]
    for oui in self.oui_base:
      if(mac_id == oui['hex']):
        ret = True
        org = oui['org']
        break

    if (mask & 4 == 4):
      if(ret == True):
        status = "confirmed"
      else:
        ret == True
    # print("#3",ret, status, org)
    return ret, status, org

  def _channel_parser(self, data, loc):
    stat_2_4_GH = dict()
    stat_5_GH = dict()

    result = groupby(sorted(data, key=lambda x: x['ch']), lambda x: x['ch'])
    for ch, count in result:
      if (ch <= 14):
        stat_2_4_GH.update({ch: len(list(count))})
      elif (ch >= 36):
        stat_5_GH.update({ch: len(list(count))})

    self.loc_base[loc].update({'ch_stat': {'2_4': stat_2_4_GH, '5': stat_5_GH}})

  def _data_parser(self, new_data):
    counter_all = 0
    counter_filt = 0
    counter_new = 0
    rand_count = 0
    conf_count = 0

    register_time = floor(dt.now().timestamp())
    data_list = new_data.get('probe_requests')
    event = False
    loc = new_data['ap_id']
    is_here = self.loc_base.get(loc)

    if is_here is None:
      self.loc_base.update({loc: {'last_time': register_time,
                                  'start_count': 0,
                                  'ch_stat': {},
                                  'mac_base': {},
                                  'session_activ':{}}
                            })
    else:
      (self.loc_base.get(loc)).update({'last_time': register_time})

    self._channel_parser(data_list, loc)
    for record in data_list:
      counter_all += 1
      dups_mac_list = list()

      for elem in data_list:
        if (record['mac'] == elem['mac']):
          dups_mac_list.append(elem)

      type_bitmask = 0
      ssid = list()

      if (len(dups_mac_list) > 1):
        for item in dups_mac_list:
          type_bitmask = type_bitmask | item['type_bitmask']

          try:
            if (record['ssid'] != ""):
              try:
                index = ssid.index(record['ssid'])
              except ValueError:
                ssid.append(record['ssid'])
          except KeyError:
            pass

        mined_mac = dict(
                         mac = record['mac'],
                         type_bitmask = type_bitmask,
                        )
      else:
        try:
          if (record['ssid'] != ""):
            ssid.append(record['ssid'])
        except KeyError:
          pass

        mined_mac = dict(
                         mac = record['mac'],
                         type_bitmask = record['type_bitmask'],
                        )

      for item in dups_mac_list:
        data_list.remove(item)

      access_mac = (self.loc_base[loc].get('mac_base')).get(mined_mac['mac'])
      if access_mac is None:
        ret, status, org = self._filter(mined_mac)
        if (ret == False):
          # print(mined_mac)
          counter_filt += 1
          continue

        if (status == "random"):
          rand_count += 1
        elif (status == "confirmed"):
          conf_count += 1

        (self.loc_base[loc].get('mac_base')).\
          update({mined_mac['mac']:\
                  {'first_time': register_time,\
                   'last_time':  register_time,
                   'reps_count': 1,
                   'type_bitmask': mined_mac['type_bitmask'],
                   'status': status,
                   'vendor': org,
                   'ssid': ssid}
                  })

        counter_new += 1
        event = True
      else:
        if (access_mac['status'] == "unconfirmed") and\
              (access_mac['vendor'] != "unknown"):
          if (mined_mac['type_bitmask'] & 4 == 4):
            conf_count += 1
            access_mac.update({'status': "confirmed"})
        elif (access_mac['status'] == "random"):
          rand_count += 1

        mac_mask = access_mac['type_bitmask'] | mined_mac['type_bitmask']
        access_mac.update({'last_time': register_time,\
                           'type_bitmask': mac_mask,
                           'reps_count': access_mac['reps_count'] + 1})

        for val in ssid:
          try:
            index = access_mac['ssid'].index(val)
          except ValueError:
            access_mac['ssid'].append(val)
        event = True

    (self.loc_base[loc].get('session_activ')).\
        update({register_time: {'all': counter_all,
                                'filt': counter_filt,
                                'new': counter_new,
                                'status_stat': {'conf': conf_count,
                                                'rand': rand_count
                                                }
                                }
               })
    return event

  def _main_loop(self):
    try:
      while True:
        while True:
          if (self.win_conn.poll() == True):
            msg = self.win_conn.recv()
            self.log._print(self.log.DEBAG, f"analyzer: [MSG] {msg[0]}")

            if (msg[0] == "ALL DATA"):
              self.win_conn.send(["ALL", self.loc_base])

          if (self.serv_conn.poll() == True):
            msg = self.serv_conn.recv()

            self.log._print(self.log.DEBAG, f"analyzer: [MSG] {msg[0]}")

            if (msg[0] == "ANALYZ"):
              # self.log._print(self.log.DEBAG,"analyz:msg from server: \n {}".\
              #         format(func.debag_json_print(msg[1])))
              break

        if (self._data_parser(msg[1]) == True):
          func._save_loc_base(self.loc_base, self.base_f_path)

        gc.collect()
    except KeyboardInterrupt:
      pass

  def run(self):
    self.oui_base = func._get_oui_base(self.log)
    if self.oui_base is None:
      return

    self.loc_base, self.base_f_path = func._get_loc_base(self.log)
    if self.loc_base is None:
      return

    # self.sesstion_start = dt.now()
    self._main_loop()
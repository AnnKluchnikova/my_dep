'''
Программа предназначена для автоматизации загрузки официальной базы OUI
и приведение ее к нужному виду для удобства использования
'''
import urllib.request
import shutil
import json
import os

def _oui_request(url, src_file):
  with urllib.request.urlopen(url) as response,\
       open(src_file, 'wb') as out_file:
    shutil.copyfileobj(response, out_file)
  return True

def _create_OUI_db(src_file, dst_file):
  oui = list()

  try:
    with open(src_file, "r") as read_file:
      for line in read_file:

        if len(line) < 16:
          continue

        if (line[2] == '-' and line[5] == '-'):
          org = line[16:].strip()
          oui.append(dict(hex = line[0:8], org = org))

  except FileNotFoundError:
    return False

  with open(dst_file, 'w') as write_file:
    json.dump(oui, write_file, indent=2)

  os.remove(src_file)
  return True

def get_path_to_OUI_db(log):
  src_file = "oui.txt"
  dst_file = "oui.json"
  url = "http://standards-oui.ieee.org/oui/oui.txt"

  if(os.path.isfile(dst_file) == True):
    log._print(log.INFO, f"Path to the OUI database: ./{dst_file}")
    return dst_file

  with open(src_file, "wb"):
    log._print(log.INFO, "Please wait a few seconds...\n"
              "       The OUI database is being loaded to make the app work")

  if (_oui_request(url, src_file) != True):
    log._print(log.ERROR, "Failed to load the OUI database\n"
          f"        from the \"{url}\" resource\n")
    return None

  if (_create_OUI_db(src_file, dst_file) != True):
    log._print(log.ERROR, "Failed to load the OUI database\n")
    return None

  log._print(log.INFO, "OUI database loaded successfully\n"
             f"       Path: ./{dst_file}")
  return dst_file

if (__name__ == '__main__'):
  get_path_to_OUI_db()
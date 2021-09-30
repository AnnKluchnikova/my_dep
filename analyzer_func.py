from oui_request import get_path_to_OUI_db
# import os.path as os_path
import json

def _get_oui_base(log):
  file_path = get_path_to_OUI_db(log)

  if file_path is None:
    return None

  with open(file_path, "r") as read_file:
    return json.load(read_file) # <class 'list'>

def _get_loc_base(log):
  file_path = "RADMAC_DB.json"

  def _parse_data(data):
    db = dict()
    for loc in data.keys():
      db.update({loc: {'last_time': None,\
                       'start_count': len(data.get(loc)),\
                       'ch_stat': {},
                       'mac_base': data.get(loc),
                       'session_activ':{}}
                })
    return db

  try:
    with open(file_path, "r") as read_file:
      data = json.load(read_file) # <class 'dict'>

    if data is None:
      return dict(), file_path
    else:
      return _parse_data(data), file_path

  except FileNotFoundError:
    with open(file_path, "w"):
      print("[WARNING] The file \"{}\" was not found\n"
            "          It will be created in the current folder"\
            .format(file_path))
      return dict(), file_path

  except json.decoder.JSONDecodeError:
    # path = os_path.join(os_path.abspath(os_path.dirname(__file__)), file_path)
    print("[WARNING] Failed to read database from file \"{}.\"\n"
          "          The file will be used to store the new database"\
          .format(file_path))
    return dict(), file_path

def _save_loc_base(data_base, file_path):
  data = dict()
  for loc in data_base.keys():
    data.update({loc: data_base[loc].get('mac_base')})

  with open(file_path, "w") as write_file:
    json.dump(data, write_file, indent=2)
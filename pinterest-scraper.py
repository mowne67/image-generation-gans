import json, os, time
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

s = requests.Session()

retries = Retry(total=5,
                backoff_factor=0.5,
                status_forcelist=[ 500, 502, 503, 504 ])

s.mount('https://', HTTPAdapter(max_retries=retries))

min_dimension = 500
ignore_domains = ["shutterstock.com", "stock.adobe.com"]
pins_to_scrape = [
  {
    "id": "155303887470047695",
    "signature": "29612cf444f4de8d8a60e9fa2d5e8156"
  }, {
    "id": "959689001815715565",
    "signature": "d0d9d0b997cc06604148b9d60ea84b20"
  }, {
    "id": "540150549129293105",
    "signature": "f30403acb021d33a9193f37ba0e105d2"
  }, {
    "id": "1030198483482478914",
    "signature": "535426acf8891401bbc0f38946076103"
  }, {
    "id": "81698180730235418",
    "signature": "3baba65cab0c872d4abc39a5de1c8057"
  }
]


downloaded_pins = []
base_dir = "/Users/HP/PycharmProjects/pythonProject/dir"
pin_dirs = os.listdir(base_dir)
for pin_dir in pin_dirs:
  if (pin_dir.startswith(".")):
    continue
  abs_pin_dir = os.path.join(base_dir, pin_dir)
  for file in os.listdir(abs_pin_dir):
    if file.endswith(".jpg"):
      downloaded_pins.append(file)

for pin_to_scrape in pins_to_scrape:
  pin_id = pin_to_scrape["id"]
  img_signature = pin_to_scrape["signature"]
  dest_dir = os.path.join(base_dir, pin_id)
  os.makedirs(dest_dir, exist_ok=True)
  response_path = os.path.join(dest_dir, "response.json")
  json_response_write = open(response_path, "a")
  bookmark_id = ""

  results_exist = True
  while results_exist:
    visual_search_url = 'https://in.pinterest.com/resource/VisualLiveSearchResource/get/?source_url=/pin/' + pin_id + '/visual-search/?imageSignature=' + img_signature + '&data={"options":{"pin_id":"' + pin_id + '","image_signature":"' + img_signature + '","bookmarks":["' + bookmark_id + '"]}}'
    time.sleep(1)
    search_response = s.get(visual_search_url)
    if search_response.status_code == 200:
      j = json.loads(search_response.text)

      results = j["resource_response"]["data"]["results"]
      for result in results:
        orig = result["images"]["orig"]
        if orig['width'] < 500 or orig['height'] < 500 or result['domain'] in ignore_domains:
          continue
        orig_url = orig["url"]
        pin = result["id"]
        file_name = os.path.basename(orig_url)
        img_extension = os.path.splitext(file_name)[1]
        pin_file_name = pin + img_extension
        pin_path = os.path.join(dest_dir, pin_file_name)

        if pin_file_name not in downloaded_pins:
          response = s.get(orig_url)
          if response.status_code == 200:
            with open(pin_path, "wb") as f:
              f.write(response.content)
              downloaded_pins.append(pin_file_name)
              time.sleep(.1)
          else:
            print(response.status_code)
            print(response.text)
        else:
          print(f"image already downloaded, sig: {file_name}, pin: {pin}")
      if len(results) == 0:
        results_exist = False
      else:
        bookmark_id = j["resource_response"]["bookmark"]
        json_response_write.write(search_response.text + "\n")

    else:
      print(f"visual search request failed with status code: {search_response.status_code}, msg: {search_response.text}")
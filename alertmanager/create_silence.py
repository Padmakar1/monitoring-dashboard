try:
  import requests
except Exception:
  requests = None

from datetime import datetime, timedelta
import json
from urllib import request as urllib_request

ALERTMANAGER = 'http://localhost:9093'

silence = {
  "matchers": [
  {"name": "alertname", "value": "TestAlert", "isRegex": False}
  ],
  "startsAt": datetime.utcnow().isoformat() + 'Z',
  "endsAt": (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z',
  "createdBy": "script",
  "comment": "Automated silence for testing"
}

def send_with_requests(url, payload):
  r = requests.post(url, json=payload)
  print(r.status_code)
  try:
    print(r.text)
  except Exception:
    pass

def send_with_urllib(url, payload):
  data = json.dumps(payload).encode('utf-8')
  req = urllib_request.Request(url, data=data, headers={'Content-Type': 'application/json'})
  try:
    with urllib_request.urlopen(req) as resp:
      body = resp.read().decode('utf-8')
      print(resp.getcode())
      print(body)
  except Exception as e:
    print('Error creating silence with urllib:', e)


if requests:
  send_with_requests(f"{ALERTMANAGER}/api/v2/silences", silence)
else:
  send_with_urllib(f"{ALERTMANAGER}/api/v2/silences", silence)

try:
    import requests
except Exception:
    requests = None

import json
from urllib import request as urllib_request

ALERTMANAGER = 'http://localhost:9093'

alert = [
    {
        "labels": {"alertname": "TestAlert", "severity": "warning"},
        "annotations": {"summary": "This is a test alert", "description": "Testing Alertmanager integration"},
        "startsAt": "2025-08-17T00:00:00Z"
    }
]

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
        print('Error sending alert with urllib:', e)


if requests:
    send_with_requests(f"{ALERTMANAGER}/api/v1/alerts", alert)
else:
    send_with_urllib(f"{ALERTMANAGER}/api/v1/alerts", alert)

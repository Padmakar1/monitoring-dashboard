from flask import Flask, Response, abort
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import logging
import time
import random

app = Flask(__name__)

# metrics
REQUESTS = Counter('app_requests_total', 'Total number of requests')
# labeled per-endpoint counter
REQUESTS_BY_ENDPOINT = Counter('app_requests_by_endpoint_total', 'Total requests by endpoint', ['endpoint'])
REQUEST_ERRORS = Counter('app_errors_total', 'Total number of errors', ['endpoint'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency seconds', buckets=(0.005,0.01,0.025,0.05,0.1,0.25,0.5,1,2.5,5,10))

# logging
handler = logging.FileHandler('/var/log/myapp/app.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

@app.route('/')
def index():
    endpoint = '/'
    REQUESTS.inc()
    REQUESTS_BY_ENDPOINT.labels(endpoint=endpoint).inc()
    with REQUEST_LATENCY.time():
        app.logger.info('Handled index request')
        # simulate small processing jitter
        time.sleep(random.uniform(0.01, 0.12))
        return 'Hello from monitored app!\n'


@app.route('/item/<name>')
def get_item(name):
    endpoint = '/item'
    REQUESTS.inc()
    REQUESTS_BY_ENDPOINT.labels(endpoint=endpoint).inc()
    with REQUEST_LATENCY.time():
        app.logger.info('Get item %s', name)
        time.sleep(random.uniform(0.01, 0.2))
        return f'Item: {name}\n'


@app.route('/error')
def error():
    endpoint = '/error'
    REQUESTS.inc()
    REQUESTS_BY_ENDPOINT.labels(endpoint=endpoint).inc()
    REQUEST_ERRORS.labels(endpoint=endpoint).inc()
    app.logger.error('Simulated error endpoint called')
    abort(500)


@app.route('/sleep')
def sleep_endpoint():
    """Sleep for `duration` seconds (query param) to simulate latency."""
    endpoint = '/sleep'
    REQUESTS.inc()
    REQUESTS_BY_ENDPOINT.labels(endpoint=endpoint).inc()
    try:
        dur = float((__import__('flask').request.args.get('duration', '0')))
    except Exception:
        dur = 0.0
    with REQUEST_LATENCY.time():
        app.logger.info('Sleeping for %s seconds', dur)
        time.sleep(max(0.0, dur))
        return f'Slept for {dur} seconds\n'

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    # generate some logs periodically in background thread style
    def bg():
        while True:
            app.logger.info('background heartbeat: %s' % random.randint(1,100))
            time.sleep(10)
    import _thread
    _thread.start_new_thread(bg, ())
    app.run(host='0.0.0.0', port=8000)

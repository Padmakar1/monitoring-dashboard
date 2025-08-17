import re
from app import app


def get_metrics_text(client):
    resp = client.get('/metrics')
    return resp.data.decode('utf-8')


def test_endpoints_and_metrics():
    client = app.test_client()

    # hit / endpoint 3 times
    for _ in range(3):
        r = client.get('/')
        assert r.status_code == 200

    # hit /item/xyz 2 times
    for _ in range(2):
        r = client.get('/item/xyz')
        assert r.status_code == 200

    # hit /error once
    r = client.get('/error')
    assert r.status_code == 500

    # check metrics exposed contain counters
    metrics = get_metrics_text(client)
    assert 'app_requests_total' in metrics
    assert 'app_requests_by_endpoint_total' in metrics
    assert 'app_errors_total' in metrics

    # parse counts (simple regex)
    total = int(re.search(r'app_requests_total\s+(\d+)', metrics).group(1))
    assert total >= 6


def test_latency_and_sleep():
    client = app.test_client()
    # cause a sleep to produce latency
    r = client.get('/sleep?duration=1')
    assert r.status_code == 200
    metrics = get_metrics_text(client)
    assert 'request_latency_seconds_bucket' in metrics

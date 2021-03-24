import time
import requests
from datetime import timedelta
import datetime
PROPERTY_ID = 266729184
GA_TIG = "UA-192913792-1"


def get_latest_ts(limit=100, offset=1000, now=None, latest_tran=None):
    if offset < 0:
        return latest_tran

    now = (datetime.datetime.utcnow() - timedelta(minutes=3)).isoformat() if not now else now
    request = f'https://wax.cryptolions.io/v2/history/get_actions?limit={limit}&simple=true&checkLib=true&before={now}&skip={offset}'

    try:
        response = requests.get(request).json()['simple_actions']
    except Exception as e:
        print(e)
        return latest_tran

    if all([r['irreversible'] for r in response]):
        # If all transactions in this batch are irrev, move to the next batch
        return get_latest_ts(limit, offset - limit, now, response[0])
    elif any([r['irreversible'] for r in response]):
        # If some transactions are irrev, find latest
        latest_tran = list(filter(lambda x: x['irreversible'], response))[0]
        return latest_tran
    else:
        return latest_tran


def push_ts_id_old(ts_id):
    url = f'https://www.google-analytics.com/collect?v=1&t=event&tid={GA_TIG}&cid=555&ec=wax-transactions&ea=latest-irreversible&el={ts_id}'
    print(f'Push ts id {ts_id}')
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    return requests.get(url, headers=headers)


def main():
    prev_ts_id = None
    while True:
        ts = get_latest_ts()
        ts_id = ts.get('transaction_id') if ts else prev_ts_id
        prev_ts_id = ts_id if ts_id is not None else prev_ts_id
        print(push_ts_id_old(ts_id))
        time.sleep(10)


if __name__ == '__main__':
    main()

from os import getenv
from json.decoder import JSONDecodeError
import time

import requests


api_key = getenv('DONORFY_API_KEY')
access_key = getenv('DONORFY_ACCESS_KEY')
base_url = f'https://data.donorfy.com/api/v1/{api_key}/'
auth = ('donorfy-export', access_key)
email_keys = [
    'ContactDetails_Personal_Email1Address',
    'ContactDetails_Personal_Email2Address',
    'ContactDetails_Other_Email1Address',
    'RecurringPaymentInstruction_Email',
    'Constituent_ConstituentDescription',
]


def request(verb, path, **kwargs):
    retries = 0
    max_retries = 5
    while retries < max_retries:
        try:
            response = requests.request(
                verb,
                base_url + path,
                auth=auth,
                **kwargs)
            response.raise_for_status()
            return response.json()
        except (JSONDecodeError, requests.exceptions.HTTPError) as e:
            sleep_time = 5
            print(e)
            print(f'Retrying after {sleep_time} seconds...')
            time.sleep(sleep_time)
        retries += 1
    raise RuntimeError(f'Giving up after {max_retries} attempts.')


def get_list_members(list_id):
    page_size = 1000
    page = 1
    path = f'lists/{list_id}/Results'
    total = 0
    while True:
        params = {
            'numberOfRows': page_size,
            'fromRow': (page - 1) * page_size,
        }
        results = request('get', path, params=params)
        total = total + len(results)
        if results == []:
            break
        for row in results:
            yield row
        page += 1

    results = request('get', f'lists/{list_id}')
    expected_total = results['RowCount']

    if total != expected_total:
        print('Total: {}\nExpected total: {}'.format(
            total, expected_total))


def get_constituent(email):
    path = f'constituents/EmailAddress/{email}'
    return request('get', path)

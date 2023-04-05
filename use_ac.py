import json
import time
from datetime import datetime, timedelta
import requests
from nt_models import CabinClass, PriceFilter
from nt_parser import convert_ac_response_to_models, results_to_excel
from nt_filter import filter_prices, filter_airbounds, AirBoundFilter
from ac_searcher import Ac_Searcher
from utils import date_range

def report(name, count):
    header = {
        "Content-Type": "application/json",
        "charset": "utf-8"
    }
    data=json.dumps({
        "title": "UA:"+ str(count),
        "device_key": "REPLACE",
        "body": name,
        "category": "myNotificationCategory",
        "sound": "minuet.caf",
        "badge": 1,
        "icon": "https://day.app/assets/images/avatar.jpg",
        "group": "test",
        "level": "timeSensitive",
    })
    url = "https://api.day.app/push"
    resp = requests.post(url, data=data, headers=header, timeout=10000)
    print("Sent" if resp.status_code == 200 else resp.json())

if __name__ == '__main__':
    origins = ['TPE']
    destinations = ['SFO']
    start_dt = '2023-05-18'
    end_dt = '2023-05-24'
    dates = date_range(start_dt, end_dt)
    #  means eco, pre, biz and first
    cabin_class = [
        "BIZ",
    ]
    airbound_filter = AirBoundFilter(
        max_stops=0,
        airline_include=[],
        airline_exclude=['ET','UA'],
    )
    price_filter = PriceFilter(
        min_quota=1,
        max_miles_per_person=999999,
        preferred_classes=[CabinClass.J, CabinClass.F, CabinClass.Y],
        mixed_cabin_accepted=False
    )
    # seg_sorter = {
    #     'key': 'departure_time',  # only takes 'duration_in_all', 'stops', 'departure_time' and 'arrival_time'.
    #     'ascending': True
    # }
    acs = Ac_Searcher()
    airbounds = []
    for ori in origins:
        for des in destinations:
            for date in dates:
                print(f'search for {ori} to {des} on {date} @ {datetime.now().strftime("%H:%M:%S")}')
                response = acs.search_for(ori, des, date, cabin_class)
                v1 = convert_ac_response_to_models(response)
                airbounds.extend(v1)
                # if there are high volume of network requests, add time.sleep
                # time.sleep(1)
    airbounds = filter_airbounds(airbounds, airbound_filter)
    airbounds = filter_prices(airbounds, price_filter)
    results = []
    for x in airbounds:
        results.extend(x.to_flatted_list())
    print(results)

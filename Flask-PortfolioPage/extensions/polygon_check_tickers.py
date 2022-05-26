import random
from datetime import datetime

import requests
from website import db, models


def polygon_check(ticker_list):
    api_keys_list = [MY_LIST_OF_POLYGON_API_KEYS]
    response_dict = {}

    used_keys = []

    for i in ticker_list:
        ticker = i
        keys_to_use = list(set(api_keys_list) - set(used_keys))
        if len(keys_to_use) > 0:
            api_key = random.choice(list(set(api_keys_list) - set(used_keys)))
            used_keys.append(api_key)
        else:
            api_key = random.choice(api_keys_list)
            used_keys.append(api_key)

        if "X:" in i:
            api_url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?adjusted=true&apiKey={api_key}"
            data = requests.get(api_url).json()
            response_dict[ticker] = []
            response_dict[ticker].append(float(data["results"][0]["c"]))
            date_timestamp = data["results"][0]["t"]
            date_str = datetime.fromtimestamp(date_timestamp // 1000).strftime(
                "%Y-%m-%d %H:%M"
            )
            response_dict[ticker].append(date_str)

        else:
            api_url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?adjusted=true&apiKey={api_key}"
            data = requests.get(api_url).json()
            response_dict[ticker] = []
            response_dict[ticker].append(float(data["results"][0]["c"]))
            date_timestamp = data["results"][0]["t"]
            date_str = datetime.fromtimestamp(date_timestamp // 1000).strftime(
                "%Y-%m-%d %H:%M"
            )
            response_dict[ticker].append(date_str)

    return response_dict


def polygon_check_or_not(ticker_list):
    dict_from_db = {}
    list_to_check = []
    now = datetime.now()

    for ticker in ticker_list:
        ticker_info = models.PolygonCheckedTicker.query.filter_by(ticker=ticker).first()

        if not ticker_info:
            list_to_check.append(ticker)
        else:
            if ticker_info.date_check != now.strftime("%Y-%m-%d"):
                list_to_check.append(ticker)
            else:
                dict_from_db[ticker_info.ticker] = []
                dict_from_db[ticker_info.ticker].append(ticker_info.price)
                dict_from_db[ticker_info.ticker].append(ticker_info.date_info)

    if len(list_to_check) > 0:

        dict_from_polygon = polygon_check(list_to_check)
        list_of_tickers_from_polygon = list(dict_from_polygon.keys())
        list_of_prices_dates_from_polygon = list(dict_from_polygon.values())

        for i in list_of_tickers_from_polygon:
            index = list_of_tickers_from_polygon.index(i)
            ticker_info = models.PolygonCheckedTicker.query.filter_by(ticker=i).first()
            date_str = now.strftime("%Y-%m-%d")
            if ticker_info:
                ticker_info.price = list_of_prices_dates_from_polygon[index][0]
                ticker_info.date_check = date_str
                ticker_info.date_info = list_of_prices_dates_from_polygon[index][1]
                db.session.commit()
            else:
                new_info = models.PolygonCheckedTicker(
                    ticker=i,
                    price=list_of_prices_dates_from_polygon[index][0],
                    date_check=date_str,
                    date_info=list_of_prices_dates_from_polygon[index][1],
                )
                db.session.add(new_info)
                db.session.commit()

        dict_from_polygon.update(dict_from_db)

        return dict_from_polygon

    else:
        return dict_from_db

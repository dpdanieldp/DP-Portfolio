import requests
from datetime import datetime
import random
from website import db
from website import models


def polygon_check(ticker_list):
    api_keys_list = ['yUSniyZhsOS5mL5kd9N0wSDXFrl0poAI', 'clsyK9TpKDfqel1gMO3u64UnO3SL9dUR',
                     'tV7mNlNS4lGGi8P7qB7rNuF3s4d6jsoR', 'pmhrv2Mzh_bxcLAEmJCDyjY5oRpCIBoy',
                     'lwBZG7QTOdKmuGhTM60bd3hNMpU8AYIw', 'TVRChL8pSAoZ3xpl_127sNTcZZru5lTb',
                     'tKRCf11vHdJhO9EUgCZRuK2lpaLYhXdG',
                     'CgPEp6ob8oRAthZlPFWykjuzBDEqp2si',
                     'yBE2Jn3kgoaMQqowqH3lovpUK9qU0W76',
                     'iEF3AkM55DuCRIrSVj2rkzH9HvDjcEYD',
                     '8S7LmmmuEPsYCJ0ngZGmw9Hr3TaUSYqM',
                     'SYs6fkbCn89t4thjz8_9edAuOq40HylA',
                     'YvCEfNq4Xl8MIzUDM60A9yUqwiA2zIsf',
                     '3PBxJmsIFpGKvz1wc34XuNZwPW9L71Mo',
                     'Z9ltuMdUStyjqmlDbg1k2kXThovXiMpq',
                     'RmTMYJ6XT7RIGxM2VpI_9r7YOu43hIuA',
                     'TX4lqCH5NEPb5GtZZle0SFykp7ng0XH6',
                     'o4BHWBPKwMyaovIlnr83xoBufgGgbcNr',
                     'GZotuQuN5Hp5_BoPxTo33ITgELx_z1pE',
                     'kB0bwXRSzPSEVCtTp2jIniaZGfurlQWx',
                     'Tw24ZhBgm4AOkJR0Z06w7GCkyWvtDLZ2',
                     '0s5OQQklJIesir5zAfYVNIFvQdGt5LFh',
                     'gB2au2i2yWNNUIwkjLdpKiKDjyl06Y7j',
                     'id5gZISrUDMUjnVT4d6TYpgQhw3f55ka',
                     'mw2LWPLjZzKjUSdiIvOvP25fwI5qobLX',
                     'zPyPnkHZI6pC1ATbQl8wxSO9GLYIpsCp',
                     'CdKxkCk437ZZ6oMnC2yGzcGSyH8GYBZ4',
                     'ArfGTdWXUtj4Vjl1xvm2Gwzm6V7Hpkmc',
                     'GLTQWikvO4pTSlsK0l87CXCWfg8AP7yT',
                     'bw4ypp8TSg6xjClDofdKUcSEHnfChnkZ',
                     'quNWRFeMZd4VL5NukpfxbZO3ksnwHwbV',
                     '7fmhhklP_9xKzP2ecvy3SsYxIF_P3t3L',
                     'A4i67lX7CTgkdv5rpqjpFSHx9dF9N6ih',
                     'aHk7_Oi5DnTliLxGJJJBVeC4ZeVSSI8r',
                     'bwkAptOSHDkelEmr9sg0EgX2ok_Mjuaw',
                     'OL3DLjRrnBEPQaS1zw99iLf1p7Oek_Sq',
                     'TlWgewHnHLwkRQ2HpYTXIyKP4H7bqccE']
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
            
        # print(api_key)

        if 'X:' in i:
            # try:
            api_url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?adjusted=true&apiKey={api_key}'
            data = requests.get(api_url).json()
            response_dict[ticker] = []
            response_dict[ticker].append(float(data['results'][0]['c']))
            date_timestamp = data['results'][0]['t']
            date_str = datetime.fromtimestamp(date_timestamp // 1000).strftime("%Y-%m-%d %H:%M")
            response_dict[ticker].append(date_str)
            # except:
            #     pass

        else:
            # try:
            api_url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?adjusted=true&apiKey={api_key}'
            data = requests.get(api_url).json()
            response_dict[ticker] = []
            response_dict[ticker].append(float(data['results'][0]['c']))
            date_timestamp = data['results'][0]['t']
            date_str = datetime.fromtimestamp(date_timestamp // 1000).strftime("%Y-%m-%d %H:%M")
            response_dict[ticker].append(date_str)
            # except:
            #     pass


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
                new_info = models.PolygonCheckedTicker(ticker=i,
                                                       price=list_of_prices_dates_from_polygon[index][0],
                                                       date_check=date_str,
                                                       date_info=list_of_prices_dates_from_polygon[index][1])
                db.session.add(new_info)
                db.session.commit()

        dict_from_polygon.update(dict_from_db)
        

        return dict_from_polygon

    else:
        return dict_from_db

from datetime import datetime

import requests
from website import db, models


def polygon_tickers_names():
    api = "ONE_OF_MY_POLYGON_API_KEYS"
    limit = "10000"
    sort = "ticker"
    api_keys_list = ["LIST_OF_MY_POLYGON_API_KEYS"]

    tickers_names_dict = {}

    api_url = f"https://api.polygon.io/v3/reference/tickers?active=true&sort={sort}&order=asc&limit={limit}&apiKey={api}"
    data1 = requests.get(api_url).json()

    for ticker in data1["results"]:
        tickers_names_dict[ticker["ticker"]] = ticker["name"]
    try:
        api_url_2 = data1["next_url"] + "&apiKey=" + api_keys_list[1]
        data2 = requests.get(api_url_2).json()
        for ticker in data2["results"]:
            tickers_names_dict[ticker["ticker"]] = ticker["name"]
        no = 2
        while "next_url" in list(data2.keys()):
            api_url_2 = data2["next_url"] + "&apiKey=" + api_keys_list[no]
            data2 = requests.get(api_url_2).json()

            no += 1

            try:
                for ticker in data2["results"]:
                    tickers_names_dict[ticker["ticker"]] = ticker["name"]
            except KeyError:
                pass
    except KeyError:
        pass

    tickers_list = list(tickers_names_dict.keys())
    names_list = list(tickers_names_dict.values())
    datenow = datetime.now()
    datenow_str = datenow.strftime("%Y-%m-%d %H:%M")
    date_list = []
    for i in range(len(tickers_list)):
        date_list.append(datenow_str)

    last_call = datenow.strftime("%Y-%m-%d")

    dict_to_save = {
        "Last_call": last_call,
        "Ticker": tickers_list,
        "Name": names_list,
        "Date": date_list,
    }

    return dict_to_save


def polygon_tickers_to_db():
    polygon_tickers_dict = polygon_tickers_names()

    date_in_db = models.LastCalls.query.filter_by(source="polygon_date").first()
    if not date_in_db:
        last_call_date = models.LastCalls(
            source="polygon_date", last_call=polygon_tickers_dict["Last_call"]
        )
        db.session.add(last_call_date)
    else:
        date_in_db.last_call = polygon_tickers_dict["Last_call"]

    db.session.commit()

    db.session.query(models.PolygonTicker).delete()
    db.session.commit()

    for i in range(len(polygon_tickers_dict["Ticker"])):
        polygon_info = models.PolygonTicker(
            ticker=polygon_tickers_dict["Ticker"][i],
            name=polygon_tickers_dict["Name"][i],
            date=polygon_tickers_dict["Date"][i],
        )
        db.session.add(polygon_info)

    db.session.commit()


def polygon_tickers_to_db_or_not():
    now = datetime.now()
    last_call_p_date = models.LastCalls.query.filter_by(source="polygon_date").first()

    if last_call_p_date:
        if last_call_p_date.last_call != now.strftime("%Y-%m-%d"):
            try:
                polygon_tickers_to_db()
            except:
                pass

    else:
        try:
            polygon_tickers_to_db()
        except:
            pass

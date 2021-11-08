import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
from website import db
from website import models
from datetime import datetime
import datetime as dt
import ssl
import re


def avg_currencies_b():
    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    '''Bankierpl/waluty/kursy-walut/nbp'''
    url = 'https://www.bankier.pl/waluty/kursy-walut/nbp'
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')

    a= soup.find_all('td', class_="textAlignRight")
    b= soup.find_all('time', class_="time")

    data= [(i.get_text(strip= True)).replace(',', '.') for i in a]
    time= [i.get_text(strip= True) for i in b]
    currency= data[::3]
    unit = []
    for i in currency:
        x = re.findall('[0-9]+', i)
        unit.extend(x)

    currency2 = []
    for i in currency:
        newstring = re.sub(r'[0-9]+', '', i)
        currency2.append(newstring)

    pln_price= data[1::3]
    one_day_change= data[2::3]

    date1= (time[0].split(' '))[-1]
    date = []
    for i in range(len(currency)):
        date.append(date1)

    now = datetime.now()

    last_call = now.strftime("%Y-%m-%d")
    # print (last_call)


    data_s= {"Last_call": last_call,
             "Currency": currency2,
         "Unit": unit,
         "Price in PLN": pln_price,
         "One_day change": one_day_change,
         "Date": date}
    return data_s


def commodities_b():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    '''Bankierpl/surowce/notowania'''
    url = 'https://www.bankier.pl/surowce/notowania'
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')

    a= soup.find_all('td', class_="colWalor textNowrap")
    b= soup.find_all('td', class_="colWaluta")
    c= soup.find_all('td', class_="colKurs")
    d= soup.find_all('td', class_="colZmianaProcentowa")
    g= soup.find_all('td', class_="colAktualizacja")

    surowce= [i.get_text(strip= True) for i in a]
    jednostka_s= [i.get_text(strip= True) for i in b]
    kurs_s= [(i.get_text(strip= True).replace(',', '.')).replace('\xa0', '') for i in c]
    zmiana_proc_s= [((i.get_text(strip= True)).replace(',', '.')).replace('\xa0', '') for i in d]

    aktualizacja_s= [i.get('data-sort-value') for i in g]

    commodities = []
    unit = []
    price = []
    change = []
    date =  []

    if 'ZŁOTO' in surowce:
        commodities.append('GOLD')
        unit.append(jednostka_s[surowce.index('ZŁOTO')])
        price.append(kurs_s[surowce.index('ZŁOTO')])
        change.append(zmiana_proc_s[surowce.index('ZŁOTO')])
        date.append(aktualizacja_s[surowce.index('ZŁOTO')])
    if 'SREBRO' in surowce:
        commodities.append('SILVER')
        unit.append(jednostka_s[surowce.index('SREBRO')])
        price.append(kurs_s[surowce.index('SREBRO')])
        change.append(zmiana_proc_s[surowce.index('SREBRO')])
        date.append(aktualizacja_s[surowce.index('SREBRO')])
    if 'MIEDŹ' in surowce:
        commodities.append('COPPER')
        unit.append(jednostka_s[surowce.index('MIEDŹ')])
        price.append(kurs_s[surowce.index('MIEDŹ')])
        change.append(zmiana_proc_s[surowce.index('MIEDŹ')])
        date.append(aktualizacja_s[surowce.index('MIEDŹ')])
    if 'PALLAD' in surowce:
        commodities.append('PALLADIUM')
        unit.append(jednostka_s[surowce.index('PALLAD')])
        price.append(kurs_s[surowce.index('PALLAD')])
        change.append(zmiana_proc_s[surowce.index('PALLAD')])
        date.append(aktualizacja_s[surowce.index('PALLAD')])
    if 'PLATYNA' in surowce:
        commodities.append('PLATINUM')
        unit.append(jednostka_s[surowce.index('PLATYNA')])
        price.append(kurs_s[surowce.index('PLATYNA')])
        change.append(zmiana_proc_s[surowce.index('PLATYNA')])
        date.append(aktualizacja_s[surowce.index('PLATYNA')])
    if 'ROPA' in surowce:
        commodities.append('OIL')
        unit.append(jednostka_s[surowce.index('ROPA')])
        price.append(kurs_s[surowce.index('ROPA')])
        change.append(zmiana_proc_s[surowce.index('ROPA')])
        date.append(aktualizacja_s[surowce.index('ROPA')])
    if 'ROPA WTI' in surowce:
        commodities.append('OIL WTI')
        unit.append(jednostka_s[surowce.index('ROPA WTI')])
        price.append(kurs_s[surowce.index('ROPA WTI')])
        change.append(zmiana_proc_s[surowce.index('ROPA WTI')])
        date.append(aktualizacja_s[surowce.index('ROPA WTI')])

    now = datetime.now()

    last_call = now.strftime("%Y-%m-%d %H:%M")
    # print(last_call)

    data_s= {"Last_call": last_call,
        "Ticker": commodities,
            "Name": commodities,
             "Unit": unit,
            "Price": price,
            "Change": change,
            "Date": date}


    return data_s


def stocks_b():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    url = 'https://www.bankier.pl/gielda/notowania/akcje'
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')

    a= soup.find_all('td', class_="colWalor textNowrap")
    b= soup.find_all('td', class_="colKurs")
    c= soup.find_all('td', class_="colZmianaProcentowa")
    d= soup.find_all('td', class_="colAktualizacja")

    indices_a= [i.get_text(strip= True) for i in a]
    robocza_dla_nazw= [i.contents[1] for i in a]
    nazwy_a= [i.get('title') for i in robocza_dla_nazw]
    kurs_a= [((i.get_text(strip= True)).replace(',', '.')).replace('\xa0', '') for i in b]
    zmiana_proc_a= [((i.get_text(strip= True)).replace(',', '.')).replace('\xa0', '') for i in c]
    aktualizacja_a= [i.get('data-sort-value') for i in d]

    now = datetime.now()
    last_call = now.strftime("%Y-%m-%d %H:%M")

    data_a= {"Last_call": last_call,
             "Ticker": indices_a,
         "Name": nazwy_a,
         "Price": kurs_a,
         "Percentage change": zmiana_proc_a,
         "Date": aktualizacja_a}

    return data_a


def new_connect_b():
    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    url = 'https://www.bankier.pl/gielda/notowania/new-connect'
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')

    a= soup.find_all('td', class_="colWalor textNowrap")
    b= soup.find_all('td', class_="colKurs")
    c= soup.find_all('td', class_="colZmianaProcentowa")
    d= soup.find_all('td', class_="colAktualizacja")

    nazwy_nc= [i.get_text(strip= True) for i in a]
    kurs_nc= [((i.get_text(strip= True)).replace(',', '.')).replace('\xa0', '') for i in b]
    zmiana_proc_nc= [((i.get_text(strip= True)).replace(',', '.')).replace('\xa0', '') for i in c]
    aktualizacja_nc= [i.get('data-sort-value') for i in d]

    now = datetime.now()
    last_call = now.strftime("%Y-%m-%d %H:%M")

    data_nc= {"Last_call": last_call,
        "Ticker": nazwy_nc,
    "Name": nazwy_nc,
    "Price": kurs_nc,
    "Percentage change": zmiana_proc_nc,
    "Date": aktualizacja_nc}

    return data_nc


def bonds_b():
    # Ignore SSL certificate errors
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    url = 'https://www.bankier.pl/gielda/notowania/obligacje'
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, 'html.parser')

    a = soup.find_all('td', class_="colWalor textNowrap")
    b = soup.find_all('td', class_="colKurs")
    c = soup.find_all('td', class_="colZmianaProcentowa")
    d = soup.find_all('td', class_="colAktualizacja")

    nazwy_ob = [i.get_text(strip=True) for i in a]
    kurs_ob = [((i.get_text(strip=True)).replace(',', '.')).replace('\xa0', '') for i in b]
    zmiana_proc_ob = [((i.get_text(strip=True)).replace(',', '.')).replace('\xa0', '') for i in c]
    aktualizacja_ob = [i.get('data-sort-value') for i in d]

    now = datetime.now()
    last_call = now.strftime("%Y-%m-%d %H:%M")


    data_ob = {"Last_call": last_call,
        "Ticker": nazwy_ob,
    "Name": nazwy_ob,
    "Price": kurs_ob,
    "Percentage change": zmiana_proc_ob,
    "Date": aktualizacja_ob}

    return data_ob


def bankier_info_to_db_currencies():



    avg_currencies = avg_currencies_b()


    date_in_db = models.LastCalls.query.filter_by(source= 'bankier_date').first()
    if not date_in_db:
        last_call_date= models.LastCalls(source= 'bankier_date', last_call= avg_currencies["Last_call"])
        db.session.add(last_call_date)
    else:
        date_in_db.last_call = avg_currencies["Last_call"]

    db.session.commit()

    db.session.query(models.BankierPLNCurrency).delete()
    db.session.commit()

    for i in range(len(avg_currencies["Currency"])):
        currency_info = models.BankierPLNCurrency(currency= avg_currencies['Currency'][i],
                                           rate= int(avg_currencies['Unit'][i]),
                                           pln_price= float(avg_currencies['Price in PLN'][i]),
                                           change= avg_currencies['One_day change'][i],
                                           date= avg_currencies['Date'][i])
        db.session.add(currency_info)


    db.session.commit()


def bankier_currencies_check_or_not():
    now= datetime.now()
    last_call_b_date = models.LastCalls.query.filter_by(source= 'bankier_date').first()

    if last_call_b_date:
        if last_call_b_date.last_call != now.strftime("%Y-%m-%d"):
            try:
                bankier_info_to_db_currencies()
            except:
                pass
    else:
        try:
            bankier_info_to_db_currencies()
        except:
            pass


def bankier_info_to_db_rest():

    commodities = commodities_b()
    stocks = stocks_b()
    new_connect = new_connect_b()
    bonds = bonds_b()

    date_in_db = models.LastCalls.query.filter_by(source= 'bankier_minutes').first()
    if not date_in_db:
        last_call_date= models.LastCalls(source= 'bankier_minutes', last_call= commodities["Last_call"])
        db.session.add(last_call_date)
    else:
        date_in_db.last_call = commodities["Last_call"]

    db.session.commit()

    db.session.query(models.BankierCommodity).delete()
    db.session.commit()



    for i in range(len(commodities["Ticker"])):
        commodities_info = models.BankierCommodity(ticker= commodities['Ticker'][i],
                                                  name= commodities['Name'][i],
                                                  unit= commodities['Unit'][i],
                                                  price= float(commodities['Price'][i]),
                                                  change= commodities['Change'][i],
                                                   date= commodities['Date'][i])
        db.session.add(commodities_info)


    db.session.commit()


    db.session.query(models.BankierStockBond).delete()
    db.session.commit()



    for i in range(len(stocks["Ticker"])):
        stocks_info = models.BankierStockBond(ticker= stocks['Ticker'][i],
                                                   name= stocks['Name'][i],
                                                   price= float(stocks['Price'][i]),
                                                   change= stocks['Percentage change'][i],
                                                   date= stocks['Date'][i])
        db.session.add(stocks_info)

    for i in range(len(new_connect["Ticker"])):
        new_connect_info = models.BankierStockBond(ticker= new_connect['Ticker'][i],
                                              name= new_connect['Name'][i],
                                              price= float(new_connect['Price'][i]),
                                              change= new_connect['Percentage change'][i],
                                              date= new_connect['Date'][i])
        db.session.add(new_connect_info)

    for i in range(len(bonds["Ticker"])):
        bonds_info = models.BankierStockBond(ticker= bonds['Ticker'][i],
                                                   name= bonds['Name'][i],
                                                   price= float(bonds['Price'][i]),
                                                   change= bonds['Percentage change'][i],
                                                   date= bonds['Date'][i])
        db.session.add(bonds_info)


    db.session.commit()

def bankier_rest_check_or_not():

    now= datetime.now()
    last_call_b_date = models.LastCalls.query.filter_by(source= 'bankier_date').first()

    last_call_b_minutes = models.LastCalls.query.filter_by(source= 'bankier_minutes').first()

    if last_call_b_minutes:

        if now - (datetime.strptime(last_call_b_minutes.last_call, '%Y-%m-%d %H:%M')) > dt.timedelta(minutes = 30):
            try:
                bankier_info_to_db_rest()
            except:
                pass
    else:
        try:
            bankier_info_to_db_rest()
        except:
            pass







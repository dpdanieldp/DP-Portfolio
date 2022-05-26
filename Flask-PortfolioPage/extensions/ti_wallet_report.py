from datetime import datetime

import pandas as pd
from sqlalchemy import desc
from website import models


def generate_ti_wallet_rep(user):
    wallet = models.Wallet.query.filter_by(user_id=user.id).order_by(
        desc(models.Wallet.percentage_in_wallet)
    )

    # -----------lists to report:
    tickers_l = []
    names_l = []
    qty_l = []
    value_1_l = []
    value_l = []
    currency_l = []
    category_l = []
    date_l = []
    percentage_l = []

    for component in wallet:
        tickers_l.append(component.ticker)
        names_l.append(component.name)
        qty_l.append(component.amount)
        value_1_l.append(component.value_per_1)
        value_l.append(component.value)
        currency_l.append(component.value_currency)
        category_l.append(component.category)
        date_l.append(component.date)
        percentage_l.append(str(component.percentage_in_wallet) + "%")

    sum = 0.0
    for value in value_l:
        sum += value

    value_l.append(round(sum, 2))
    currency_l.append(wallet[0].value_currency)
    list_of_lists = [tickers_l, names_l, qty_l, category_l, date_l, percentage_l]
    for list in list_of_lists:
        list.append("")

    now = datetime.now()
    date_to_rep = now.strftime("%Y-%m-%d")
    date_rep = []
    date_rep.append(date_to_rep)
    for i in range(len(tickers_l) - 1):
        date_rep.append("")

    value_1_l.append("SUM:")

    dict_to_save = {
        "Ticker": tickers_l,
        "Name": names_l,
        "Category": category_l,
        "Quantity": qty_l,
        "Value per one": value_1_l,
        "Value": value_l,
        "Currency": currency_l,
        "Weight": percentage_l,
        "Date of data": date_l,
        "Date of report": date_rep,
    }

    df_to_save = pd.DataFrame.from_dict(dict_to_save)

    print(df_to_save)

    path_2pay = "./website/Reports/TI_rep/TI_wallet.xlsx"
    writer = pd.ExcelWriter(path_2pay, engine="xlsxwriter")

    user_first_name = user.first_name
    sheet_name = f"TI wallet- {user_first_name}"
    df_to_save.to_excel(writer, sheet_name=sheet_name, index=False)
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    cell_format1 = workbook.add_format({"bold": True, "border": 1})

    worksheet.set_column(first_col=0, last_col=2, width=15, cell_format=cell_format1)
    worksheet.set_column(first_col=3, last_col=3, width=10, cell_format=cell_format1)
    worksheet.set_column(first_col=4, last_col=5, width=15, cell_format=cell_format1)
    worksheet.set_column(first_col=6, last_col=7, width=10, cell_format=cell_format1)
    worksheet.set_column(first_col=8, last_col=9, width=16, cell_format=cell_format1)

    writer.save()

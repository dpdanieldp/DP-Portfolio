from website import db, models

from . import bankier_btfs, polygon_check_tickers


def get_cur_list(user):
    cur_names = models.BankierPLNCurrency.query.all()
    currencies = []

    for result in cur_names:
        currencies.append(result.currency)

    cur_with_pln = ["PLN"]
    cur_with_pln.extend(sorted(currencies))

    if len(user.components) == 0:

        return cur_with_pln

    else:
        default_currency = [user.components[0].value_currency]
        cur_with_pln.remove(default_currency[0])
        default_currency.extend(sorted(cur_with_pln))

        return default_currency


def check_user_currency(user):
    user_wallet = user.components

    if len(user_wallet) == 0:
        return "PLN"
    else:
        return user_wallet[0].value_currency


def check_wallet_components(user, currency):
    bankier_btfs.bankier_currencies_check_or_not()
    bankier_btfs.bankier_rest_check_or_not()

    user_wallet = user.components

    if len(user_wallet) == 0:
        pass
    else:
        polygon_tickers_list = []
        for component in user_wallet:
            if component.category == "Other":

                if component.value_currency != currency:

                    if currency == "PLN":
                        old_currency = component.value_currency
                        old_value = component.value
                        old_currency_data = models.BankierPLNCurrency.query.filter_by(
                            currency=old_currency
                        ).first()
                        old_currency_pln_rate = old_currency_data.rate
                        old_currency_pln_price = old_currency_data.pln_price

                        new_value = (
                            old_value / old_currency_pln_rate
                        ) * old_currency_pln_price

                        component.value = round(new_value, 2)
                        component.value_per_1 = round(new_value, 2)
                        component.value_currency = currency
                        db.session.commit()

                    else:
                        old_currency = component.value_currency
                        old_value = component.value

                        new_currency_data = models.BankierPLNCurrency.query.filter_by(
                            currency=currency
                        ).first()
                        new_currency_pln_rate = new_currency_data.rate
                        new_currency_pln_price = new_currency_data.pln_price

                        if old_currency == "PLN":
                            new_value = (
                                old_value * new_currency_pln_rate
                            ) / new_currency_pln_price
                        else:
                            old_currency_data = (
                                models.BankierPLNCurrency.query.filter_by(
                                    currency=old_currency
                                ).first()
                            )
                            old_currency_pln_rate = old_currency_data.rate
                            old_currency_pln_price = old_currency_data.pln_price
                            value_in_pln = (
                                old_value / old_currency_pln_rate
                            ) * old_currency_pln_price
                            new_value = (
                                value_in_pln * new_currency_pln_rate
                            ) / new_currency_pln_price

                        component.value = round(new_value, 2)
                        component.value_per_1 = round(new_value, 2)
                        component.value_currency = currency
                        db.session.commit()

            else:

                if component.category == "Polish stocks/bonds":

                    if component.value_currency != currency:
                        component.value_currency = currency

                        db.session.commit()

                    ticker_data = models.BankierStockBond.query.filter_by(
                        ticker=component.ticker
                    ).first()

                    component.name = ticker_data.name
                    component.date = ticker_data.date

                    db.session.commit()

                    if currency == "PLN":
                        component.value_per_1 = round(ticker_data.price, 2)
                        # db.session.commit()
                        component.value = round(
                            (component.value_per_1 * component.amount), 2
                        )
                        db.session.commit()
                    else:
                        new_currency_data = models.BankierPLNCurrency.query.filter_by(
                            currency=currency
                        ).first()
                        new_currency_pln_rate = new_currency_data.rate
                        new_currency_pln_price = new_currency_data.pln_price

                        new_currency_ticker_price = (
                            ticker_data.price * new_currency_pln_rate
                        ) / new_currency_pln_price

                        component.value_per_1 = round(new_currency_ticker_price, 2)
                        # db.session.commit()
                        component.value = round(
                            (component.value_per_1 * component.amount), 2
                        )
                        db.session.commit()

                if component.category == "Cash":
                    component.name = component.ticker

                    if component.value_currency != currency:
                        component.value_currency = currency

                        db.session.commit()

                    if component.ticker == "PLN" and currency == "PLN":
                        currency_data = models.BankierPLNCurrency.query.filter_by(
                            id=1
                        ).first()
                        component.value_per_1 = 1.0
                        component.value = component.amount
                        component.date = currency_data.date
                        db.session.commit()

                    if component.ticker == "PLN" and currency != "PLN":
                        new_currency_data = models.BankierPLNCurrency.query.filter_by(
                            currency=currency
                        ).first()

                        component.value_per_1 = round(
                            (new_currency_data.rate / new_currency_data.pln_price), 2
                        )

                        new_value = component.amount * component.value_per_1
                        db.session.commit()

                        component.value = round(new_value, 2)
                        component.date = new_currency_data.date

                        db.session.commit()

                    if component.ticker != "PLN" and currency == "PLN":
                        old_currency = component.ticker
                        old_currency_data = models.BankierPLNCurrency.query.filter_by(
                            currency=old_currency
                        ).first()
                        old_currency_pln_rate = old_currency_data.rate
                        old_currency_pln_price = old_currency_data.pln_price
                        value_in_pln = (
                            component.amount / old_currency_pln_rate
                        ) * old_currency_pln_price

                        component.value_per_1 = round(
                            (value_in_pln / component.amount), 2
                        )

                        component.value = round(
                            (component.value_per_1 * component.amount), 2
                        )

                        component.date = old_currency_data.date

                        db.session.commit()

                    if component.ticker != "PLN" and currency != "PLN":
                        new_currency_data = models.BankierPLNCurrency.query.filter_by(
                            currency=currency
                        ).first()
                        new_currency_pln_rate = new_currency_data.rate
                        new_currency_pln_price = new_currency_data.pln_price

                        old_currency = component.ticker
                        old_currency_data = models.BankierPLNCurrency.query.filter_by(
                            currency=old_currency
                        ).first()
                        old_currency_pln_rate = old_currency_data.rate
                        old_currency_pln_price = old_currency_data.pln_price
                        value_in_pln = (
                            component.amount / old_currency_pln_rate
                        ) * old_currency_pln_price
                        new_value = (
                            value_in_pln * new_currency_pln_rate
                        ) / new_currency_pln_price

                        component.value_per_1 = round((new_value / component.amount), 2)
                        component.value = round(
                            (component.value_per_1 * component.amount), 2
                        )
                        component.date = new_currency_data.date

                        db.session.commit()

                if component.category == "Commodities":

                    if component.value_currency != currency:
                        component.value_currency = currency

                        db.session.commit()

                    component.name = component.ticker
                    db.session.commit()

                    ticker_data = models.BankierCommodity.query.filter_by(
                        ticker=component.ticker
                    ).first()

                    usd_data = models.BankierPLNCurrency.query.filter_by(
                        currency="USD"
                    ).first()
                    usd_pln_rate = usd_data.rate
                    usd_pln_price = usd_data.pln_price

                    if currency == "PLN":

                        component.value_per_1 = round(
                            ((ticker_data.price / usd_pln_rate) * usd_pln_price), 2
                        )
                        component.value = round(
                            (component.value_per_1 * component.amount), 2
                        )
                        component.date = ticker_data.date
                        db.session.commit()

                    else:

                        new_currency_data = models.BankierPLNCurrency.query.filter_by(
                            currency=currency
                        ).first()
                        new_currency_pln_rate = new_currency_data.rate
                        new_currency_pln_price = new_currency_data.pln_price

                        value_per_1_in_pln = (
                            ticker_data.price / usd_pln_rate
                        ) * usd_pln_price

                        value_per_1_in_currency = (
                            value_per_1_in_pln * new_currency_pln_rate
                        ) / new_currency_pln_price

                        component.value_per_1 = round(value_per_1_in_currency, 2)
                        component.value = round(
                            (component.value_per_1 * component.amount), 2
                        )
                        component.date = ticker_data.date
                        db.session.commit()

                if component.category == "Gold/Silver bullion":

                    if component.value_currency != currency:
                        component.value_currency = currency

                        db.session.commit()

                    component.name = component.ticker
                    db.session.commit()

                    if "Gold" in component.ticker:
                        ticker = "GOLD"
                    else:
                        ticker = "SILVER"

                    ticker_data = models.BankierCommodity.query.filter_by(
                        ticker=ticker
                    ).first()

                    usd_data = models.BankierPLNCurrency.query.filter_by(
                        currency="USD"
                    ).first()
                    usd_pln_rate = usd_data.rate
                    usd_pln_price = usd_data.pln_price

                    if currency == "PLN":
                        if component.ticker == "Gold bullion":
                            qty = component.amount

                            value1 = (
                                (ticker_data.price / usd_pln_rate) * usd_pln_price
                            ) * 1.04
                            value = value1 * qty

                            component.value_per_1 = round(value1, 2)
                            component.value = round(value, 2)
                            component.date = ticker_data.date
                            db.session.commit()

                        if component.ticker == "Silver bullion":
                            value1 = (
                                (ticker_data.price / usd_pln_rate) * usd_pln_price
                            ) * (1.28)
                            value = value1 * component.amount

                            component.value_per_1 = round(value1, 2)
                            component.value = round(value, 2)
                            component.date = ticker_data.date
                            db.session.commit()

                    else:

                        new_currency_data = models.BankierPLNCurrency.query.filter_by(
                            currency=currency
                        ).first()
                        new_currency_pln_rate = new_currency_data.rate
                        new_currency_pln_price = new_currency_data.pln_price

                        value_per_1_in_pln = (
                            ticker_data.price / usd_pln_rate
                        ) * usd_pln_price

                        value_per_1_in_currency = (
                            value_per_1_in_pln * new_currency_pln_rate
                        ) / new_currency_pln_price

                        if component.ticker == "Gold bullion":
                            value1 = value_per_1_in_currency * (1.04)
                            value = value1 * component.amount

                            component.value_per_1 = round(value1, 2)
                            component.value = round(value, 2)

                            component.date = ticker_data.date
                            db.session.commit()

                        if component.ticker == "Silver bullion":
                            value1 = value_per_1_in_currency * (1.28)
                            value = value1 * component.amount

                            component.value_per_1 = round(value1, 2)
                            component.value = round(value, 2)

                            component.date = ticker_data.date
                            db.session.commit()

                if component.category in ["US stocks/ ETFs", "Crypto"]:
                    polygon_tickers_list.append(component.ticker)

        if len(polygon_tickers_list) > 0:

            polygon_ticker_value_dict = polygon_check_tickers.polygon_check_or_not(
                polygon_tickers_list
            )

            response_tickers_list = list(polygon_ticker_value_dict.keys())
            # response_value_list = list(polygon_ticker_value_dict.values())

            for component in user_wallet:
                if component.ticker in response_tickers_list:
                    if component.value_currency != currency:
                        component.value_currency = currency

                        db.session.commit()

                    if not component.name:
                        ticker_name = models.PolygonTicker.query.filter_by(
                            ticker=component.ticker
                        ).first()

                        component.name = ticker_name.name
                        db.session.commit()

                    usd_data = models.BankierPLNCurrency.query.filter_by(
                        currency="USD"
                    ).first()
                    usd_pln_rate = usd_data.rate
                    usd_pln_price = usd_data.pln_price

                    if currency == "PLN":

                        value_per_1_in_pln = (
                            polygon_ticker_value_dict[component.ticker][0]
                            / usd_pln_rate
                        ) * usd_pln_price
                        value_in_pln = value_per_1_in_pln * component.amount

                        component.value_per_1 = round(value_per_1_in_pln, 2)
                        component.value = round(value_in_pln, 2)
                        component.date = polygon_ticker_value_dict[component.ticker][1]
                        db.session.commit()

                    else:

                        new_currency_data = models.BankierPLNCurrency.query.filter_by(
                            currency=currency
                        ).first()
                        new_currency_pln_rate = new_currency_data.rate
                        new_currency_pln_price = new_currency_data.pln_price

                        value_per_1_in_pln = (
                            polygon_ticker_value_dict[component.ticker][0]
                            / usd_pln_rate
                        ) * usd_pln_price

                        value_per_1_in_currency = (
                            value_per_1_in_pln * new_currency_pln_rate
                        ) / new_currency_pln_price

                        component.value_per_1 = round(value_per_1_in_currency, 2)
                        component.value = round(
                            (value_per_1_in_currency * component.amount), 2
                        )
                        component.date = polygon_ticker_value_dict[component.ticker][1]
                        db.session.commit()


def check_wallet_sum_value(user):

    user_wallet = user.components
    current_wallet_value = 0.00

    if len(user_wallet) == 0:
        pass
    else:

        for component in user_wallet:
            current_wallet_value += component.value
        for component in user_wallet:
            component.percentage_in_wallet = round(
                ((component.value / current_wallet_value) * 100), 2
            )
            db.session.commit()

        user_wallet_value = models.WalletValue.query.filter_by(user_id=user.id).first()
        if not user_wallet_value:
            current_value = models.WalletValue(
                sum_value=round(current_wallet_value, 2), user_id=user.id
            )
            db.session.add(current_value)
        else:
            user_wallet_value.sum_value = round(current_wallet_value, 2)
    return round(current_wallet_value, 2)

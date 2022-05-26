from flask_login import UserMixin
from sqlalchemy.sql import func

from . import db, ma


class LastCalls(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(10))
    last_call = db.Column(db.String(30))


class PolygonCheckedTicker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(100))
    price = db.Column(db.Float())
    date_info = db.Column(db.String(100))
    date_check = db.Column(db.String(100))


class PolygonTicker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    date = db.Column(db.String(100))


class BankierPLNCurrency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(100))
    rate = db.Column(db.Integer())
    pln_price = db.Column(db.Float())
    change = db.Column(db.String(10))
    date = db.Column(db.String(100))


class BankierCommodity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(30))
    name = db.Column(db.String(30))
    unit = db.Column(db.String(30))
    price = db.Column(db.Float())
    change = db.Column(db.String(10))
    date = db.Column(db.String(30))


class BankierStockBond(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(20))
    name = db.Column(db.String(1000))
    price = db.Column(db.Float())
    change = db.Column(db.String(20))
    date = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class WalletValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sum_value = db.Column(db.Float())
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    value_per_1 = db.Column(db.Float())
    amount = db.Column(db.Float())
    value = db.Column(db.Float())
    value_currency = db.Column(db.String(100))
    percentage_in_wallet = db.Column(db.Float())
    category = db.Column(db.String(100))
    date = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    components = db.relationship("Wallet")


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000))
    author = db.Column(db.String(1000))
    publication_date = db.Column(db.Date())
    isbn = db.Column(db.String(30))
    page_count = db.Column(db.String(10))
    link_to_cover = db.Column(db.String(10000))
    publication_language = db.Column(db.String(200))


class TemporaryInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String())
    info = db.Column(db.String())


class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Book

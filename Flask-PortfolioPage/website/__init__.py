import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db = SQLAlchemy()
DB_NAME = os.getenv("DB_NAME")
ma = Marshmallow()

mail = Mail()


def create_app():

    application = Flask(__name__)
    application.config["FLASK_ENV"] = os.getenv("FLASK_ENV")
    application.config["SECRET_KEY"] = os.getenv("MY_SECRET")
    application.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQL_DB_URI")
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv("SQL_TRACK_MOD")
    application.config["JSON_AS_ASCII"] = os.getenv("JSON_AS_ASCII")

    application.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=10)
    application.config["SESSION_REFRESH_EACH_REQUEST"] = True
    # ---------------------

    application.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    application.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    application.config["MAIL_SERVER"] = "smtp.googlemail.com"
    application.config["MAIL_PORT"] = 465
    application.config["MAIL_USE_TLS"] = False
    application.config["MAIL_USE_SSL"] = True

    mail.init_app(application)

    db.init_app(application)
    ma.init_app(application)

    from .auth import auth
    from .views import views

    application.register_blueprint(views, url_prefix="/")
    application.register_blueprint(auth, url_prefix="/")

    from .models import (BankierCommodity, BankierPLNCurrency,
                         BankierStockBond, Book, BookSchema, LastCalls,
                         PolygonTicker, TemporaryInfo, User, Wallet)

    create_database(application)

    login_manager = LoginManager(application)
    login_manager.login_view = "auth.login"
    login_manager.init_app(application)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return application


def create_database(app):
    if not os.path.exists("website/" + DB_NAME):
        db.create_all(app=app)
